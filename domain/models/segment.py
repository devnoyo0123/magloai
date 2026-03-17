"""Domain models for audio segments."""
from dataclasses import dataclass
from typing import List


@dataclass
class Segment:
    """Represents a single audio segment with timestamp."""
    start: float
    end: float
    text: str

    def to_dict(self) -> dict:
        return {
            'start': self.start,
            'end': self.end,
            'text': self.text
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Segment':
        return cls(
            start=data['start'],
            end=data['end'],
            text=data['text']
        )


@dataclass
class ParagraphSegment(Segment):
    """Represents a merged paragraph segment."""
    pass


def segments_to_dict_list(segments: List[Segment]) -> List[dict]:
    """Convert list of segments to list of dicts."""
    return [seg.to_dict() for seg in segments]


def segments_from_dict_list(data: List[dict]) -> List[Segment]:
    """Convert list of dicts to list of segments."""
    return [Segment.from_dict(item) for item in data]
