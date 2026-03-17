"""Use case for processing YouTube videos."""
from pathlib import Path
from datetime import datetime
from typing import Tuple
from application.ports.output.summarization_port import SummarizationPort
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from adapters.output.youtube_adapter import YouTubeAdapter
from domain.models.summary import Summary


class ProcessYoutubeUseCase:
    """Use case for processing YouTube videos."""

    def __init__(
        self,
        youtube_adapter: YouTubeAdapter,
        summarization: SummarizationPort,
        repository: SummaryRepositoryPort
    ):
        self.youtube_adapter = youtube_adapter
        self.summarization = summarization
        self.repository = repository

    def execute(self, youtube_url: str) -> Tuple[Summary, Path]:
        """
        Process YouTube video: extract transcript, summarize, and save.

        Returns:
            Tuple of (Summary, json_path)
        """
        # 1. Extract video ID
        video_id = self.youtube_adapter.extract_video_id(youtube_url)

        # 2. Get transcript
        transcript = self.youtube_adapter.get_transcript(video_id)

        # 3. Summarize
        summary_text = self.summarization.summarize(transcript)

        # 4. Create domain model
        summary = Summary(
            source_id=video_id,
            source_url=youtube_url,
            source_type="youtube",
            summary_text=summary_text,
            transcript=transcript,
            segments=None,
            audio_file_path=None,
            timestamp=datetime.now(),
            model=None
        )

        # 5. Save to repository
        json_path, _ = self.repository.save(summary, audio_file=None)

        return summary, json_path
