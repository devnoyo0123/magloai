"""Domain models for summaries."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from .segment import Segment


@dataclass
class Summary:
    """Represents a video/audio summary with metadata."""
    source_id: str
    source_url: str
    source_type: str  # 'youtube' or 'audio'
    summary_text: str
    transcript: Optional[str] = None
    segments: Optional[List[Segment]] = None
    audio_file_path: Optional[str] = None
    timestamp: Optional[datetime] = None
    model: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'source_id': self.source_id,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'summary': self.summary_text,
            'transcript': self.transcript,
            'segments': [seg.to_dict() for seg in self.segments] if self.segments else None,
            'audio_file': self.audio_file_path,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'model': self.model
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Summary':
        from .segment import segments_from_dict_list

        return cls(
            source_id=data.get('source_id', ''),
            source_url=data.get('source_url', ''),
            source_type=data.get('source_type', 'youtube'),
            summary_text=data.get('summary', ''),
            transcript=data.get('transcript'),
            segments=segments_from_dict_list(data['segments']) if data.get('segments') else None,
            audio_file_path=data.get('audio_file'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            model=data.get('model')
        )
