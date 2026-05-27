"""Chat adapter using OpenRouter with NVIDIA Nemotron free model."""
from typing import List, Dict
from openai import OpenAI
from application.ports.output.chat_port import ChatPort


class ChatAdapter(ChatPort):
    """Adapter for chat Q&A via OpenRouter (NVIDIA Nemotron free model)."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)
        self.model = model
        self._history: List[Dict[str, str]] = []

    def chat(
        self,
        messages: List[Dict[str, str]],
        context: str
    ) -> str:
        """
        Send a chat completion request with transcript context.

        Args:
            messages: Conversation history [{'role': 'user'|'assistant', 'content': '...'}]
            context: Transcript + summary text to use as system context.

        Returns:
            Assistant reply text.
        """
        system_prompt = (
            "당신은 영상/음성 스크립트 분석 전문가입니다.\n"
            "아래 제공된 스크립트와 요약을 바탕으로 사용자의 질문에 한국어로 정확하게 답변해주세요.\n"
            "스크립트에 없는 내용은 추측하지 말고, 있다면 '제공된 내용에서 찾을 수 없습니다'라고 답변하세요.\n"
            "가능하면 스크립트의 구체적인 내용을 인용하여 답변하세요.\n\n"
            f"[참고 스크립트 및 요약]\n{context}"
        )

        all_messages = [{"role": "system", "content": system_prompt}] + messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            temperature=0.3
        )

        if not response.choices or not response.choices[0].message.content:
            return "모델이 응답을 생성하지 못했습니다. 다시 시도해주세요."

        return response.choices[0].message.content

    def clear_history(self) -> None:
        """Clear internal history."""
        self._history = []
