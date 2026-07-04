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
MODE_ALIASES = {
    "football": "tracking",
    "tracking": "tracking",
    "crowd": "crowd",
    "zone_count": "zone_count",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Supervision + YOLO demo for tracking, crowd counting, or zone counting."
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the input video.",
    )
    parser.add_argument(
        "--mode",
        choices=tuple(MODE_ALIASES.keys()),
        default="tracking",
        help="tracking: trace people, crowd: count people, zone_count: count people inside the auto zone.",
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


def build_center_zone(width: int, height: int) -> np.ndarray:
    margin_x = int(width * 0.2)
    margin_y = int(height * 0.2)
    return np.array(
        [
            [margin_x, margin_y],
            [width - margin_x, margin_y],
            [width - margin_x, height - margin_y],
            [margin_x, height - margin_y],
        ],
        dtype=np.int32,
    )


def normalize_mode(mode: str) -> str:
    return MODE_ALIASES.get(mode, mode)


def process_video(
    source: Path,
    mode: str,
    model_name: str,
    output_dir: Path,
    device_arg: str | None = None,
    imgsz: int = 1280,
    conf: float = 0.25,
) -> dict[str, Any]:
    normalized_mode = normalize_mode(mode)
    device = resolve_device(device_arg)
    output_video_path, csv_path = ensure_paths(source, output_dir)
    writer, width, height, fps = open_writer(source, output_video_path)

    model = YOLO(model_name)

    ellipse_annotator = sv.EllipseAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_position=sv.Position.TOP_CENTER)
    trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=max(15, int(fps)))
    corner_annotator = sv.BoxCornerAnnotator(thickness=2)

    zone_polygon = build_center_zone(width, height)
    polygon_zone = sv.PolygonZone(
        polygon=zone_polygon,
        triggering_anchors=(sv.Position.CENTER,),
    )

    peak_people = 0
    peak_zone_people = 0

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["frame_index", "people_count", "in_zone_count", "tracked_ids"])

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

            tracker_ids: list[int] = []
            if detections.tracker_id is not None:
                tracker_ids = [int(track_id) for track_id in detections.tracker_id.tolist()]

            zone_mask = polygon_zone.trigger(detections) if len(detections) else np.array([], dtype=bool)
            detections_in_zone = detections[zone_mask] if len(detections) else detections
            in_zone_count = len(detections_in_zone)
            peak_zone_people = max(peak_zone_people, in_zone_count)

            annotated = frame
            labels: list[str] = []

            if normalized_mode == "tracking":
                labels = [f"person #{track_id}" for track_id in tracker_ids]
                if detections.tracker_id is not None and len(detections):
                    annotated = trace_annotator.annotate(scene=annotated, detections=detections)
                annotated = ellipse_annotator.annotate(scene=annotated, detections=detections)
                annotated = corner_annotator.annotate(scene=annotated, detections=detections)
                if labels:
                    annotated = label_annotator.annotate(
                        scene=annotated,
                        detections=detections,
                        labels=labels,
                    )
            elif normalized_mode == "crowd":
                annotated = corner_annotator.annotate(scene=annotated, detections=detections)
                annotated = label_annotator.annotate(
                    scene=annotated,
                    detections=detections,
                    labels=[f"person {idx + 1}" for idx in range(people_count)],
                )
            elif normalized_mode == "zone_count":
                annotated = sv.draw_polygon(
                    scene=annotated,
                    polygon=zone_polygon,
                    color=sv.Color.GREEN,
                )
                annotated = corner_annotator.annotate(scene=annotated, detections=detections)
                if len(detections_in_zone):
                    zone_labels = []
                    if detections_in_zone.tracker_id is not None:
                        zone_labels = [
                            f"in zone #{track_id}"
                            for track_id in detections_in_zone.tracker_id.tolist()
                        ]
                    else:
                        zone_labels = ["in zone"] * len(detections_in_zone)
                    annotated = label_annotator.annotate(
                        scene=annotated,
                        detections=detections_in_zone,
                        labels=zone_labels,
                    )

            overlay_lines = [
                f"mode: {normalized_mode}",
                f"device: {device}",
                f"people in frame: {people_count}",
                f"peak people: {peak_people}",
            ]
            if normalized_mode == "tracking" and tracker_ids:
                overlay_lines.append(f"active tracks: {len(tracker_ids)}")
            if normalized_mode == "zone_count":
                overlay_lines.append(f"people in zone: {in_zone_count}")
                overlay_lines.append(f"peak zone count: {peak_zone_people}")

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
            csv_writer.writerow(
                [frame_index, people_count, in_zone_count, "|".join(map(str, tracker_ids))]
            )

    writer.release()
    return {
        "output_video_path": output_video_path,
        "csv_path": csv_path,
        "peak_people": peak_people,
        "peak_zone_people": peak_zone_people,
        "device": device,
        "mode": normalized_mode,
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
    print(f"Peak zone count: {result['peak_zone_people']}")
    print(f"Device used: {result['device']}")


if __name__ == "__main__":
    run_demo(parse_args())
