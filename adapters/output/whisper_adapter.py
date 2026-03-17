"""Whisper speech recognition adapter."""
from typing import List, Tuple
from faster_whisper import WhisperModel
from application.ports.output.speech_recognition_port import SpeechRecognitionPort
from domain.models.segment import Segment


class WhisperAdapter(SpeechRecognitionPort):
    """Adapter for faster-whisper speech recognition."""

    def __init__(self, model_size: str = "large-v3", device: str = "cpu"):
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, audio_file) -> Tuple[str, object, List[Segment]]:
        """Transcribe audio file using Whisper."""
        segments_raw, info = self.model.transcribe(audio_file, beam_size=5)

        segments = []
        full_text_parts = []

        for seg in segments_raw:
            segment = Segment(
                start=seg.start,
                end=seg.end,
                text=seg.text
            )
            segments.append(segment)
            full_text_parts.append(seg.text)

        full_text = ' '.join(full_text_parts)
        return full_text, info, segments
