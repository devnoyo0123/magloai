# YouTube 자막 요약기

YouTube 영상의 영어 자막을 추출하여 한국어로 요약해주는 Streamlit 앱입니다.

## 기능

- YouTube URL 입력으로 자동 자막 추출
- AI를 활용한 요약 및 한국어 번역
- 깔끔한 웹 인터페이스
- 저비용 운영 (Gemini 2.0 Flash 무료 모델 사용)

## 설치 방법

### 옵션 1: uv 사용 (추천 - 빠름)

```bash
cd magloai

# uv가 없다면 먼저 설치
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 Homebrew:
# brew install uv

# 가상환경 생성 및 패키지 설치 (한 번에!)
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

uv pip install -r requirements.txt
```

### 옵션 2: 기본 venv 사용

```bash
cd magloai

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 3. API 키 설정

1. [OpenRouter](https://openrouter.ai/keys)에서 무료 API 키 발급
2. `.env.example` 파일을 `.env`로 복사
3. `.env` 파일에 API 키 입력

```bash
cp .env.example .env
# .env 파일을 열어서 OPENROUTER_API_KEY 입력
```

## 사용 방법

### 1. 앱 실행

```bash
streamlit run app.py
```

### 2. 브라우저에서 사용

1. 자동으로 브라우저가 열립니다 (보통 http://localhost:8501)
2. YouTube 영상 URL 입력
3. "요약하기" 버튼 클릭
4. 결과 확인

## 지원 영상

- 영어 자막이 있는 YouTube 영상
- 자동 생성 자막 또는 수동 자막 모두 지원

## 기술 스택

- **Frontend**: Streamlit
- **자막 추출**: youtube-transcript-api
- **AI 요약/번역**: OpenRouter (Gemini 2.0 Flash)
- **언어**: Python 3.8+

## 예상 비용

- Gemini 2.0 Flash (무료 티어): $0/영상
- OpenRouter 무료 할당량 내에서 무료 사용 가능

## 문제 해결

### "자막을 찾을 수 없습니다"
- 해당 영상에 영어 자막이 없는 경우입니다
- 자막 설정이 활성화된 다른 영상을 시도해보세요

### "OPENROUTER_API_KEY가 설정되지 않았습니다"
- `.env` 파일이 있는지 확인
- API 키가 올바르게 입력되었는지 확인

### 처리 속도가 느림
- Gemini Flash는 무료 모델이라 가끔 느릴 수 있습니다
- 보통 30초~1분 정도 소요됩니다

---

## faster-whisper 모델 가이드 (음성 처리용)

### 모델 크기 및 성능

| 모델 | 크기 | 1분 음성 처리 | 10분 통화 처리 | 정확도 | 추천 |
|------|------|--------------|---------------|--------|------|
| **tiny** | ~75 MB | ~5-8초 | ~1분 | 낮음 | ❌ |
| **base** | ~140 MB | ~10-15초 | ~2-3분 | 보통 | ✅ 추천 |
| **small** | ~460 MB | ~20-30초 | ~3-5분 | 좋음 | ✅ 고품질 |
| **medium** | ~1.5 GB | ~40-60초 | ~7-10분 | 우수 | GPU 권장 |
| **large** | ~3 GB | ~60-90초 | ~10-15분 | 최고 | GPU 필수 |

**추천**:
- 일반 사용: **base** (빠르고 가벼움)
- 중요한 회의/인터뷰: **small** (더 정확함)

### 모델 저장 위치

#### macOS/Linux
```
~/.cache/huggingface/hub/
├── models--Systran--faster-whisper-base/    (~140MB)
├── models--Systran--faster-whisper-small/   (~460MB)
└── models--Systran--faster-whisper-medium/  (~1.5GB)
```

#### 실제 경로 (macOS 예시)
```
/Users/사용자명/.cache/huggingface/hub/
```

### 모델 확인 및 관리

#### 저장된 모델 확인
```bash
ls -lh ~/.cache/huggingface/hub/
```

#### 모델 삭제 (공간 확보)
```bash
# base 모델만 삭제
rm -rf ~/.cache/huggingface/hub/models--Systran--faster-whisper-base

# 전체 캐시 삭제
rm -rf ~/.cache/huggingface/hub/
```

### 모델 변경 방법

#### .env 파일에서 설정
```bash
# base 모델 사용 (기본값)
WHISPER_MODEL=base

# small 모델로 변경 (더 정확함)
WHISPER_MODEL=small

# medium 모델 (고품질, GPU 권장)
WHISPER_MODEL=medium
```

#### 첫 실행 시 자동 다운로드
```python
# 설정한 모델이 없으면 자동 다운로드
# ~/.cache/huggingface/hub/ 에 저장
```

### 용량 관리

#### 여러 모델 동시 설치 가능
```
base + small = ~600MB
base + small + medium = ~2GB
```

#### 권장사항
- **시작**: base 모델만 설치 (~140MB)
- **필요 시**: small 추가 다운로드
- **불필요 모델**: 위 명령어로 삭제

### 처리 시간 예상

#### 10분 통화 녹음
- **base**: 2-3분 처리 ✅
- **small**: 3-5분 처리 ✅
- **medium**: 7-10분 처리 ⚠️

#### 30분 회의 녹음
- **base**: 6-9분 처리 ✅
- **small**: 9-15분 처리 ✅
- **medium**: 20-30분 처리 ❌

**참고**: CPU 성능에 따라 다를 수 있음

---

## 라이선스

MIT License
