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
        "summary": "같은 사람을 프레임 사이에서 계속 연결해서 이동 궤적을 보여줍니다.",
        "use_case": "선수 동선 추적, 매장 방문자 추적, 작업자 이동 분석",
        "official_path_label": "vendor/supervision/examples/tracking",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/tracking",
        "preview_path": ASSETS_DIR / "tracking_preview.mp4",
        "notes": [
            "같은 사람을 ID로 이어서 볼 수 있습니다.",
            "움직임 패턴이나 동선을 보여주는 데 적합합니다.",
        ],
    },
    {
        "key": "heatmap_and_track",
        "title": "Heatmap And Track",
        "summary": "사람이 자주 지나간 구역을 히트맵처럼 누적해서 시각화합니다.",
        "use_case": "유동 인구 집중 구역 분석, 공간 재배치 근거 확보",
        "official_path_label": "vendor/supervision/examples/heatmap_and_track",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/heatmap_and_track",
        "preview_path": ASSETS_DIR / "heatmap_preview.mp4",
        "notes": [
            "사람이 몰리는 위치를 직관적으로 보여줍니다.",
            "카운트보다 공간 활용 분석에 더 적합합니다.",
        ],
    },
    {
        "key": "count_people_in_zone",
        "title": "Count People In Zone",
        "summary": "지정된 구역 안에 현재 몇 명이 있는지 집계합니다.",
        "use_case": "대기열 관리, 혼잡도 측정, 특정 구역 점유 분석",
        "official_path_label": "vendor/supervision/examples/count_people_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/count_people_in_zone",
        "preview_path": ASSETS_DIR / "zone_count_preview.mp4",
        "notes": [
            "폴리곤 존 안쪽 인원 수를 셉니다.",
            "고정 카메라 환경에서 빠르게 적용하기 좋습니다.",
        ],
    },
    {
        "key": "traffic_analysis",
        "title": "Traffic Analysis",
        "summary": "차량 흐름을 추적하고 도로 구간 분석에 필요한 시각화를 보여줍니다.",
        "use_case": "교통 흐름 분석, 출입구 차량 모니터링",
        "official_path_label": "vendor/supervision/examples/traffic_analysis",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/traffic_analysis",
        "preview_path": ASSETS_DIR / "traffic_preview.mp4",
        "notes": [
            "교통 CCTV PoC에 자주 쓰이는 패턴입니다.",
            "차량 검출과 추적 흐름을 한 번에 볼 수 있습니다.",
        ],
    },
    {
        "key": "speed_estimation",
        "title": "Speed Estimation",
        "summary": "이동량을 바탕으로 차량 속도 추정 시각화를 제공합니다.",
        "use_case": "과속 감지 PoC, 도로 구간 비교",
        "official_path_label": "vendor/supervision/examples/speed_estimation",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/speed_estimation",
        "preview_path": ASSETS_DIR / "speed_preview.mp4",
        "notes": [
            "실서비스 전에는 카메라 보정이 더 필요합니다.",
            "그래도 속도 분석 흐름을 설명하기에는 충분합니다.",
        ],
    },
    {
        "key": "time_in_zone_checkout",
        "title": "Time In Zone - Checkout",
        "summary": "특정 구역 안에 사람이 얼마나 오래 머무는지 측정합니다.",
        "use_case": "계산대 대기시간, 체류시간 분석",
        "official_path_label": "vendor/supervision/examples/time_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/time_in_zone",
        "preview_path": ASSETS_DIR / "time_checkout_preview.mp4",
        "notes": [
            "리테일 대기열 분석에 잘 맞습니다.",
            "단순 카운트보다 운영 지표에 가깝습니다.",
        ],
    },
    {
        "key": "time_in_zone_traffic",
        "title": "Time In Zone - Traffic",
        "summary": "차량이나 객체가 관심 구역 안에 머무는 시간을 분석합니다.",
        "use_case": "정체 구간 체류시간, 출입구 체류 패턴 분석",
        "official_path_label": "vendor/supervision/examples/time_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/time_in_zone",
        "preview_path": ASSETS_DIR / "time_traffic_preview.mp4",
        "notes": [
            "교통과 산업 현장 모두에 응용하기 좋습니다.",
            "나중에 알람 조건과 결합하기 편한 유형입니다.",
        ],
    },
]

UPLOAD_MODES = [
    {
        "key": "tracking",
        "title": "People Tracking",
        "summary": "같은 사람을 계속 추적하며 이동 궤적을 표시합니다.",
        "best_for": "축구 선수 움직임, 행사장 방문자 동선",
    },
    {
        "key": "crowd",
        "title": "Crowd Counting",
        "summary": "프레임마다 사람이 몇 명 보이는지 집계합니다.",
        "best_for": "관중 수 추정, 행사장 혼잡도 파악",
    },
    {
        "key": "zone_count",
        "title": "Zone Count",
        "summary": "화면 중앙 존 안에 들어온 사람 수를 따로 셉니다.",
        "best_for": "대기 구역, 출입구, 특정 관심 구역 분석",
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


def mode_label(mode_key: str) -> str:
    mapping = {
        "tracking": "People Tracking",
        "crowd": "Crowd Counting",
        "zone_count": "Zone Count",
    }
    return mapping.get(mode_key, mode_key)


def render_kids_intro() -> None:
    st.title("서윤이와 수호를 위한 CV 놀이터")
    st.caption("컴퓨터가 영상을 보고 무엇을 알아낼 수 있는지 쉽고 재미있게 보여주는 데모")

    hero_col1, hero_col2 = st.columns([1.4, 1.1])
    with hero_col1:
        st.subheader("CV가 뭐야?")
        st.write(
            "CV는 `Computer Vision`의 줄임말이에요. "
            "사람이 눈으로 보고 알아차리듯이, 컴퓨터도 사진이나 영상을 보고 "
            "`사람이 어디 있는지`, `몇 명 있는지`, `어느 쪽으로 움직이는지` "
            "같은 것을 찾아보는 기술이에요."
        )
        st.write(
            "이 사이트에서는 축구 영상, 사람 많은 영상, 줄 서 있는 영상 같은 것을 올려서 "
            "컴퓨터가 어떻게 장면을 이해하는지 직접 볼 수 있어요."
        )
    with hero_col2:
        st.info(
            "이 사이트는 두 부분으로 나뉘어요.\n"
            "- `CV 구경하기`: 준비된 예제를 보는 곳\n"
            "- `내 영상 실험실`: 직접 mp4를 올려 보는 곳"
        )

    st.subheader("컴퓨터가 할 수 있는 일")
    feature_cols = st.columns(4)
    cards = [
        ("사람 찾기", "영상 속에서 사람이나 자동차 같은 대상을 찾아요."),
        ("움직임 따라가기", "같은 사람이 어디로 움직였는지 이어서 봐요."),
        ("숫자 세기", "화면에 몇 명이 있는지 세어볼 수 있어요."),
        ("특정 구역 보기", "정해 둔 구역 안에 몇 명이 들어왔는지 볼 수 있어요."),
    ]
    for col, (title, body) in zip(feature_cols, cards):
        with col:
            st.markdown(f"**{title}**")
            st.write(body)


def render_upload_examples_for_kids() -> None:
    st.subheader("어떤 영상을 올리면 재미있을까?")
    st.write("아래 같은 영상을 올리면 결과가 잘 보이고, CV가 하는 일을 이해하기 쉬워요.")
    idea_cols = st.columns(3)
    ideas = [
        (
            "축구나 운동장 영상",
            "선수들이 어디로 움직이는지 추적해볼 수 있어요.",
        ),
        (
            "행사장이나 관중 영상",
            "사람이 몇 명쯤 보이는지 세어볼 수 있어요.",
        ),
        (
            "출입구나 줄 서 있는 영상",
            "특정 구역 안에 몇 명이 들어오는지 볼 수 있어요.",
        ),
    ]
    for col, (title, body) in zip(idea_cols, ideas):
        with col:
            st.markdown(f"**{title}**")
            st.write(body)


def render_header() -> None:
    render_kids_intro()
    render_upload_examples_for_kids()


def render_examples_intro() -> None:
    st.header("CV 구경하기")
    st.info(
        "이곳은 준비된 예제를 구경하는 곳이에요. "
        "여기서는 이미 만들어 둔 결과를 보면서 "
        "`컴퓨터가 영상을 어떻게 이해하는지`를 배울 수 있어요."
    )


def render_example_gallery() -> None:
    render_examples_intro()
    for example in EXAMPLES:
        with st.expander(example["title"], expanded=example["key"] == "tracking"):
            col1, col2 = st.columns([1.1, 1.9])
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
                        f"Preview ready: {example['preview_path'].name} "
                        f"({format_bytes(example['preview_path'].stat().st_size)})"
                    )
                else:
                    st.warning("Preview file is missing.")
            with col2:
                payload = read_bytes_if_exists(example["preview_path"])
                if payload is not None:
                    st.video(payload)
                else:
                    st.info("Preview video is not available in this environment.")


def render_mode_cards() -> None:
    st.subheader("내 영상으로 해볼 수 있는 실험")
    cols = st.columns(len(UPLOAD_MODES))
    for col, mode_info in zip(cols, UPLOAD_MODES):
        with col:
            st.markdown(f"**{mode_info['title']}**")
            st.write(mode_info["summary"])
            st.caption(f"추천 영상: {mode_info['best_for']}")


def render_upload_page() -> None:
    st.header("내 영상 실험실")
    st.success(
        "여기는 진짜로 영상을 올려서 실험해보는 곳이에요. "
        "mp4나 mov를 올리고, 어떤 방식으로 분석할지 고른 뒤 실행하면 됩니다."
    )
    render_mode_cards()

    with st.expander("What Do These Settings Mean?", expanded=False):
        st.write("- `Mode`: 사람을 따라갈지, 숫자를 셀지, 특정 구역만 볼지 고르는 버튼이에요.")
        st.write("- `Model`: 컴퓨터의 눈을 얼마나 가볍게 또는 꼼꼼하게 쓸지 정해요.")
        st.write("- `Image Size`: 크게 보면 더 자세하지만 조금 느려질 수 있어요.")
        st.write("- `Confidence`: 컴퓨터가 얼마나 확실할 때만 표시할지 정하는 기준이에요.")
        st.write("- `Device Override`: GPU나 CPU 중 어떤 힘을 쓸지 정하는 옵션이에요.")

    with st.sidebar:
        st.header("실험 설정")
        mode = st.selectbox(
            "어떤 실험을 해볼까?",
            options=[mode_info["key"] for mode_info in UPLOAD_MODES],
            format_func=mode_label,
        )
        model_name = st.selectbox(
            "컴퓨터 눈 모델",
            options=["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"],
            index=0,
        )
        imgsz = st.slider("얼마나 크게 볼까?", min_value=640, max_value=1920, value=1280, step=64)
        conf = st.slider("얼마나 확실해야 표시할까?", min_value=0.05, max_value=0.9, value=0.25, step=0.05)
        device = st.text_input(
            "장치 설정",
            value="",
            help="비워두면 자동 선택합니다. 로컬 GPU는 0, CPU 강제는 cpu 입니다.",
        )

    uploaded_file = st.file_uploader(
        "여기에 MP4 또는 MOV 영상을 올려보세요",
        type=["mp4", "mov", "m4v", "avi"],
        help="축구, 관중, 줄 서 있는 장면처럼 사람이 잘 보이는 영상을 추천해요.",
    )

    if uploaded_file is None:
        st.warning("업로드는 여기에서 합니다. 위 박스를 눌러 전체 mp4도 직접 올릴 수 있어요.")
        return

    st.subheader("올린 영상")
    st.video(uploaded_file.getvalue())

    if st.button("Run Analysis", type="primary", use_container_width=True):
        with st.spinner("Running video analysis..."):
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

        st.success("분석이 끝났어요")

        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("실험 종류", mode_label(result["mode"]))
        with metric_cols[1]:
            st.metric("가장 많이 보인 사람 수", int(result["peak_people"]))
        with metric_cols[2]:
            st.metric("구역 안 최대 인원", int(result["peak_zone_people"]))
        with metric_cols[3]:
            st.metric("사용한 장치", str(result["device"]))

        csv_path = Path(result["csv_path"])
        output_video_path = Path(result["output_video_path"])

        st.subheader("컴퓨터가 표시한 결과 영상")
        st.video(output_video_path.read_bytes())

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.download_button(
                label="Download CSV",
                data=csv_path.read_bytes(),
                file_name=csv_path.name,
                mime="text/csv",
                use_container_width=True,
            )
        with action_col2:
            st.download_button(
                label="결과 영상 다운로드",
                data=output_video_path.read_bytes(),
                file_name=output_video_path.name,
                mime="video/mp4",
                use_container_width=True,
            )

        df = pd.read_csv(csv_path)
        if not df.empty:
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.subheader("시간에 따라 사람 수가 어떻게 바뀌었을까?")
                st.line_chart(df[["frame_index", "people_count"]].set_index("frame_index"))
            with chart_col2:
                st.subheader("구역 안 사람 수는 어떻게 바뀌었을까?")
                st.line_chart(df[["frame_index", "in_zone_count"]].set_index("frame_index"))
            st.dataframe(df.head(30), use_container_width=True)


def render_deploy_notes() -> None:
    st.header("어른들을 위한 메모")
    st.write("- `CV 구경하기`는 설명형 예제 영역입니다.")
    st.write("- `내 영상 실험실`은 실제 업로드 테스트 영역입니다.")
    st.write("- Streamlit Community Cloud에서는 교육용 소개와 가벼운 테스트에 적합합니다.")
    st.write("- 긴 영상과 GPU 추론은 로컬 또는 별도 GPU 서버가 더 안정적입니다.")


st.set_page_config(page_title="Nolan CV Dashboard", layout="wide")

render_header()

page = st.sidebar.radio(
    "어디로 가볼까?",
    options=["내 영상 실험실", "CV 구경하기", "어른들을 위한 메모"],
    index=0,
)

if page == "내 영상 실험실":
    render_upload_page()
elif page == "CV 구경하기":
    render_example_gallery()
else:
    render_deploy_notes()
