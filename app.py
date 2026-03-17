"""Main application entry point."""
import os
from pathlib import Path
from dotenv import load_dotenv

from adapters.output.whisper_adapter import WhisperAdapter
from adapters.output.openai_adapter import OpenAIAdapter
from adapters.output.filesystem_adapter import FileSystemAdapter
from adapters.output.html_player_adapter import HTMLPlayerAdapter
from adapters.output.youtube_adapter import YouTubeAdapter
from adapters.input.streamlit_adapter import StreamlitAdapter
from application.use_cases.process_audio_use_case import ProcessAudioUseCase
from application.use_cases.process_youtube_use_case import ProcessYoutubeUseCase
from domain.services.segment_merger import SegmentMerger

# Load environment variables
load_dotenv()

# Directories
SUMMARIES_DIR = Path("summaries")
AUDIO_FILES_DIR = SUMMARIES_DIR / "audio_files"

# Initialize adapters
whisper = WhisperAdapter(
    model_size=os.getenv("WHISPER_MODEL", "large-v3"),
    device="cpu"
)

openai_adapter = OpenAIAdapter(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4o-mini"
)

repository = FileSystemAdapter(
    summaries_dir=SUMMARIES_DIR,
    audio_dir=AUDIO_FILES_DIR
)

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

# Initialize and run UI
ui = StreamlitAdapter(
    process_audio_use_case=process_audio_use_case,
    process_youtube_use_case=process_youtube_use_case,
    repository=repository,
    html_player=html_player
)

ui.render_ui()
