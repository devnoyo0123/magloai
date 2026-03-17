"""Port for text summarization."""
from abc import ABC, abstractmethod


class SummarizationPort(ABC):
    """Port for summarizing and translating text."""

    @abstractmethod
    def summarize(self, text: str) -> str:
        """
        Summarize text in Korean.

        Args:
            text: Input text to summarize

        Returns:
            Summary in Korean
        """
        pass
