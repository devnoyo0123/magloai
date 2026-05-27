"""File system adapter for summary persistence."""
import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from domain.models.summary import Summary

logger = logging.getLogger(__name__)


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
        # Save audio file first if provided
        audio_path = None
        if audio_file is not None:
            audio_filename = f"{summary.source_id}_{summary.timestamp.strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = self.audio_dir / audio_filename
            shutil.copy(audio_file, audio_path)
            # Update summary with audio path before saving JSON
            summary.audio_file_path = str(audio_path)

        # Save JSON with complete data
        json_filename = f"{summary.source_id}_{summary.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.summaries_dir / json_filename

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary.to_dict(), f, ensure_ascii=False, indent=2)

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

    def delete(self, summary: Summary) -> None:
        deleted = False

        if summary.timestamp:
            ts_str = summary.timestamp.strftime('%Y%m%d_%H%M%S')
            pattern = f"*_{ts_str}.json" if summary.source_id else "*.json"
            matches = list(self.summaries_dir.glob(pattern))
            logger.info(f"Delete: source_id={summary.source_id}, ts={ts_str}, pattern={pattern}, matches={len(matches)}")

            for match in matches:
                try:
                    data = json.loads(match.read_text(encoding='utf-8'))
                    file_ts = data.get('timestamp', '')
                    file_sid = data.get('source_id', '')
                    if ts_str in file_ts and (not summary.source_id or file_sid == summary.source_id):
                        match.unlink()
                        logger.info(f"Deleted JSON: {match.name}")
                        deleted = True
                        break
                except Exception as e:
                    logger.warning(f"Failed to read {match.name}: {e}")

            if not deleted:
                logger.warning(f"No JSON found for source_id={summary.source_id}, ts={ts_str}")

        if summary.audio_file_path:
            audio_path = Path(summary.audio_file_path)
            if audio_path.exists():
                audio_path.unlink()
                logger.info(f"Deleted audio: {audio_path.name}")
