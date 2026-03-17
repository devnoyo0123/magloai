"""Port for speech recognition."""
from abc import ABC, abstractmethod
from typing import List, Tuple
from domain.models.segment import Segment


class SpeechRecognitionPort(ABC):
    """Port for converting audio to text with timestamps."""

    @abstractmethod
    def transcribe(self, audio_file) -> Tuple[str, object, List[Segment]]:
        """
        Transcribe audio file to text with segments.

        Args:
            audio_file: Audio file object

        Returns:
            Tuple of (full_text, info, segments)
        """
        pass
