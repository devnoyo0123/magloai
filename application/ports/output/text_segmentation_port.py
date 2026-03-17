"""Port for text segmentation using LLM."""
from abc import ABC, abstractmethod
from typing import List


class TextSegmentationPort(ABC):
    """Port for segmenting text into paragraphs using LLM."""

    @abstractmethod
    def segment_text(self, text: str) -> List[str]:
        """
        Segment text into meaningful paragraphs.

        Args:
            text: Full transcript text

        Returns:
            List of paragraph texts in original order
        """
        pass
