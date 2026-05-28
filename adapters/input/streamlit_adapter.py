"""Streamlit UI adapter."""
import logging
import streamlit as st
from pathlib import Path
from typing import Optional
from application.use_cases.process_audio_use_case import ProcessAudioUseCase
from application.use_cases.process_youtube_use_case import ProcessYoutubeUseCase
from application.use_cases.chat_use_case import ChatUseCase
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from adapters.output.html_player_adapter import HTMLPlayerAdapter

logger = logging.getLogger(__name__)


class StreamlitAdapter:
    """Adapter for Streamlit UI interactions."""

    def __init__(
        self,
        process_audio_use_case: ProcessAudioUseCase,
        process_youtube_use_case: ProcessYoutubeUseCase,
        chat_use_case: ChatUseCase,
        repository: SummaryRepositoryPort,
        html_player: HTMLPlayerAdapter
    ):
        self.process_audio_use_case = process_audio_use_case
        self.process_youtube_use_case = process_youtube_use_case
        self.chat_use_case = chat_use_case
        self.repository = repository
        self.html_player = html_player

    def render_ui(self):
        """Render main Streamlit UI."""
        st.title("🎙️ 음성 인식 및 요약 서비스")

        page = st.radio(
            "메뉴",
            ["📤 음성 파일 업로드", "🎬 YouTube", "📋 저장된 요약", "💬 채팅"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if page == "📤 음성 파일 업로드":
            self._render_upload_tab()
        elif page == "🎬 YouTube":
            self._render_youtube_tab()
        elif page == "📋 저장된 요약":
            self._render_history_tab()
        elif page == "💬 채팅":
            self._render_chat_tab()

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
                    st.iframe(html_content, height=600)

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
        summaries = self.repository.load_all()

        if not summaries:
            st.info("저장된 요약이 없습니다.")
            return

        st.write(f"총 {len(summaries)}개의 요약")

        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            pass
        with col_del2:
            delete_target = st.selectbox(
                "삭제할 항목",
                options=range(len(summaries)),
                format_func=lambda i: f"{summaries[i].source_id or 'unknown'} - {summaries[i].timestamp.strftime('%Y-%m-%d %H:%M') if summaries[i].timestamp else 'N/A'}",
                key="delete_target"
            )
            if st.button("🗑️ 삭제", type="secondary"):
                target = summaries[delete_target]
                sid = target.source_id or "unknown"
                try:
                    logger.info(f"Deleting: source_id={sid}, timestamp={target.timestamp}")
                    self.repository.delete(target)
                    logger.info(f"Deleted: {sid}")
                    st.success(f"삭제 완료: {sid}")
                except Exception as e:
                    logger.error(f"Delete failed: {e}", exc_info=True)
                    st.error(f"삭제 실패: {e}")

        st.divider()

        for idx, summary in enumerate(summaries):
            sid = summary.source_id or "unknown"
            ts_str = summary.timestamp.strftime('%Y%m%d_%H%M%S') if summary.timestamp else 'nots'
            label = f"🎬 {sid} - {summary.timestamp.strftime('%Y-%m-%d %H:%M') if summary.timestamp else 'N/A'}"

            with st.expander(label):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📁 소스 타입: {summary.source_type or 'N/A'}")
                with col2:
                    if summary.timestamp:
                        st.caption(f"🕐 처리 시간: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                with col3:
                    if summary.model:
                        st.caption(f"🤖 모델: {summary.model[:50]}...")

                if summary.source_url:
                    st.caption(f"🔗 원본 URL: {summary.source_url}")

                if summary.summary_text:
                    st.subheader("📝 요약")
                    st.write(summary.summary_text)

                if summary.transcript:
                    st.subheader("📜 전체 스크립트")
                    st.text_area(
                        "전체 스크립트",
                        value=summary.transcript,
                        height=200,
                        disabled=True,
                        label_visibility="collapsed",
                        key=f"transcript_{idx}"
                    )

                if summary.audio_file_path and summary.segments:
                    audio_path = Path(summary.audio_file_path)
                    if audio_path.exists():
                        st.subheader("🎵 인터랙티브 음성 플레이어")
                        html_content = self.html_player.render(
                            audio_path=audio_path,
                            segments=summary.segments
                        )
                        st.iframe(html_content, height=600)

                if summary.timestamp:
                    json_filename = f"{sid}_{ts_str}.json"
                    json_path = Path("summaries") / json_filename
                    st.info(f"저장 위치: {json_path}")

    def _render_chat_tab(self):
        summaries = self.repository.load_all()

        if not summaries:
            st.info("먼저 영상/음성을 처리하여 요약을 생성해주세요.")
            return

        selected_summary = self._render_summary_selector(summaries)
        if not selected_summary:
            return

        self._render_chat_interface(selected_summary)

    def _render_summary_selector(self, summaries):
        summary_options = {
            f"{s.source_id} - {s.timestamp.strftime('%Y-%m-%d %H:%M') if s.timestamp else 'N/A'}": s
            for s in summaries
        }
        selected_label = st.selectbox(
            "채팅할 요약본을 선택하세요",
            options=list(summary_options.keys()),
            index=0
        )
        return summary_options.get(selected_label)

    def _render_chat_interface(self, summary):
        st.write(f"**{summary.source_id}** 의 스크립트를 기반으로 질문하세요.")

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        if st.button("🔄 대화 초기화"):
            st.session_state.chat_messages = []
            self.chat_use_case.clear_history()

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("영상 내용에 대해 질문하세요..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("답변 생성 중..."):
                    try:
                        response = self.chat_use_case.chat(
                            messages=st.session_state.chat_messages,
                            summary=summary
                        )
                        st.markdown(response)
                    except Exception as e:
                        response = f"오류가 발생했습니다: {str(e)}"
                        st.error(response)

            st.session_state.chat_messages.append({"role": "assistant", "content": response})
