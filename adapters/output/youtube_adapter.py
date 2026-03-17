"""YouTube transcript adapter."""
import re
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
            fetched = api.fetch(video_id, languages=['en'])
            transcript_text = ' '.join([snippet.text for snippet in fetched.snippets])
            return transcript_text
        except TranscriptsDisabled:
            raise Exception("이 영상은 자막이 비활성화되어 있습니다.")
        except NoTranscriptFound:
            raise Exception("영어 자막을 찾을 수 없습니다.")
        except Exception as e:
            raise Exception(f"자막 추출 중 오류 발생: {str(e)}")
