import streamlit as st
import streamlit.components.v1 as components
import os
import json
import base64
from datetime import datetime
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
import re
from dotenv import load_dotenv
import tempfile

# 환경 변수 로드
load_dotenv()

# 요약 저장 디렉토리
SUMMARIES_DIR = Path("summaries")
SUMMARIES_DIR.mkdir(exist_ok=True)

# 음성 파일 저장 디렉토리
AUDIO_FILES_DIR = SUMMARIES_DIR / "audio_files"
AUDIO_FILES_DIR.mkdir(exist_ok=True)

# OpenRouter 클라이언트 설정
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def extract_video_id(url):
    """YouTube URL에서 video ID 추출"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """YouTube 자막 추출"""
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

def transcribe_audio(audio_file):
    """음성 파일을 텍스트로 변환 (faster-whisper)"""
    try:
        from faster_whisper import WhisperModel

        # 모델 로드
        model_size = os.getenv("WHISPER_MODEL", "base")

        with st.spinner(f"Whisper 모델 로딩 중... ({model_size})"):
            model = WhisperModel(model_size, device="cpu", compute_type="int8")

        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.name).suffix) as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_path = tmp_file.name

        # 음성 인식
        segments, info = model.transcribe(tmp_path, beam_size=5)

        # 타임스탬프 포함하여 저장
        segments_list = []
        for segment in segments:
            segments_list.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text
            })

        # 전체 텍스트 (기존 호환성 유지)
        transcript_text = ' '.join([s['text'] for s in segments_list])

        # 임시 파일 삭제
        os.unlink(tmp_path)

        return transcript_text, info, segments_list

    except ImportError:
        raise Exception("faster-whisper가 설치되지 않았습니다. 'pip install faster-whisper'를 실행하세요.")
    except Exception as e:
        raise Exception(f"음성 인식 중 오류 발생: {str(e)}")

def summarize_and_translate(transcript):
    """OpenRouter를 사용하여 요약 및 번역"""
    try:
        max_chars = 15000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "..."

        prompt = f"""다음은 YouTube 영상의 영어 자막입니다. 이 내용을 분석하여:

1. 핵심 내용을 5-7개 bullet point로 요약
2. 전체를 3-4문장으로 요약
3. 모든 결과를 자연스러운 한국어로 작성

자막:
{transcript}

다음 형식으로 답변해주세요:

## 핵심 요약
- [bullet point 1]
- [bullet point 2]
...

## 전체 요약
[3-4문장 요약]"""

        model_name = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"요약 중 오류 발생: {str(e)}")

def render_interactive_player(audio_path, segments):
    """인터랙티브 플레이어"""
    with open(audio_path, 'rb') as f:
        audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    
    ext = Path(audio_path).suffix.lower()
    mime_types = {'.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.m4a': 'audio/mp4', '.flac': 'audio/flac', '.ogg': 'audio/ogg'}
    mime_type = mime_types.get(ext, 'audio/mpeg')
    
    segments_html = ""
    for i, seg in enumerate(segments):
        start_time = seg['start']
        minutes, seconds = int(start_time // 60), int(start_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        text = seg['text'].strip()
        segments_html += f'<div class="segment" id="segment-{i}"><button class="timestamp-btn" onclick="seekTo({start_time}, {i})">⏱️ {time_str}</button><p class="segment-text">{text}</p></div>'
    
    html_code = f"""<!DOCTYPE html><html><head><style>* {{margin:0;padding:0;box-sizing:border-box}}body {{font-family:sans-serif;background:#0e1117;color:#fafafa}}.container {{padding:20px;padding-bottom:140px}}.segment {{margin-bottom:15px;padding:15px;border-left:3px solid #4CAF50;background:#1e1e1e;border-radius:0 8px 8px 0;transition:all 0.2s}}.segment:hover {{background:#262626;transform:translateX(5px)}}.segment.active {{background:#2d3a2e;border-left-color:#81C784;box-shadow:0 0 20px rgba(76,175,80,0.2)}}.timestamp-btn {{background:linear-gradient(135deg,#4CAF50,#45a049);color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-weight:600;margin-bottom:8px;transition:all 0.2s}}.timestamp-btn:hover {{background:linear-gradient(135deg,#66BB6A,#4CAF50);transform:translateY(-2px)}}.segment-text {{line-height:1.6;color:#e0e0e0}}.audio-panel {{position:fixed;bottom:0;left:0;right:0;background:#1e1e1e;padding:15px 20px;box-shadow:0 -4px 20px rgba(0,0,0,0.5);z-index:1000;border-top:2px solid #4CAF50}}.audio-controls {{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:20px}}audio {{flex:1;max-width:800px;border-radius:8px}}</style></head><body><div class="container">{segments_html}</div><div class="audio-panel"><div class="audio-controls"><audio id="audioPlayer" controls><source src="data:{mime_type};base64,{audio_base64}" type="{mime_type}"></audio></div></div><script>const audio=document.getElementById('audioPlayer');let currentSegmentIndex=-1;function seekTo(seconds,segmentIndex){{audio.currentTime=seconds;audio.play();highlightSegment(segmentIndex)}}function highlightSegment(index){{document.querySelectorAll('.segment').forEach(seg=>seg.classList.remove('active'));const segment=document.getElementById('segment-'+index);if(segment){{segment.classList.add('active');segment.scrollIntoView({{behavior:'smooth',block:'center'}});currentSegmentIndex=index}}}}audio.addEventListener('timeupdate',function(){{const current=audio.currentTime;const segments={json.dumps([{"start":s["start"],"end":s["end"]} for s in segments])};for(let i=0;i<segments.length;i++){{if(current>=segments[i].start&&current<segments[i].end){{if(currentSegmentIndex!==i)highlightSegment(i);break}}}}}});</script></body></html>"""
    
    components.html(html_code, height=700, scrolling=True)

def merge_segments_into_paragraphs(segments, transcript_text):
    """Whisper segments를 문단으로 병합"""
    try:
        if len(segments) < 5:
            return segments
        
        # 전체 텍스트를 LLM에 전달 (자르지 않음!)
        prompt = f"""다음 텍스트를 의미 있는 문단으로 나눠주세요.
규칙:
1. 각 문단은 하나의 주제/아이디어
2. 각 문단은 2-4문장
3. 원본 텍스트를 그대로 사용 (내용 수정 금지)
4. **중요**: 원본 텍스트의 순서를 절대 바꾸지 말 것 (시간 순서 유지)
5. 각 문단 사이에 "###PARAGRAPH###" 구분자
6. 다른 설명 없이 문단만 출력

텍스트:
{transcript_text}"""
        
        model_name = os.getenv("MODEL_NAME", "google/gemini-2.5-flash-lite")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000  # 충분히 큰 값
        )
        
        paragraphs = [p.strip() for p in response.choices[0].message.content.strip().split("###PARAGRAPH###") if p.strip()]
        
        if not paragraphs or len(paragraphs) < 2:
            st.warning("⚠️ 문단 분리 실패, 원본 segments 사용")
            return segments
        
        # 각 문단의 시작 시간 찾기
        paragraph_segments = []
        for para in paragraphs:
            para_words = ' '.join(para.strip().split()[:10]).lower()
            found = False
            for seg in segments:
                if para_words[:30] in seg['text'].strip().lower() or seg['text'].strip().lower()[:30] in para_words:
                    paragraph_segments.append({'start': seg['start'], 'end': seg['end'], 'text': para})
                    found = True
                    break
            if not found and paragraph_segments:
                prev_end = paragraph_segments[-1].get('end', 0)
                paragraph_segments.append({'start': prev_end, 'end': prev_end + 30, 'text': para})
            elif not found:
                paragraph_segments.append({'start': 0, 'end': 30, 'text': para})
        
        # end 시간 보정
        for i in range(len(paragraph_segments) - 1):
            paragraph_segments[i]['end'] = paragraph_segments[i + 1]['start']
        if paragraph_segments and segments:
            paragraph_segments[-1]['end'] = segments[-1]['end']
        
        return paragraph_segments if len(paragraph_segments) > 0 else segments
    
    except Exception as e:
        st.warning(f"문단 병합 실패, 원본 segments 사용: {str(e)}")
        return segments


def save_summary(source_id, source_url, summary, transcript=None, audio_file=None, segments=None, source_type="youtube"):
    """요약, 전체 스크립트, 음성 파일, 타임스탬프를 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source_type}_{source_id}_{timestamp}.json"
    filepath = SUMMARIES_DIR / filename

    # 음성 파일 저장 (음성 파일이 있는 경우)
    audio_file_path = None
    audio_file_absolute_path = None
    if audio_file is not None:
        audio_filename = f"{source_type}_{source_id}_{timestamp}{Path(audio_file.name).suffix}"
        audio_file_absolute_path = AUDIO_FILES_DIR / audio_filename
        with open(audio_file_absolute_path, 'wb') as f:
            f.write(audio_file.getvalue())
        # 상대 경로로 저장
        audio_file_path = str(audio_file_absolute_path.relative_to(SUMMARIES_DIR.parent))

    data = {
        "source_type": source_type,
        "source_id": source_id,
        "source_url": source_url,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "transcript": transcript,
        "audio_file": audio_file_path,
        "segments": segments,
        "model": os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath, audio_file_absolute_path

def load_summaries():
    """저장된 요약 목록 불러오기"""
    summaries = []
    if SUMMARIES_DIR.exists():
        for filepath in sorted(SUMMARIES_DIR.glob("*.json"), reverse=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries.append({
                        "filepath": filepath,
                        "filename": filepath.name,
                        "source_type": data.get("source_type", "youtube"),
                        "source_id": data.get("source_id", data.get("video_id", "Unknown")),
                        "source_url": data.get("source_url", data.get("url", "")),
                        "timestamp": data.get("timestamp", ""),
                        "summary": data.get("summary", ""),
                        "model": data.get("model", "")
                    })
            except:
                continue
    return summaries

# Streamlit UI
st.set_page_config(page_title="YouTube 자막 & 음성 요약기", page_icon="🎤", layout="wide")

# Session state 초기화
if 'selected_summary' not in st.session_state:
    st.session_state.selected_summary = None

st.title("🎤 YouTube 자막 & 음성 요약기")

# API 키 확인
if not os.getenv("OPENROUTER_API_KEY"):
    st.error("⚠️ OPENROUTER_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    st.stop()

# 사이드바
with st.sidebar:
    # 홈 버튼 (요약 보기 중일 때만 표시)
    if st.session_state.selected_summary:
        if st.button("🏠 홈으로", type="primary", use_container_width=True):
            st.session_state.selected_summary = None
            st.rerun()
        st.markdown("---")

    st.markdown("### 📚 요약 히스토리")

    summaries = load_summaries()

    if summaries:
        st.markdown(f"총 {len(summaries)}개의 요약")

        # 선택 박스
        options = ["새 요약 작성하기"] + [
            f"{'🎬' if item['source_type']=='youtube' else '🎤'} {item['source_id']} ({item['timestamp'][:19]})"
            for item in summaries
        ]

        selected = st.selectbox(
            "요약 선택",
            options,
            index=0
        )

        # 선택된 요약 저장
        if selected != "새 요약 작성하기":
            selected_index = options.index(selected) - 1
            st.session_state.selected_summary = summaries[selected_index]
        else:
            st.session_state.selected_summary = None

        # 전체 삭제 버튼
        st.markdown("")
        if st.button("🗑️ 전체 히스토리 삭제", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_delete', False):
                try:
                    deleted_count = 0
                    for item in summaries:
                        item['filepath'].unlink()
                        deleted_count += 1
                    st.success(f"✅ {deleted_count}개의 요약이 삭제되었습니다!")
                    st.session_state.selected_summary = None
                    st.session_state.confirm_delete = False
                    st.rerun()
                except Exception as e:
                    st.error(f"삭제 실패: {e}")
                    st.session_state.confirm_delete = False
            else:
                st.session_state.confirm_delete = True
                st.warning("⚠️ 한 번 더 누르면 모든 히스토리가 삭제됩니다!")
    else:
        st.info("아직 저장된 요약이 없습니다.")
        st.session_state.selected_summary = None

    st.markdown("---")
    st.markdown("### ℹ️ 사용 방법")
    st.markdown("""
    **YouTube 탭**
    1. YouTube URL 입력
    2. '요약하기' 클릭

    **음성 파일 탭**
    1. 음성 파일 업로드
    2. 자동 처리
    """)

    st.markdown("### ⚙️ 설정")
    current_model = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    st.markdown(f"요약 모델: `{current_model[:30]}...`")
    st.markdown(f"음성 모델: `{whisper_model}`")
    st.markdown(f"API 키: {'✅' if os.getenv('OPENROUTER_API_KEY') else '❌'}")

# 메인 영역
if st.session_state.selected_summary:
    # 저장된 요약 표시
    item = st.session_state.selected_summary

    source_icon = "🎬" if item['source_type'] == 'youtube' else "🎤"
    source_label = "YouTube" if item['source_type'] == 'youtube' else "음성 파일"

    st.markdown(f"### 📝 저장된 요약 ({source_icon} {source_label})")
    st.markdown(f"**ID:** {item['source_id']}")
    if item['source_url']:
        st.markdown(f"**URL/파일:** {item['source_url']}")
    st.markdown(f"**날짜:** {item['timestamp'][:19]}")
    st.markdown(f"**모델:** `{item['model']}`")

    st.markdown("---")
    st.markdown(item['summary'])

    if st.button("🗑️ 삭제", type="secondary"):
        try:
            item['filepath'].unlink()
            st.success("삭제되었습니다!")
            st.session_state.selected_summary = None
            st.rerun()
        except Exception as e:
            st.error(f"삭제 실패: {e}")

else:
    # 탭으로 YouTube / 음성 파일 분리
    tab1, tab2 = st.tabs(["🎬 YouTube 영상", "🎤 음성 파일"])

    # YouTube 탭
    with tab1:
        st.markdown("YouTube URL을 입력하면 영상 자막을 추출하여 한국어로 요약해드립니다.")

        url_input = st.text_input(
            "YouTube URL을 입력하세요",
            placeholder="https://www.youtube.com/watch?v=..."
        )

        if st.button("요약하기", type="primary", key="youtube_btn"):
            if not url_input:
                st.warning("YouTube URL을 입력해주세요.")
            else:
                video_id = extract_video_id(url_input)

                if not video_id:
                    st.error("❌ 올바른 YouTube URL이 아닙니다.")
                else:
                    try:
                        with st.spinner("자막을 추출하는 중..."):
                            transcript = get_transcript(video_id)

                        st.success(f"✅ 자막 추출 완료 ({len(transcript)} 글자)")

                        with st.spinner("요약 및 번역 중... (30초~1분 소요)"):
                            summary = summarize_and_translate(transcript)

                        save_summary(video_id, url_input, summary, "youtube")

                        st.markdown("---")
                        st.markdown("### 📝 요약 결과")
                        st.markdown(summary)
                        st.success(f"💾 요약이 저장되었습니다!")

                        with st.expander("📄 원본 자막 보기"):
                            st.text_area("원본 영어 자막", transcript, height=300)

                    except Exception as e:
                        st.error(f"❌ {str(e)}")

    # 음성 파일 탭
    with tab2:
        st.markdown("음성 파일을 업로드하면 자동으로 텍스트로 변환하여 한국어로 요약해드립니다.")

        uploaded_file = st.file_uploader(
            "음성 파일을 선택하세요",
            type=['mp3', 'wav', 'm4a', 'flac', 'ogg'],
            help="지원 형식: MP3, WAV, M4A, FLAC, OGG"
        )

        if uploaded_file is not None:
            st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')

            if st.button("음성 인식 및 요약하기", type="primary", key="audio_btn"):
                try:
                    file_id = uploaded_file.name.replace('.', '_')

                    with st.spinner("음성을 텍스트로 변환 중... (시간이 걸릴 수 있습니다)"):
                        transcript, info, segments = transcribe_audio(uploaded_file)

                    st.success(f"✅ 음성 인식 완료 ({len(transcript)} 글자, 원본 세그먼트: {len(segments)}개)")

                    # 문단 병합
                    with st.spinner("💡 의미 있는 문단으로 정리 중..."):
                        paragraph_segments = merge_segments_into_paragraphs(segments, transcript)

                    st.info(f"언어: {info.language}, 길이: {info.duration:.1f}초, 문단: {len(paragraph_segments)}개")

                    with st.spinner("요약 및 번역 중..."):
                        summary = summarize_and_translate(transcript)

                    # 저장하고 오디오 파일 경로 받기
                    _, saved_audio_path = save_summary(file_id, uploaded_file.name, summary, transcript=transcript, audio_file=uploaded_file, segments=paragraph_segments, source_type="audio")

                    # 인터랙티브 플레이어 표시
                    if saved_audio_path and len(paragraph_segments) > 0:
                        st.markdown("---")
                        st.markdown("### 🎧 인터랙티브 음성 플레이어")
                        st.caption("⏱️ 타임스탬프를 클릭하면 해당 시점부터 재생됩니다")
                        render_interactive_player(str(saved_audio_path), paragraph_segments)

                    st.markdown("---")
                    st.markdown("### 📝 요약 결과")
                    st.markdown(summary)
                    st.success(f"💾 요약이 저장되었습니다!")

                    with st.expander("📄 원본 텍스트 보기"):
                        st.text_area("인식된 텍스트", transcript, height=300)

                except Exception as e:
                    st.error(f"❌ {str(e)}")
