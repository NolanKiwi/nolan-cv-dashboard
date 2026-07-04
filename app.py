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
        "summary": "같은 사람을 프레임 사이에서 계속 이어서 움직임을 따라가는 예제예요.",
        "use_case": "선수 동선 추적, 매장 방문자 이동 보기",
        "official_path_label": "vendor/supervision/examples/tracking",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/tracking",
        "preview_path": ASSETS_DIR / "tracking_preview.mp4",
        "notes": [
            "같은 사람을 하나의 ID로 이어서 볼 수 있어요.",
            "사람이 어디로 움직였는지 보여줄 때 좋아요.",
        ],
    },
    {
        "key": "heatmap_and_track",
        "title": "Heatmap And Track",
        "summary": "사람이 많이 지나간 곳을 색으로 누적해서 보여주는 예제예요.",
        "use_case": "사람이 몰리는 자리 찾기, 동선 시각화",
        "official_path_label": "vendor/supervision/examples/heatmap_and_track",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/heatmap_and_track",
        "preview_path": ASSETS_DIR / "heatmap_preview.mp4",
        "notes": [
            "어느 곳이 가장 바쁜지 눈으로 바로 볼 수 있어요.",
            "숫자보다 공간 흐름을 보여줄 때 더 재미있어요.",
        ],
    },
    {
        "key": "count_people_in_zone",
        "title": "Count People In Zone",
        "summary": "정해 둔 구역 안에 몇 명이 들어왔는지 세는 예제예요.",
        "use_case": "대기 줄 보기, 특정 구역 인원 수 세기",
        "official_path_label": "vendor/supervision/examples/count_people_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/count_people_in_zone",
        "preview_path": ASSETS_DIR / "zone_count_preview.mp4",
        "notes": [
            "선 안쪽 사람 수만 따로 셀 수 있어요.",
            "출입구나 줄 서는 곳에 잘 어울려요.",
        ],
    },
    {
        "key": "traffic_analysis",
        "title": "Traffic Analysis",
        "summary": "도로 위 차들이 어떻게 움직이는지 분석하는 예제예요.",
        "use_case": "교통 흐름 보기, 차량 움직임 추적",
        "official_path_label": "vendor/supervision/examples/traffic_analysis",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/traffic_analysis",
        "preview_path": ASSETS_DIR / "traffic_preview.mp4",
        "notes": [
            "차량도 사람처럼 찾아서 따라갈 수 있어요.",
            "도로 CCTV를 분석하는 느낌을 볼 수 있어요.",
        ],
    },
    {
        "key": "speed_estimation",
        "title": "Speed Estimation",
        "summary": "움직이는 차의 속도를 추정해 보는 예제예요.",
        "use_case": "차량 속도 보기, 움직임 비교",
        "official_path_label": "vendor/supervision/examples/speed_estimation",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/speed_estimation",
        "preview_path": ASSETS_DIR / "speed_preview.mp4",
        "notes": [
            "움직임을 통해 속도도 짐작할 수 있어요.",
            "정확한 속도계는 아니지만 원리를 이해하기 좋아요.",
        ],
    },
    {
        "key": "time_in_zone_checkout",
        "title": "Time In Zone - Checkout",
        "summary": "사람이 한 구역 안에 얼마나 오래 머무는지 보는 예제예요.",
        "use_case": "계산대 대기 시간 보기, 체류 시간 보기",
        "official_path_label": "vendor/supervision/examples/time_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/time_in_zone",
        "preview_path": ASSETS_DIR / "time_checkout_preview.mp4",
        "notes": [
            "사람이 오래 머무는 곳을 찾을 수 있어요.",
            "가게나 줄 서는 곳 분석에 잘 맞아요.",
        ],
    },
    {
        "key": "time_in_zone_traffic",
        "title": "Time In Zone - Traffic",
        "summary": "차량이나 물체가 특정 구역 안에 머문 시간을 보는 예제예요.",
        "use_case": "정체 구간 보기, 특정 구역 머문 시간 보기",
        "official_path_label": "vendor/supervision/examples/time_in_zone",
        "official_url": "https://github.com/roboflow/supervision/tree/develop/examples/time_in_zone",
        "preview_path": ASSETS_DIR / "time_traffic_preview.mp4",
        "notes": [
            "구역 안에 얼마나 오래 있었는지 알 수 있어요.",
            "교통이나 출입구 관찰에 재미있게 쓸 수 있어요.",
        ],
    },
]

UPLOAD_MODES = [
    {
        "key": "tracking",
        "title": "People Tracking",
        "summary": "같은 사람을 계속 따라가며 움직임을 표시해요.",
        "best_for": "축구 경기, 운동장, 사람이 걷는 영상",
    },
    {
        "key": "crowd",
        "title": "Crowd Counting",
        "summary": "화면에 몇 명이 보이는지 프레임마다 세어봐요.",
        "best_for": "관중석, 행사장, 매장 사람 수 보기",
    },
    {
        "key": "zone_count",
        "title": "Zone Count",
        "summary": "화면 중앙 구역 안 사람 수를 따로 세어봐요.",
        "best_for": "줄 서는 곳, 출입구, 특정 구역 보기",
    },
]


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Pen+Script&family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

        :root {
            --paper: #f6f0df;
            --paper-2: #fff9ec;
            --ink: #22313f;
            --accent: #0f766e;
            --accent-2: #f97316;
            --card: rgba(255, 252, 244, 0.92);
            --line: rgba(34, 49, 63, 0.12);
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(249, 115, 22, 0.14), transparent 25%),
                radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 28%),
                radial-gradient(circle at 20% 18%, rgba(255,255,255,0.45), transparent 18%),
                linear-gradient(180deg, var(--paper) 0%, #efe4c7 100%);
            color: var(--ink);
            font-family: "Noto Sans KR", sans-serif;
        }

        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: -0.02em;
        }

        h1 {
            font-family: "Nanum Pen Script", cursive;
            font-size: 4rem !important;
            line-height: 1.05;
            color: #124e66;
            margin-bottom: 0.2rem;
        }

        .stCaption, .stMarkdown, .stText, p, li, label {
            font-family: "Noto Sans KR", sans-serif !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #124e66 0%, #1f6f78 100%);
        }

        section[data-testid="stSidebar"] * {
            color: #f7f7f2 !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        .hero-note {
            background: rgba(255, 255, 255, 0.6);
            border: 1px dashed rgba(18, 78, 102, 0.28);
            border-radius: 24px;
            padding: 1rem 1.2rem;
            margin-top: 0.5rem;
        }

        .landing-hero {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(135deg, rgba(255,255,255,0.92), rgba(255,248,230,0.82)),
                linear-gradient(90deg, rgba(15,118,110,0.08), rgba(249,115,22,0.08));
            border: 1px solid rgba(18, 78, 102, 0.12);
            border-radius: 30px;
            padding: 1.4rem 1.4rem 1.2rem 1.4rem;
            box-shadow: 0 18px 40px rgba(34, 49, 63, 0.08);
            margin-bottom: 1rem;
        }

        .landing-hero:before {
            content: "";
            position: absolute;
            right: -50px;
            top: -50px;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(249,115,22,0.22), transparent 65%);
        }

        .landing-hero:after {
            content: "";
            position: absolute;
            left: -40px;
            bottom: -40px;
            width: 160px;
            height: 160px;
            background: radial-gradient(circle, rgba(15,118,110,0.16), transparent 65%);
        }

        .illustration-strip {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
            margin-top: 0.8rem;
        }

        .doodle-card {
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(34,49,63,0.1);
            border-radius: 22px;
            padding: 0.9rem;
            min-height: 150px;
            position: relative;
        }

        .doodle-icon {
            font-size: 2rem;
            line-height: 1;
            margin-bottom: 0.4rem;
        }

        .mini-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1rem 0.8rem 1rem;
            box-shadow: 0 12px 30px rgba(34, 49, 63, 0.06);
            min-height: 180px;
        }

        .section-banner {
            background: linear-gradient(90deg, rgba(15, 118, 110, 0.95), rgba(18, 78, 102, 0.95));
            color: white;
            border-radius: 22px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0 1rem 0;
        }

        div[data-testid="stExpander"] {
            border-radius: 20px !important;
            border: 1px solid var(--line) !important;
            background: rgba(255, 251, 242, 0.88) !important;
        }

        div[data-testid="stMetric"] {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.6rem 0.8rem;
        }

        .stButton button, .stDownloadButton button {
            border-radius: 999px !important;
            border: none !important;
            background: linear-gradient(90deg, var(--accent-2), #f59e0b) !important;
            color: white !important;
            font-weight: 800 !important;
            box-shadow: 0 10px 20px rgba(249, 115, 22, 0.2);
        }

        .stButton button:hover, .stDownloadButton button:hover {
            filter: brightness(1.04);
        }

        .stCodeBlock, code {
            border-radius: 14px !important;
        }

        @media (max-width: 900px) {
            .illustration-strip {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def render_hero() -> None:
    st.title("서윤이와 수호를 위한 CV 놀이터")
    st.caption("컴퓨터가 영상을 보고 무엇을 알아낼 수 있는지 쉽고 재미있게 소개하는 공간")
    st.markdown(
        """
        <div class="landing-hero">
            <h3 style="margin-top:0;">CV가 뭐야?</h3>
            <p style="font-size:1.02rem;">
                CV는 <strong>Computer Vision</strong>의 줄임말이에요.
                사람이 눈으로 보고 알아차리듯이, 컴퓨터도 사진이나 영상을 보고
                사람, 자동차, 움직임, 숫자 같은 것을 찾아볼 수 있어요.
            </p>
            <p style="font-size:1.02rem; margin-bottom:0.4rem;">
                이 사이트에서는 준비된 예제를 먼저 구경하고,
                그 다음에는 직접 영상을 올려서 컴퓨터가 어떻게 장면을 이해하는지 실험해볼 수 있어요.
            </p>
            <div class="illustration-strip">
                <div class="doodle-card">
                    <div class="doodle-icon">👀</div>
                    <strong>찾아보기</strong>
                    <p>영상 속 사람이나 자동차를 발견해요.</p>
                </div>
                <div class="doodle-card">
                    <div class="doodle-icon">🏃</div>
                    <strong>따라가기</strong>
                    <p>같은 사람이 어디로 움직였는지 이어서 봐요.</p>
                </div>
                <div class="doodle-card">
                    <div class="doodle-icon">📊</div>
                    <strong>세어보기</strong>
                    <p>몇 명이 보이는지, 구역 안에 몇 명인지 살펴봐요.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-note">
            <strong>이 사이트에서 할 수 있는 것</strong><br>
            1. 준비된 예제로 CV를 먼저 이해하기<br>
            2. 내 mp4 영상을 올려 직접 실험하기<br>
            3. 사람 수, 움직임, 구역 안 인원 수를 살펴보기
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_cards() -> None:
    st.markdown(
        '<div class="section-banner"><strong>컴퓨터가 할 수 있는 일</strong><br>사람처럼 본다고 하면, 무엇을 알아낼 수 있을까요?</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    cards = [
        ("사람 찾기", "영상 속에서 사람이나 자동차 같은 대상을 찾아요."),
        ("움직임 따라가기", "같은 사람이 어디로 움직였는지 이어서 볼 수 있어요."),
        ("숫자 세기", "사람이 몇 명 있는지 세어볼 수 있어요."),
        ("특정 구역 보기", "정한 구역 안에 몇 명이 들어오는지 따로 볼 수 있어요."),
    ]
    for col, (title, body) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="mini-card"><h3>{title}</h3><p>{body}</p></div>',
                unsafe_allow_html=True,
            )


def render_upload_ideas() -> None:
    st.markdown(
        '<div class="section-banner"><strong>어떤 영상을 올리면 좋을까?</strong><br>아래처럼 사람이 잘 보이는 영상이면 결과가 더 재미있게 나와요.</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    ideas = [
        ("축구나 운동장 영상", "선수들이 어디로 움직이는지 추적하기 좋아요."),
        ("행사장이나 관중 영상", "사람이 몇 명쯤 보이는지 세어보기 좋아요."),
        ("출입구나 줄 서는 영상", "특정 구역 안 인원 수를 보기 좋아요."),
    ]
    for col, (title, body) in zip(cols, ideas):
        with col:
            st.markdown(
                f'<div class="mini-card"><h3>{title}</h3><p>{body}</p></div>',
                unsafe_allow_html=True,
            )


def render_examples_intro() -> None:
    st.markdown(
        '<div class="section-banner"><strong>CV 구경하기</strong><br>먼저 준비된 예제를 보면서, 컴퓨터가 영상을 어떻게 이해하는지 천천히 살펴봐요.</div>',
        unsafe_allow_html=True,
    )


def render_example_gallery() -> None:
    render_examples_intro()
    for example in EXAMPLES:
        with st.expander(example["title"], expanded=example["key"] == "tracking"):
            col1, col2 = st.columns([1.05, 1.95])
            with col1:
                st.subheader(example["title"])
                st.write(example["summary"])
                st.caption(f"활용 예시: {example['use_case']}")
                for note in example["notes"]:
                    st.write(f"- {note}")
                st.code(example["official_path_label"], language="text")
                st.caption("이 예제는 공식 supervision 예제를 바탕으로 미리보기 영상으로 정리해둔 것입니다.")
                if example["preview_path"].exists():
                    st.success(
                        f"미리보기 준비됨: {example['preview_path'].name} "
                        f"({format_bytes(example['preview_path'].stat().st_size)})"
                    )
                else:
                    st.warning("미리보기 파일이 없습니다.")
            with col2:
                payload = read_bytes_if_exists(example["preview_path"])
                if payload is not None:
                    st.video(payload)
                else:
                    st.info("이 환경에는 미리보기 영상이 없습니다.")


def render_mode_cards() -> None:
    st.markdown(
        '<div class="section-banner"><strong>내 영상 실험 모드</strong><br>어떤 방식으로 영상을 볼지 먼저 골라보세요.</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(UPLOAD_MODES))
    for col, mode_info in zip(cols, UPLOAD_MODES):
        with col:
            st.markdown(
                (
                    f'<div class="mini-card"><h3>{mode_info["title"]}</h3>'
                    f'<p>{mode_info["summary"]}</p>'
                    f'<p><strong>추천 영상:</strong> {mode_info["best_for"]}</p></div>'
                ),
                unsafe_allow_html=True,
            )


def render_upload_page() -> None:
    st.markdown(
        '<div class="section-banner"><strong>내 영상 실험실</strong><br>이곳에서는 mp4나 mov 파일을 직접 올려서 실제로 테스트할 수 있어요.</div>',
        unsafe_allow_html=True,
    )
    render_mode_cards()

    with st.expander("설정은 무슨 뜻일까?", expanded=False):
        st.write("- `Mode`: 사람을 따라갈지, 숫자를 셀지, 구역 안만 볼지 고르는 옵션이에요.")
        st.write("- `Model`: 컴퓨터의 눈을 가볍게 쓸지, 조금 더 꼼꼼하게 쓸지 정해요.")
        st.write("- `Image Size`: 크게 보면 자세하지만 조금 느려질 수 있어요.")
        st.write("- `Confidence`: 컴퓨터가 얼마나 확실할 때 표시할지 정하는 기준이에요.")
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
        help="축구, 관중, 줄 서는 장면처럼 사람이 잘 보이는 영상을 추천해요.",
    )

    if uploaded_file is None:
        st.warning("업로드는 여기에서 합니다. 위 박스를 눌러 전체 mp4도 직접 올릴 수 있어요.")
        return

    st.subheader("올린 영상")
    st.video(uploaded_file.getvalue())

    if st.button("분석 시작하기", type="primary", use_container_width=True):
        with st.spinner("컴퓨터가 영상을 살펴보는 중이에요..."):
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
                label="CSV 다운로드",
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
    st.markdown(
        '<div class="section-banner"><strong>어른들을 위한 메모</strong><br>이 앱을 설명하거나 배포할 때 참고할 수 있는 간단한 안내예요.</div>',
        unsafe_allow_html=True,
    )
    st.write("- `CV 구경하기`는 설명형 예제 영역입니다.")
    st.write("- `내 영상 실험실`은 실제 업로드 테스트 영역입니다.")
    st.write("- Streamlit Community Cloud에서는 교육용 소개와 가벼운 테스트에 적합합니다.")
    st.write("- 긴 영상과 GPU 추론은 로컬 또는 별도 GPU 서버가 더 안정적입니다.")


st.set_page_config(page_title="서윤이와 수호를 위한 CV 놀이터", layout="wide")
inject_global_styles()

page = st.sidebar.radio(
    "어디로 가볼까?",
    options=["CV 구경하기", "내 영상 실험실", "어른들을 위한 메모"],
    index=0,
)

if page == "CV 구경하기":
    render_example_gallery()
    render_hero()
    render_feature_cards()
    render_upload_ideas()
elif page == "내 영상 실험실":
    render_hero()
    render_feature_cards()
    render_upload_ideas()
    render_upload_page()
else:
    render_hero()
    render_deploy_notes()
