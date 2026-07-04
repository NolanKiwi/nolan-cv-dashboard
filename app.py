from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from demo import process_video


ROOT = Path(__file__).parent
OUTPUTS_DIR = ROOT / "outputs"
ASSETS_DIR = ROOT / "assets" / "examples"

EXAMPLES = [
    {
        "key": "tracking",
        "title": "Tracking",
        "summary": "사람을 지속적으로 추적해서 같은 객체가 프레임 사이에서 어떻게 움직이는지 보여줍니다.",
        "use_case": "축구 선수 동선 추적, 매장 방문자 추적, 공장 작업자 이동 분석",
        "official_path_label": "vendor/supervision/examples/tracking",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/tracking",
        "preview_path": ASSETS_DIR / "tracking_preview.mp4",
        "notes": [
            "ByteTrack 기반으로 사람 ID를 유지합니다.",
            "같은 사람을 프레임마다 다른 박스로 끝내지 않고, 이동 궤적까지 이어서 볼 수 있습니다.",
        ],
    },
    {
        "key": "heatmap_and_track",
        "title": "Heatmap And Track",
        "summary": "사람이 자주 지나간 구역을 히트맵으로 누적해서 보여줍니다.",
        "use_case": "유동 인구가 몰리는 구역 파악, 동선 시각화, 공간 재배치 근거 확보",
        "official_path_label": "vendor/supervision/examples/heatmap_and_track",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/heatmap_and_track",
        "preview_path": ASSETS_DIR / "heatmap_preview.mp4",
        "notes": [
            "단순 카운트보다 공간 활용도를 훨씬 직관적으로 보여줍니다.",
            "매장, 경기장 출입구, 행사장 동선 분석에 잘 맞습니다.",
        ],
    },
    {
        "key": "count_people_in_zone",
        "title": "Count People In Zone",
        "summary": "지정한 구역 안에 현재 몇 명이 있는지 프레임 단위로 셉니다.",
        "use_case": "대기열 관리, 매장 혼잡도 측정, 특정 구역 점유율 모니터링",
        "official_path_label": "vendor/supervision/examples/count_people_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/count_people_in_zone",
        "preview_path": ASSETS_DIR / "zone_count_preview.mp4",
        "notes": [
            "폴리곤 존을 기준으로 사람 수를 집계합니다.",
            "카메라 각도가 고정된 환경에서 특히 빠르게 적용할 수 있습니다.",
        ],
    },
    {
        "key": "traffic_analysis",
        "title": "Traffic Analysis",
        "summary": "차량 흐름을 추적하고 도로 구간 분석에 필요한 시각화를 제공합니다.",
        "use_case": "차량 흐름 파악, 차선별 모니터링, 교통량 분석 PoC",
        "official_path_label": "vendor/supervision/examples/traffic_analysis",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/traffic_analysis",
        "preview_path": ASSETS_DIR / "traffic_preview.mp4",
        "notes": [
            "차량 검출과 추적을 조합한 교통 분석 예제입니다.",
            "도로 CCTV, 진출입 램프, 주차장 출입구 분석으로 확장하기 좋습니다.",
        ],
    },
    {
        "key": "speed_estimation",
        "title": "Speed Estimation",
        "summary": "차량 이동을 기반으로 속도 추정 시각화를 수행합니다.",
        "use_case": "과속 감지 PoC, 도로 구간 비교, 차량 흐름 분석",
        "official_path_label": "vendor/supervision/examples/speed_estimation",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/speed_estimation",
        "preview_path": ASSETS_DIR / "speed_preview.mp4",
        "notes": [
            "실서비스 수준 정확도를 내려면 카메라 보정과 거리 기준점이 더 필요합니다.",
            "그래도 PoC 단계에서 움직임 기반 속도 추정 흐름을 이해하기 좋습니다.",
        ],
    },
    {
        "key": "time_in_zone_checkout",
        "title": "Time In Zone - Checkout",
        "summary": "특정 구역 안에서 사람이 얼마나 오래 머무르는지 추적합니다.",
        "use_case": "계산대 대기시간, 체류시간 분석, 혼잡 구간 체류 패턴 측정",
        "official_path_label": "vendor/supervision/examples/time_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/time_in_zone",
        "preview_path": ASSETS_DIR / "time_checkout_preview.mp4",
        "notes": [
            "공식 예제는 화면 표시 중심이라, 저장형 래퍼를 추가해 결과 mp4도 만들었습니다.",
            "리테일 분석이나 대기열 모니터링에 바로 연결하기 좋은 패턴입니다.",
        ],
    },
    {
        "key": "time_in_zone_traffic",
        "title": "Time In Zone - Traffic",
        "summary": "차량이나 객체가 관심 구역 안에 머무는 시간을 추적합니다.",
        "use_case": "정체 구간 체류시간, 교차로 분석, 출입구 체류 패턴 확인",
        "official_path_label": "vendor/supervision/examples/time_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/time_in_zone",
        "preview_path": ASSETS_DIR / "time_traffic_preview.mp4",
        "notes": [
            "존 기반 dwell time 분석은 산업 현장과 교통 현장에서 모두 재사용성이 높습니다.",
            "나중에 알람 조건과 결합하면 운영 자동화로 이어질 수 있습니다.",
        ],
    },
]


def read_bytes_if_exists(path: Path) -> bytes | None:
    if path.exists() and path.is_file():
        return path.read_bytes()
    return None


def format_bytes(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def render_example_gallery() -> None:
    st.header("Official Example Gallery")
    st.write(
        "`roboflow/supervision` 공식 예제를 실제로 실행한 결과를 한곳에서 비교할 수 있게 묶었습니다."
    )

    for example in EXAMPLES:
        with st.expander(example["title"], expanded=example["key"] == "tracking"):
            col1, col2 = st.columns([1.2, 1.8])
            with col1:
                st.subheader(example["title"])
                st.write(example["summary"])
                st.caption(f"활용 예시: {example['use_case']}")
                for note in example["notes"]:
                    st.write(f"- {note}")
                st.code(example["official_path_label"], language="text")
                st.link_button("Open Official Example", example["official_url"])
                if example["preview_path"].exists():
                    st.success(
                        f"프리뷰 준비됨: {example['preview_path'].name} "
                        f"({format_bytes(example['preview_path'].stat().st_size)})"
                    )
                else:
                    st.warning("프리뷰 파일이 아직 없습니다.")
            with col2:
                payload = read_bytes_if_exists(example["preview_path"])
                if payload is not None:
                    st.video(payload)
                else:
                    st.info("이 환경에는 예제 프리뷰 영상이 아직 없습니다.")


def render_upload_lab() -> None:
    st.header("Upload Lab")
    st.write(
        "직접 mp4 영상을 올려서 사람 추적 또는 군중 카운팅을 실행할 수 있습니다. "
        "로컬 GPU 환경에서는 빠르게 돌고, Streamlit Cloud에서는 CPU 기준으로 더 느리게 동작할 수 있습니다."
    )

    with st.sidebar:
        st.header("Inference Settings")
        mode = st.selectbox(
            "Mode",
            options=["football", "crowd"],
            format_func=lambda value: (
                "Football Tracking" if value == "football" else "Crowd Counting"
            ),
        )
        model_name = st.selectbox(
            "Model",
            options=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"],
            index=0,
        )
        imgsz = st.slider("Image Size", min_value=640, max_value=1920, value=1280, step=64)
        conf = st.slider("Confidence", min_value=0.05, max_value=0.9, value=0.25, step=0.05)
        device = st.text_input(
            "Device Override",
            value="",
            help="로컬 GPU에서는 0, CPU 강제는 cpu. 비워두면 자동 선택합니다.",
        )

    uploaded_file = st.file_uploader(
        "Upload an MP4 or MOV file",
        type=["mp4", "mov", "m4v", "avi"],
        help="축구 중계, 행사장, 매장, 교통 영상처럼 사람이 보이는 영상을 권장합니다.",
    )

    if uploaded_file is None:
        st.info("샘플 영상을 먼저 둘러본 뒤, 직접 영상을 올려 테스트해보세요.")
        return

    st.video(uploaded_file.getvalue())

    if st.button("Run Analysis", type="primary"):
        with st.spinner("Running detection and tracking..."):
            with tempfile.TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                input_path = temp_dir / uploaded_file.name
                input_path.write_bytes(uploaded_file.getbuffer())

                result = process_video(
                    source=input_path,
                    mode=mode,
                    model_name=model_name,
                    output_dir=OUTPUTS_DIR,
                    device_arg=device.strip() or None,
                    imgsz=imgsz,
                    conf=conf,
                )

        st.success("Analysis complete")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peak People Count", int(result["peak_people"]))
        with col2:
            st.metric("Mode", result["mode"])
        with col3:
            st.metric("Device", str(result["device"]))

        csv_path = Path(result["csv_path"])
        output_video_path = Path(result["output_video_path"])

        st.subheader("Annotated Video")
        st.video(output_video_path.read_bytes())

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.download_button(
                label="Download CSV",
                data=csv_path.read_bytes(),
                file_name=csv_path.name,
                mime="text/csv",
            )
        with action_col2:
            st.download_button(
                label="Download Annotated Video",
                data=output_video_path.read_bytes(),
                file_name=output_video_path.name,
                mime="video/mp4",
            )

        df = pd.read_csv(csv_path)
        if not df.empty and "people_count" in df.columns:
            st.subheader("People Count Over Time")
            chart_df = df[["frame_index", "people_count"]].set_index("frame_index")
            st.line_chart(chart_df)
            st.dataframe(df.head(20), use_container_width=True)


def render_overview() -> None:
    st.title("Nolan CV Dashboard")
    st.caption("Supervision official examples + custom video analysis demo")

    st.write(
        "이 대시보드는 `roboflow/supervision` 공식 예제가 실제로 어떤 문제를 푸는지 보여주고, "
        "같은 환경에서 직접 업로드한 영상도 테스트할 수 있게 만든 설명형 데모입니다."
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Official Examples", len(EXAMPLES))
    with metric_col2:
        st.metric("Custom Demo Modes", 2)
    with metric_col3:
        st.metric("Saved Local Outputs", len(list(OUTPUTS_DIR.glob("*"))) if OUTPUTS_DIR.exists() else 0)

    st.subheader("What You Can Show")
    st.write("- 객체 추적: 같은 사람이나 차량을 프레임 간 연결")
    st.write("- 존 카운팅: 특정 구역 안 인원 수 집계")
    st.write("- 체류시간: 구역 안에 얼마나 오래 머무는지 분석")
    st.write("- 히트맵: 사람들이 몰리는 위치 시각화")
    st.write("- 속도 추정: 이동량을 기반으로 속도 분석 PoC")

    st.subheader("Deployment Fit")
    st.write(
        "이 앱은 로컬 Windows + CUDA 환경에서는 GPU를 활용할 수 있고, "
        "Streamlit Community Cloud에 올리면 공식 예제 갤러리와 가벼운 업로드 데모 중심으로 운영하는 구성이 적합합니다."
    )


def render_deploy_notes() -> None:
    st.header("Deploy Notes")
    st.write("`nolan_cv.streamlit.app` 같은 주소로 올릴 수 있게 구조를 맞춰둘 수 있습니다.")
    st.write("- 실제 배포는 GitHub 저장소와 Streamlit Community Cloud 계정 연결이 필요합니다.")
    st.write("- Community Cloud는 배포 자체는 간단하지만 GPU가 없는 환경을 전제로 보는 편이 안전합니다.")
    st.write("- 큰 영상 업로드가 많다면 Streamlit Cloud보다는 GPU 서버 + Streamlit 또는 FastAPI 조합이 더 안정적입니다.")
    st.write("- 현재 앱은 로컬에서는 GPU 추론, 클라우드에서는 CPU 데모용 흐름으로 사용하기 좋게 구성했습니다.")


st.set_page_config(page_title="Nolan CV Dashboard", layout="wide")

render_overview()

tab1, tab2, tab3 = st.tabs(["Official Examples", "Upload Lab", "Deploy Notes"])

with tab1:
    render_example_gallery()

with tab2:
    render_upload_lab()

with tab3:
    render_deploy_notes()
