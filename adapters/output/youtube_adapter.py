"""YouTube transcript adapter."""
import re
import json
import urllib.request
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class YouTubeAdapter:
    """Adapter for YouTube transcript extraction."""

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError("유효한 YouTube URL이 아닙니다.")

    def get_transcript(self, video_id: str) -> str:
        """Get transcript from YouTube video."""
        try:
            api = YouTubeTranscriptApi()

            # Try Korean transcript first, then English as fallback
            languages = ['ko', 'en']
            transcript_text = None

            for lang in languages:
                try:
                    fetched = api.fetch(video_id, languages=[lang])
                    transcript_text = ' '.join([snippet.text for snippet in fetched.snippets])
                    break
                except NoTranscriptFound:
                    continue

            if transcript_text is None:
                raise Exception("한글 또는 영어 자막을 찾을 수 없습니다.")

            return transcript_text
        except TranscriptsDisabled:
            raise Exception("이 영상은 자막이 비활성화되어 있습니다.")
        except Exception as e:
            raise Exception(f"자막 추출 중 오류 발생: {str(e)}")

    def get_video_title(self, video_id: str) -> str:
        url = f"https://www.youtube.com/watch?v={video_id}"
        oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
        try:
            with urllib.request.urlopen(oembed_url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                return data.get("title", video_id)
        except Exception:
            return video_id

    @staticmethod
    def sanitize_filename(title: str, max_length: int = 50) -> str:
        import re as _re
        sanitized = _re.sub(r'[\\/:*?"<>|]', '', title)
        sanitized = _re.sub(r'\s+', '_', sanitized.strip())
        return sanitized[:max_length]
