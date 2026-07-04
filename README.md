# Nolan CV Dashboard

`roboflow/supervision` 공식 예제를 설명형 갤러리로 보여주고, 직접 업로드한 영상도 분석할 수 있는 Streamlit 대시보드입니다.

현재 구성은 두 축입니다.

- 공식 예제 갤러리: tracking, heatmap, zone counting, traffic analysis, speed estimation, time in zone
- 직접 업로드 실험실: mp4 업로드 후 사람 추적 또는 군중 카운팅 실행

배포용 저장소에는 대용량 원본 결과 영상 대신 짧은 프리뷰 mp4만 포함합니다. 그래서 GitHub와 Streamlit Cloud에 바로 올리기 쉬운 구조입니다.

## Local Run

권장 환경:

- Windows
- Conda
- CUDA가 활성화된 PyTorch 환경
- 예시 환경: `timesfm-env`

실행:

```powershell
conda activate timesfm-env
python -m streamlit run app.py
```

브라우저에서 열리면 다음을 확인할 수 있습니다.

- 공식 `supervision` 예제별 설명과 프리뷰 영상
- 업로드한 영상 분석
- 결과 mp4와 CSV 다운로드

## Deployable Preview Assets

앱에서 사용하는 배포용 프리뷰 파일:

- `assets/examples/tracking_preview.mp4`
- `assets/examples/heatmap_preview.mp4`
- `assets/examples/zone_count_preview.mp4`
- `assets/examples/traffic_preview.mp4`
- `assets/examples/speed_preview.mp4`
- `assets/examples/time_checkout_preview.mp4`
- `assets/examples/time_traffic_preview.mp4`

로컬 작업용으로는 `vendor/supervision` 클론과 원본 결과 영상도 그대로 둘 수 있지만, Git 추적에서는 제외됩니다.

## Custom Upload Demo

업로드 분석은 `demo.py`를 사용합니다.

- `football`: 사람을 추적하고 이동 궤적을 표시
- `crowd`: 프레임별 사람 수와 최대 인원 수 집계

예시:

```powershell
python demo.py --source .\samples\8GBYQmuBH_s_clip.mp4 --mode football --model yolov8n.pt --device 0
```

출력:

- `outputs/<video_stem>_annotated.mp4`
- `outputs/<video_stem>_metrics.csv`

## Streamlit Cloud Deployment

`nolan_cv.streamlit.app` 같은 주소로 올릴 수 있게 저장소 구조를 맞춰뒀습니다. 다만 최종 배포 URL 생성은 GitHub 저장소와 Streamlit 계정 연결이 필요합니다.

배포 순서:

1. 이 폴더를 GitHub 저장소로 push
2. Streamlit Community Cloud에서 저장소 연결
3. 메인 파일로 `app.py` 선택
4. 앱 이름을 `nolan-cv` 같은 식으로 지정
5. Deploy 실행

참고:

- Streamlit Cloud는 배포가 매우 간단합니다. 공식 안내도 GitHub 로그인 후 저장소와 파일을 선택해 배포하는 흐름입니다. Source: https://streamlit.io/cloud
- `st.file_uploader` 기본 업로드 한도는 200MB이고 설정으로 조정할 수 있습니다. 이 프로젝트는 `.streamlit/config.toml`에 `maxUploadSize = 400`을 넣어두었습니다. Source: https://docs.streamlit.io/knowledge-base/deploy/increase-file-uploader-limit-streamlit-cloud
- Streamlit Community Cloud는 GPU 환경을 기대하는 용도보다는 예제 소개와 가벼운 CPU 데모에 더 적합합니다. 로컬 CUDA나 별도 GPU 서버와 조합하는 편이 현실적입니다.
- 이 프로젝트는 `.gitignore`로 `vendor/`, `samples/`, `outputs/`, 대형 weight 파일을 제외하도록 맞춰뒀습니다.

## Recommended Split

가장 현실적인 운영 방식은 아래처럼 나누는 것입니다.

- Streamlit Cloud: 공식 예제 설명, 결과 영상 쇼케이스, 가벼운 업로드 데모
- 로컬 GPU 또는 별도 서버: 긴 영상, 대량 처리, 실시간 추론

## Files

- `app.py`: 설명형 Streamlit 대시보드
- `demo.py`: 업로드 영상 분석 로직
- `.streamlit/config.toml`: 업로드 크기와 테마 설정
- `assets/examples`: 배포용 프리뷰 영상
- `vendor/supervision`: 로컬 참고용 공식 저장소 클론
