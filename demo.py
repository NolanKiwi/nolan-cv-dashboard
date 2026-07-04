from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import supervision as sv
import torch
from ultralytics import YOLO


PERSON_CLASS_ID = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Supervision + YOLO demo for football tracking or crowd counting."
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the input video.",
    )
    parser.add_argument(
        "--mode",
        choices=("football", "crowd"),
        default="football",
        help="football: track players, crowd: count people per frame.",
    )
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="Ultralytics model name or local weights path.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Override device, e.g. 0, cpu. Defaults to GPU if CUDA is available.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=1280,
        help="Inference image size. Lower this if speed matters more than accuracy.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for annotated video and CSV outputs.",
    )
    return parser.parse_args()


def resolve_device(device_arg: str | None) -> str | int:
    if device_arg is not None:
        return int(device_arg) if device_arg.isdigit() else device_arg
    return 0 if torch.cuda.is_available() else "cpu"


def ensure_paths(source: Path, output_dir: Path) -> tuple[Path, Path]:
    if not source.exists():
        raise FileNotFoundError(f"Input video not found: {source}")
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    video_path = output_dir / f"{stem}_annotated.mp4"
    csv_path = output_dir / f"{stem}_metrics.csv"
    return video_path, csv_path


def open_writer(source: Path, destination: Path) -> tuple[cv2.VideoWriter, int, int, float]:
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {source}")

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    capture.release()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(destination), fourcc, fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video: {destination}")
    return writer, width, height, fps


def filter_people(detections: sv.Detections) -> sv.Detections:
    if detections.class_id is None:
        return detections
    return detections[detections.class_id == PERSON_CLASS_ID]


def attach_tracker_ids(detections: sv.Detections, result: Any) -> sv.Detections:
    if detections.tracker_id is not None:
        return detections
    if getattr(result, "boxes", None) is None or result.boxes.id is None:
        return detections
    detections.tracker_id = np.asarray(result.boxes.id.cpu().numpy(), dtype=int)
    return detections


def process_video(
    source: Path,
    mode: str,
    model_name: str,
    output_dir: Path,
    device_arg: str | None = None,
    imgsz: int = 1280,
    conf: float = 0.25,
) -> dict[str, Any]:
    device = resolve_device(device_arg)
    output_video_path, csv_path = ensure_paths(source, output_dir)
    writer, _, _, fps = open_writer(source, output_video_path)

    model = YOLO(model_name)

    ellipse_annotator = sv.EllipseAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_position=sv.Position.TOP_CENTER)
    trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=max(15, int(fps)))
    corner_annotator = sv.BoxCornerAnnotator(thickness=2)

    peak_people = 0

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["frame_index", "people_count", "tracked_ids"])

        results = model.track(
            source=str(source),
            stream=True,
            persist=True,
            classes=[PERSON_CLASS_ID],
            conf=conf,
            imgsz=imgsz,
            tracker="bytetrack.yaml",
            device=device,
            verbose=False,
        )

        for frame_index, result in enumerate(results):
            frame = result.orig_img.copy()
            detections = sv.Detections.from_ultralytics(result)
            detections = filter_people(detections)
            detections = attach_tracker_ids(detections, result)

            people_count = len(detections)
            peak_people = max(peak_people, people_count)

            tracker_ids = []
            if detections.tracker_id is not None:
                tracker_ids = [int(track_id) for track_id in detections.tracker_id.tolist()]

            labels = []
            if mode == "football":
                labels = [f"player #{track_id}" for track_id in tracker_ids]

            annotated = frame
            if mode == "football":
                if detections.tracker_id is not None:
                    annotated = trace_annotator.annotate(scene=annotated, detections=detections)
                annotated = ellipse_annotator.annotate(scene=annotated, detections=detections)
                annotated = corner_annotator.annotate(scene=annotated, detections=detections)
                if labels:
                    annotated = label_annotator.annotate(
                        scene=annotated,
                        detections=detections,
                        labels=labels,
                    )
            else:
                annotated = corner_annotator.annotate(scene=annotated, detections=detections)
                annotated = label_annotator.annotate(
                    scene=annotated,
                    detections=detections,
                    labels=[f"person {idx + 1}" for idx in range(people_count)],
                )

            overlay_lines = [
                f"mode: {mode}",
                f"device: {device}",
                f"people in frame: {people_count}",
                f"peak count: {peak_people}",
            ]
            if mode == "football" and tracker_ids:
                overlay_lines.append(f"active tracks: {len(tracker_ids)}")

            y = 30
            for line in overlay_lines:
                cv2.putText(
                    annotated,
                    line,
                    (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                y += 32

            writer.write(annotated)
            csv_writer.writerow([frame_index, people_count, "|".join(map(str, tracker_ids))])

    writer.release()
    return {
        "output_video_path": output_video_path,
        "csv_path": csv_path,
        "peak_people": peak_people,
        "device": device,
        "mode": mode,
        "model": model_name,
    }


def run_demo(args: argparse.Namespace) -> None:
    result = process_video(
        source=args.source,
        mode=args.mode,
        model_name=args.model,
        output_dir=args.output_dir,
        device_arg=args.device,
        imgsz=args.imgsz,
        conf=args.conf,
    )
    print(f"Finished. Annotated video: {result['output_video_path']}")
    print(f"Metrics CSV: {result['csv_path']}")
    print(f"Peak people count: {result['peak_people']}")
    print(f"Device used: {result['device']}")


if __name__ == "__main__":
    run_demo(parse_args())
