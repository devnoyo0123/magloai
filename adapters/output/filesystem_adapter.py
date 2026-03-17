"""File system adapter for summary persistence."""
import json
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from domain.models.summary import Summary


class FileSystemAdapter(SummaryRepositoryPort):
    """Adapter for file system storage."""

    def __init__(self, summaries_dir: Path, audio_dir: Path):
        self.summaries_dir = Path(summaries_dir)
        self.audio_dir = Path(audio_dir)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        summary: Summary,
        audio_file: Optional[object] = None
    ) -> Tuple[Path, Optional[Path]]:
        """Save summary and optional audio file."""
        # Save JSON
        json_filename = f"{summary.source_id}_{summary.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.summaries_dir / json_filename

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, ensure_ascii=False, indent=2)

        # Save audio file if provided
        audio_path = None
        if audio_file is not None:
            audio_filename = f"{summary.source_id}_{summary.timestamp.strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = self.audio_dir / audio_filename
            shutil.copy(audio_file, audio_path)

        return json_path, audio_path

    def load_all(self) -> List[Summary]:
        """Load all saved summaries."""
        summaries = []
        for json_file in sorted(self.summaries_dir.glob("*.json"), reverse=True):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries.append(Summary.from_dict(data))
            except Exception:
                continue
        return summaries
