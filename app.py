"""Main application entry point."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

from adapters.output.whisper_adapter import WhisperAdapter
from adapters.output.openai_adapter import OpenAIAdapter
from adapters.output.chat_adapter import ChatAdapter
from adapters.output.filesystem_adapter import FileSystemAdapter
from adapters.output.html_player_adapter import HTMLPlayerAdapter
from adapters.output.youtube_adapter import YouTubeAdapter
from adapters.input.streamlit_adapter import StreamlitAdapter
from application.use_cases.process_audio_use_case import ProcessAudioUseCase
from application.use_cases.process_youtube_use_case import ProcessYoutubeUseCase
from application.use_cases.chat_use_case import ChatUseCase
from domain.services.segment_merger import SegmentMerger

# Load environment variables
load_dotenv()

# Directories
SUMMARIES_DIR = Path("summaries")
AUDIO_FILES_DIR = SUMMARIES_DIR / "audio_files"


@st.cache_resource
def get_whisper_adapter() -> WhisperAdapter:
    return WhisperAdapter(
        model_size=os.getenv("WHISPER_MODEL", "large-v3"),
        device="cpu"
    )


@st.cache_resource
def get_openai_adapter() -> OpenAIAdapter:
    return OpenAIAdapter(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        model="openai/gpt-4o-mini"
    )


@st.cache_resource
def get_filesystem_adapter() -> FileSystemAdapter:
    return FileSystemAdapter(
        summaries_dir=SUMMARIES_DIR,
        audio_dir=AUDIO_FILES_DIR
    )


@st.cache_resource
def get_chat_adapter() -> ChatAdapter:
    return ChatAdapter(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv("CHAT_MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
    )


# Initialize adapters
whisper = get_whisper_adapter()
openai_adapter = get_openai_adapter()
repository = get_filesystem_adapter()
chat_adapter = get_chat_adapter()

html_player = HTMLPlayerAdapter()
youtube = YouTubeAdapter()

# Initialize use cases
process_audio_use_case = ProcessAudioUseCase(
    speech_recognition=whisper,
    summarization=openai_adapter,
    text_segmentation=openai_adapter,
    repository=repository,
    segment_merger=SegmentMerger()
)

process_youtube_use_case = ProcessYoutubeUseCase(
    youtube_adapter=youtube,
    summarization=openai_adapter,
    repository=repository
)

chat_use_case = ChatUseCase(
    chat_port=chat_adapter,
    repository=repository
)

# Initialize and run UI
ui = StreamlitAdapter(
    process_audio_use_case=process_audio_use_case,
    process_youtube_use_case=process_youtube_use_case,
    chat_use_case=chat_use_case,
    repository=repository,
    html_player=html_player
)

try:
    ui.render_ui()
except Exception as e:
    logging.getLogger(__name__).error(f"UI render failed: {e}", exc_info=True)
    st.error(f"렌더링 오류: {e}")
    import traceback
    st.code(traceback.format_exc())
