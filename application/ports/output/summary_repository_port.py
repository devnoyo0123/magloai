"""Port for summary persistence."""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from pathlib import Path
from domain.models.summary import Summary


class SummaryRepositoryPort(ABC):
    """Port for saving and loading summaries."""

    @abstractmethod
    def save(
        self,
        summary: Summary,
        audio_file: Optional[object] = None
    ) -> Tuple[Path, Optional[Path]]:
        """
        Save summary and optional audio file.

        Args:
            summary: Summary domain model
            audio_file: Optional audio file to save

        Returns:
            Tuple of (json_path, audio_path)
        """
        pass

    @abstractmethod
    def load_all(self) -> List[Summary]:
        """Load all saved summaries."""
        pass
