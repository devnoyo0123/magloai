"""HTML audio player adapter."""
import base64
from pathlib import Path
from typing import List
from domain.models.segment import ParagraphSegment


class HTMLPlayerAdapter:
    """Adapter for rendering interactive HTML5 audio player."""

    def render(self, audio_path: Path, segments: List[ParagraphSegment]) -> str:
        """Render interactive audio player with clickable timestamps."""
        with open(audio_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()

        # Generate segment buttons
        segments_html = ""
        for i, seg in enumerate(segments):
            start_time = seg.start
            text = seg.text.strip()
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"
            segments_html += f'''
            <div class="segment" id="seg-{i}" onclick="seekTo({start_time}, {i})">
                <span class="timestamp">[{timestamp_str}]</span>
                <span class="text">{text[:100]}...</span>
            </div>
            '''

        html = f"""
        <div style="margin: 20px 0;">
            <audio id="audioPlayer" controls style="width: 100%; margin-bottom: 15px;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>

            <div id="segments" style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
                {segments_html}
            </div>
        </div>

        <style>
            .segment {{
                padding: 10px;
                margin: 5px 0;
                cursor: pointer;
                border-radius: 5px;
                transition: all 0.2s;
            }}
            .segment:hover {{
                background-color: #e3f2fd;
            }}
            .segment:hover .text {{
                color: #1a1a1a;
            }}
            .segment.active {{
                background-color: #bbdefb;
                font-weight: bold;
            }}
            .segment.active .text {{
                color: #000;
            }}
            .timestamp {{
                color: #64b5f6;
                font-weight: bold;
                margin-right: 10px;
            }}
            .segment.active .timestamp {{
                color: #1976d2;
            }}
            .text {{
                color: #e0e0e0;
            }}
        </style>

        <script>
            const audio = document.getElementById('audioPlayer');
            const segments = {[seg.start for seg in segments]};

            function seekTo(time, index) {{
                audio.currentTime = time;
                audio.play();
                updateActiveSegment(index);
            }}

            function updateActiveSegment(index) {{
                document.querySelectorAll('.segment').forEach(seg => seg.classList.remove('active'));
                const activeSegment = document.getElementById('seg-' + index);
                activeSegment.classList.add('active');
                activeSegment.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}

            audio.addEventListener('timeupdate', () => {{
                const currentTime = audio.currentTime;
                for (let i = segments.length - 1; i >= 0; i--) {{
                    if (currentTime >= segments[i]) {{
                        updateActiveSegment(i);
                        break;
                    }}
                }}
            }});
        </script>
        """
        return html
