"""Streamlit UI adapter."""
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from typing import Optional
from application.use_cases.process_audio_use_case import ProcessAudioUseCase
from application.use_cases.process_youtube_use_case import ProcessYoutubeUseCase
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from adapters.output.html_player_adapter import HTMLPlayerAdapter


class StreamlitAdapter:
    """Adapter for Streamlit UI interactions."""

    def __init__(
        self,
        process_audio_use_case: ProcessAudioUseCase,
        process_youtube_use_case: ProcessYoutubeUseCase,
        repository: SummaryRepositoryPort,
        html_player: HTMLPlayerAdapter
    ):
        self.process_audio_use_case = process_audio_use_case
        self.process_youtube_use_case = process_youtube_use_case
        self.repository = repository
        self.html_player = html_player

    def render_ui(self):
        """Render main Streamlit UI."""
        st.title("🎙️ 음성 인식 및 요약 서비스")

        tab1, tab2, tab3 = st.tabs(["📤 음성 파일 업로드", "🎬 YouTube", "📋 저장된 요약"])

        with tab1:
            self._render_upload_tab()

        with tab2:
            self._render_youtube_tab()

        with tab3:
            self._render_history_tab()

    def _render_upload_tab(self):
        """Render audio upload and processing tab."""
        uploaded_file = st.file_uploader(
            "음성 파일을 업로드하세요",
            type=['mp3', 'wav', 'm4a', 'ogg']
        )

        if uploaded_file:
            st.audio(uploaded_file)

            source_id = st.text_input("소스 ID", value=uploaded_file.name.split('.')[0])

            if st.button("🚀 처리 시작", type="primary"):
                self._process_uploaded_audio(uploaded_file, source_id)

    def _process_uploaded_audio(self, uploaded_file, source_id: str):
        """Process uploaded audio file."""
        with st.spinner("음성을 텍스트로 변환 중..."):
            # Save uploaded file temporarily
            temp_path = f"/tmp/{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # Execute use case
                summary, json_path, audio_path = self.process_audio_use_case.execute(
                    audio_file_path=temp_path,
                    source_id=source_id,
                    source_url="",
                    source_type="audio"
                )

                st.success("✅ 처리 완료!")

                # Display results
                st.subheader("📝 요약")
                st.write(summary.summary_text)

                st.subheader("📜 전체 스크립트")
                with st.expander("전체 스크립트 보기"):
                    st.text(summary.transcript)

                # Render interactive player
                if audio_path and summary.segments:
                    st.subheader("🎵 인터랙티브 음성 플레이어")
                    html_content = self.html_player.render(
                        audio_path=Path(audio_path),
                        segments=summary.segments
                    )
                    components.html(html_content, height=600, scrolling=True)

                st.info(f"저장 위치: {json_path}")

            except Exception as e:
                st.error(f"처리 중 오류 발생: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

    def _render_youtube_tab(self):
        """Render YouTube video processing tab."""
        youtube_url = st.text_input(
            "YouTube URL을 입력하세요",
            placeholder="https://www.youtube.com/watch?v=..."
        )

        if st.button("🚀 처리 시작", type="primary", key="youtube_btn"):
            if not youtube_url:
                st.error("YouTube URL을 입력하세요.")
                return

            with st.spinner("YouTube 자막 추출 및 요약 중..."):
                try:
                    # Execute use case
                    summary, json_path = self.process_youtube_use_case.execute(youtube_url)

                    st.success("✅ 처리 완료!")

                    # Display results
                    st.subheader("📝 요약")
                    st.write(summary.summary_text)

                    st.subheader("📜 전체 스크립트")
                    with st.expander("전체 스크립트 보기"):
                        st.text(summary.transcript)

                    st.info(f"저장 위치: {json_path}")

                except Exception as e:
                    st.error(f"처리 중 오류 발생: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

    def _render_history_tab(self):
        """Render saved summaries history tab."""
        summaries = self.repository.load_all()

        if not summaries:
            st.info("저장된 요약이 없습니다.")
            return

        st.write(f"총 {len(summaries)}개의 요약")

        for summary in summaries:
            with st.expander(
                f"🎬 {summary.source_id} - {summary.timestamp.strftime('%Y-%m-%d %H:%M')}"
            ):
                # 메타데이터 정보
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📁 소스 타입: {summary.source_type}")
                with col2:
                    if summary.timestamp:
                        st.caption(f"🕐 처리 시간: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                with col3:
                    if summary.model:
                        st.caption(f"🤖 모델: {summary.model[:50]}...")

                if summary.source_url:
                    st.caption(f"🔗 원본 URL: {summary.source_url}")

                # 요약 섹션
                st.subheader("📝 요약")
                st.write(summary.summary_text)

                # 전체 스크립트 섹션
                if summary.transcript:
                    st.subheader("📜 전체 스크립트")
                    with st.expander("전체 스크립트 보기"):
                        st.text(summary.transcript)

                # 인터랙티브 플레이어 섹션
                if summary.audio_file_path and summary.segments:
                    audio_path = Path(summary.audio_file_path)
                    if audio_path.exists():
                        st.subheader("🎵 인터랙티브 음성 플레이어")
                        html_content = self.html_player.render(
                            audio_path=audio_path,
                            segments=summary.segments
                        )
                        components.html(html_content, height=600, scrolling=True)

                # 저장 위치 정보
                if summary.timestamp:
                    json_filename = f"{summary.source_id}_{summary.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                    json_path = Path("summaries") / json_filename
                    st.info(f"저장 위치: {json_path}")
