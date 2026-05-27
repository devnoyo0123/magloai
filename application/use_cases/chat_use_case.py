"""Use case for chatting about processed content."""
from typing import List, Dict, Optional
from application.ports.output.chat_port import ChatPort
from application.ports.output.summary_repository_port import SummaryRepositoryPort
from domain.models.summary import Summary


class ChatUseCase:
    """Use case for Q&A chat over a saved summary's content."""

    def __init__(
        self,
        chat_port: ChatPort,
        repository: SummaryRepositoryPort
    ):
        self.chat_port = chat_port
        self.repository = repository

    def build_context(self, summary: Summary) -> str:
        """
        Build context string from a Summary for chat grounding.

        Uses summary_text first, then full transcript.
        """
        parts = []
        if summary.summary_text:
            parts.append(f"[요약]\n{summary.summary_text}")
        if summary.transcript:
            parts.append(f"[전체 스크립트]\n{summary.transcript}")
        return "\n\n".join(parts) if parts else "컨텍스트가 없습니다."

    def chat(
        self,
        messages: List[Dict[str, str]],
        summary: Summary
    ) -> str:
        """
        Send a chat message grounded in the given summary.

        Args:
            messages: Conversation history.
            summary: The Summary to use as context.

        Returns:
            Assistant response.
        """
        context = self.build_context(summary)
        return self.chat_port.chat(messages=messages, context=context)

    def clear_history(self) -> None:
        """Reset chat history."""
        self.chat_port.clear_history()
