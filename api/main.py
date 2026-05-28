import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from adapters.output.whisper_adapter import WhisperAdapter
from adapters.output.openai_adapter import OpenAIAdapter
from adapters.output.chat_adapter import ChatAdapter
from adapters.output.filesystem_adapter import FileSystemAdapter
from adapters.output.youtube_adapter import YouTubeAdapter
from application.use_cases.process_audio_use_case import ProcessAudioUseCase
from application.use_cases.process_youtube_use_case import ProcessYoutubeUseCase
from application.use_cases.chat_use_case import ChatUseCase
from domain.services.segment_merger import SegmentMerger

from api.routers import summaries, youtube, audio, chat

SUMMARIES_DIR = Path("summaries")
AUDIO_DIR = SUMMARIES_DIR / "audio_files"

whisper = WhisperAdapter(
    model_size=os.getenv("WHISPER_MODEL", "small"),
    device="cpu"
)
openai_adapter = OpenAIAdapter(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4o-mini"
)
repository = FileSystemAdapter(
    summaries_dir=SUMMARIES_DIR,
    audio_dir=AUDIO_DIR
)
chat_adapter = ChatAdapter(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model=os.getenv("CHAT_MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
)

youtube_adapter = YouTubeAdapter()

process_audio_use_case = ProcessAudioUseCase(
    speech_recognition=whisper,
    summarization=openai_adapter,
    text_segmentation=openai_adapter,
    repository=repository,
    segment_merger=SegmentMerger()
)

process_youtube_use_case = ProcessYoutubeUseCase(
    youtube_adapter=youtube_adapter,
    summarization=openai_adapter,
    repository=repository
)

chat_use_case = ChatUseCase(
    chat_port=chat_adapter,
    repository=repository
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="MagloAI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summaries.router, prefix="/api", tags=["summaries"])
app.include_router(youtube.router, prefix="/api", tags=["youtube"])
app.include_router(audio.router, prefix="/api", tags=["audio"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

if AUDIO_DIR.exists():
    app.mount("/api/static/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio-files")
