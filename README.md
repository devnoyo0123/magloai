# 음성 인식 및 요약 서비스

YouTube 영상 자막 추출, 음성 파일 변환, AI 요약, 스크립트 기반 채팅 Q&A를 제공하는 웹 서비스입니다.

**Next.js(프론트엔드) + FastAPI(백엔드)** 아키텍처로 구현되었습니다.

## 기능

### 📤 음성 파일 업로드
- 음성 파일(mp3, wav, m4a, ogg) 업로드 → 텍스트 변환(faster-whisper) → AI 요약

### 🎬 YouTube
- YouTube URL 입력 → 영어 자막 자동 추출 → 한국어 요약

### 📋 저장된 요약
- 처리 완료된 요약본 목록 조회 (요약, 스크립트, 메타데이터)
- 요약본 삭제 기능

### 💬 채팅 Q&A
- 처리된 영상/음성의 스크립트를 기반으로 질문-답변
- 스크립트에 없는 내용은 추측하지 않고 정확한 인용으로 답변
- 대화 내역 유지 (초기화 가능)

## 비용

| 기능 | 모델 | 비용 |
|------|------|------|
| 음성→텍스트 | faster-whisper (로컬) | 무료 |
| 요약 | gpt-4o-mini (OpenRouter) | 건당 ~$0.001 |
| 채팅 Q&A | gpt-4o-mini (OpenRouter) | 건당 ~$0.001 |

**거의 무료**로 사용 가능합니다. 요약/채팅 건당 약 0.1원 수준입니다.

## 프로젝트 구조

```
magloai/
├── api/                    # FastAPI 백엔드
│   ├── main.py             # 앱 진입점
│   └── routers/            # API 라우터
│       ├── audio.py        # 음성 처리
│       ├── youtube.py      # YouTube 처리
│       ├── summaries.py    # 요약 목록/상세
│       └── chat.py         # 채팅 Q&A
├── web/                    # Next.js 프론트엔드
│   ├── app/                # 페이지 컴포넌트
│   ├── components/         # UI 컴포넌트
│   └── lib/                # 유틸리티
├── domain/                 # 도메인 로직 (Ports & Adapters)
├── application/            # 애플리케이션 계층
├── adapters/               # 인프라스트럭처 어댑터
└── summaries/             # 저장된 요약 파일
```

**아키텍처:** Hexagonal (Ports & Adapters)
- 도메인 로직은 외부 의존성 없이 순수 Python
- FastAPI/Next.js는 어댑터로 분리

## 설치 방법

### 1. 백엔드 (FastAPI)

```bash
# Python 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 패키지 설치
pip install -r requirements.txt
```

### 2. 프론트엔드 (Next.js)

```bash
cd web

# 의존성 설치
npm install
```

### 3. API 키 설정

1. [OpenRouter](https://openrouter.ai/keys)에서 API 키 발급
2. `.env` 파일 생성 후 API 키 입력

```bash
OPENROUTER_API_KEY=sk-or-v1-...
WHISPER_MODEL=small
CHAT_MODEL_NAME=openai/gpt-4o-mini
```

## 사용 방법

### 1. 백엔드 서버 시작 (포트 8000)

```bash
cd /Users/colosseum_nohys/Documents/my/playground/magloai
source .venv/bin/activate
uvicorn api.main:app --reload
```

### 2. 프론트엔드 서버 시작 (포트 3000)

```bash
cd web
npm run dev
```

### 3. 브라우저 접속

http://localhost:3000

## 기술 스택

**백엔드:**
- FastAPI - Python 웹 프레임워크
- faster-whisper - 음성 인식 (로컬 CPU)
- youtube-transcript-api - 자막 추출
- OpenRouter - AI 모델 라우팅

**프론트엔드:**
- Next.js 16 - React 프레임워크
- TypeScript - 타입 안전성
- Tailwind CSS - 스타일링
- shadcn/ui - UI 컴포넌트

**아키텍처:**
- Ports & Adapters (Hexagonal)
- 의존성 주입
- 클린 아키텍처 원칙

## 설정 (.env)

```bash
# 필수
OPENROUTER_API_KEY=sk-or-v1-...          # OpenRouter API 키

# 선택 (기본값 있음)
WHISPER_MODEL=small                       # 음성 인식 모델
CHAT_MODEL_NAME=openai/gpt-4o-mini       # 채팅 모델
```

## faster-whisper 모델 가이드

### 모델 크기 및 성능

| 모델 | 크기 | 1분 음성 처리 | 10분 통화 처리 | 정확도 | 추천 |
|------|------|--------------|---------------|--------|------|
| **tiny** | ~75 MB | ~5-8초 | ~1분 | 낮음 | ❌ |
| **base** | ~140 MB | ~10-15초 | ~2-3분 | 보통 | ✅ 추천 |
| **small** | ~460 MB | ~20-30초 | ~3-5분 | 좋음 | ✅ 고품질 |
| **medium** | ~1.5 GB | ~40-60초 | ~7-10분 | 우수 | GPU 권장 |
| **large** | ~3 GB | ~60-90초 | ~10-15분 | 최고 | GPU 필수 |

### 모델 저장 위치

```bash
~/.cache/huggingface/hub/
├── models--Systran--faster-whisper-base/
├── models--Systran--faster-whisper-small/
└── models--Systran--faster-whisper-medium/
```

## 개발 참고사항

### 백엔드 개발

```bash
# FastAPI 자동 리로드 모드로 실행
uvicorn api.main:app --reload

# 특정 포트로 실행
uvicorn api.main:app --port 8000
```

### 프론트엔드 개발

```bash
cd web
npm run dev     # 개발 서버 (포트 3000)
npm run build   # 프로덕션 빌드
npm run start   # 프로덕션 서버
npm run lint    # ESLint 검사
```

### API 문서

백엔드 실행 후 http://localhost:8000/docs 접속

## 라이선스

MIT License
