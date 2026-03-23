#!/usr/bin/env python3
"""Fix audio_file paths in existing summary JSON files."""
import json
from pathlib import Path


def fix_audio_paths(summaries_dir: Path = Path("summaries")):
    """Update audio_file paths in all summary JSON files."""

    fixed_count = 0
    skipped_count = 0
    audio_dir = summaries_dir / "audio_files"

    for json_file in summaries_dir.glob("*.json"):
        try:
            # Read JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Skip if already has audio_file or is YouTube
            if data.get('audio_file') or data.get('source_type') == 'youtube':
                skipped_count += 1
                continue

            # Construct expected audio filename
            source_id = data.get('source_id', '')
            timestamp_str = data.get('timestamp', '')

            if timestamp_str:
                # Parse timestamp to get formatted filename
                from datetime import datetime
                timestamp = datetime.fromisoformat(timestamp_str)
                base_filename = f"{source_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

                # Try different extensions
                audio_path = None
                for ext in ['.mp3', '.m4a', '.wav']:
                    candidate_path = audio_dir / f"{base_filename}{ext}"
                    if candidate_path.exists():
                        audio_path = candidate_path
                        break

                # Check if audio file exists
                if audio_path:
                    # Update JSON
                    data['audio_file'] = str(audio_path)

                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    print(f"✅ Fixed: {json_file.name} -> {audio_path.name}")
                    fixed_count += 1
                else:
                    print(f"⚠️  Audio not found for: {json_file.name}")
                    skipped_count += 1
            else:
                skipped_count += 1

        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            skipped_count += 1

    print(f"\n📊 Summary:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")


if __name__ == "__main__":
    fix_audio_paths()
