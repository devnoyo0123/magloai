"""Use case for processing audio files."""
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from application.ports.output.speech_recognition_port import SpeechRecognitionPort
from application.ports.output.summarization_port import SummarizationPort
from application.ports.output.text_segmentation_port import TextSegmentationPort
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from domain.models.summary import Summary
from domain.services.segment_merger import SegmentMerger


class ProcessAudioUseCase:
    """Use case for processing audio files end-to-end."""

    def __init__(
        self,
        speech_recognition: SpeechRecognitionPort,
        summarization: SummarizationPort,
        text_segmentation: TextSegmentationPort,
        repository: SummaryRepositoryPort,
        segment_merger: SegmentMerger
    ):
        self.speech_recognition = speech_recognition
        self.summarization = summarization
        self.text_segmentation = text_segmentation
        self.repository = repository
        self.segment_merger = segment_merger

    def execute(
        self,
        audio_file_path: str,
        source_id: str,
        source_url: str = "",
        source_type: str = "audio"
    ) -> Tuple[Summary, Path, Optional[Path]]:
        """
        Process audio file: transcribe, segment, summarize, and save.

        Returns:
            Tuple of (Summary, json_path, audio_path)
        """
        # 1. Transcribe audio
        full_text, info, segments = self.speech_recognition.transcribe(audio_file_path)

        # 2. Segment text into paragraphs
        paragraphs = self.text_segmentation.segment_text(full_text)

        # 3. Merge segments with timestamps
        paragraph_segments = self.segment_merger.merge_into_paragraphs(segments, paragraphs)

        # 4. Summarize
        summary_text = self.summarization.summarize(full_text)

        # 5. Create domain model
        summary = Summary(
            source_id=source_id,
            source_url=source_url,
            source_type=source_type,
            summary_text=summary_text,
            transcript=full_text,
            segments=paragraph_segments,
            audio_file_path=None,  # Will be set after save
            timestamp=datetime.now(),
            model=str(info.all_language_probs) if hasattr(info, 'all_language_probs') else None
        )

        # 6. Save to repository
        json_path, audio_path = self.repository.save(summary, audio_file_path)

        # Update audio path in summary
        if audio_path:
            summary.audio_file_path = str(audio_path)

        return summary, json_path, audio_path
