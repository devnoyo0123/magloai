"""Port for chat-based Q&A over processed content."""
from abc import ABC, abstractmethod
from typing import List, Dict


class ChatPort(ABC):
    """Port for conversational Q&A using LLM."""

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        context: str
    ) -> str:
        """
        Send a chat message with context and get a response.

        Args:
            messages: Conversation history as list of dicts with 'role' and 'content'.
            context: The transcript/summary text to ground the conversation.

        Returns:
            Assistant response text.
        """
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """Clear internal conversation history."""
        pass
