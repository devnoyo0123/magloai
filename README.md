# 음성 인식 및 요약 서비스

YouTube 영상 자막 추출, 음성 파일 변환, AI 요약, 스크립트 기반 채팅 Q&A를 제공하는 Streamlit 앱입니다.

## 기능

### 📤 음성 파일 업로드
- 음성 파일(mp3, wav, m4a, ogg) 업로드 → 텍스트 변환(faster-whisper) → AI 요약

### 🎬 YouTube
- YouTube URL 입력 → 영어 자막 자동 추출 → 한국어 요약

### 📋 저장된 요약
- 처리 완료된 요약본 목록 조회 (요약, 스크립트, 메타데이터)

### 💬 채팅 Q&A
- 처리된 영상/음성의 스크립트를 기반으로 질문-답변
- 스크립트에 없는 내용은 추측하지 않고 정확한 인용으로 답변
- 대화 내역 유지 (초기화 가능)

## 비용

| 기능 | 모델 | 비용 |
|------|------|------|
| 음성→텍스트 | faster-whisper (로컬) | 무료 |
| 요약 | gpt-4o-mini (OpenRouter) | 건당 ~$0.001 |
| 채팅 Q&A | nvidia/nemotron (OpenRouter) | 무료 |

**거의 무료**로 사용 가능합니다. 요약만 건당 약 0.1원 수준입니다.

## 설치 방법

### 옵션 1: uv 사용 (추천 - 빠름)

```bash
cd magloai

# uv가 없다면 먼저 설치
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 패키지 설치
uv venv
source .venv/bin/activate  # macOS/Linux

uv pip install -r requirements.txt
```

### 옵션 2: 기본 venv 사용

```bash
cd magloai

python -m venv venv
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### API 키 설정

1. [OpenRouter](https://openrouter.ai/keys)에서 API 키 발급
2. `.env.example` 파일을 `.env`로 복사
3. `.env` 파일에 API 키 입력

```bash
cp .env.example .env
# .env 파일을 열어서 OPENROUTER_API_KEY 입력
```

## 사용 방법

```bash
streamlit run app.py
```

1. 브라우저가 자동으로 열립니다 (http://localhost:8501)
2. 상단 라디오 버튼으로 기능 선택
3. **YouTube**: URL 입력 → 처리 시작 → 요약/스크립트 확인
4. **채팅**: 요약본 선택 → 스크립트 기반으로 질문 → AI 답변

## 기술 스택

- **UI**: Streamlit
- **음성 인식**: faster-whisper (로컬 CPU)
- **자막 추출**: youtube-transcript-api
- **AI 요약**: OpenRouter (gpt-4o-mini)
- **AI 채팅**: OpenRouter (nvidia/nemotron 무료 모델)
- **언어**: Python 3.8+

## 설정 (.env)

```bash
OPENROUTER_API_KEY=sk-or-v1-...     # 필수
WHISPER_MODEL=small                  # tiny, base, small, medium, large
CHAT_MODEL_NAME=nvidia/nemotron-3-super-120b-a12b:free  # 채팅 모델
```

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
