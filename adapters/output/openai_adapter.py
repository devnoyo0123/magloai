"""OpenAI API adapter for summarization and text segmentation."""
from typing import List
from openai import OpenAI
from application.ports.output.summarization_port import SummarizationPort
from application.ports.output.text_segmentation_port import TextSegmentationPort


class OpenAIAdapter(SummarizationPort, TextSegmentationPort):
    """Adapter for OpenAI/OpenRouter API."""

    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def summarize(self, text: str) -> str:
        """Summarize text in Korean using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "한국어로 요약해주세요."},
                {"role": "user", "content": f"다음 텍스트를 요약해주세요:\n\n{text}"}
            ]
        )
        return response.choices[0].message.content

    def segment_text(self, text: str) -> List[str]:
        """Segment text into paragraphs using OpenAI."""
        prompt = f"""다음 텍스트를 의미 있는 문단으로 나눠주세요.

규칙:
1. 각 문단은 하나의 주제/아이디어를 담아야 합니다
2. 각 문단은 2-4문장 정도로 구성
3. 원본 텍스트를 그대로 사용하세요 (내용 수정 금지)
4. **중요**: 원본 텍스트의 순서를 절대 바꾸지 말 것 (시간 순서 유지)
5. 각 문단 사이에 "###PARAGRAPH###" 구분자를 넣어주세요
6. 다른 설명 없이 문단만 출력하세요

텍스트:
{text}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "텍스트를 문단으로 나누는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000
        )

        result = response.choices[0].message.content
        paragraphs = [p.strip() for p in result.split("###PARAGRAPH###") if p.strip()]
        return paragraphs
