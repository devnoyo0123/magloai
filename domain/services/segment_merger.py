"""Domain service for merging audio segments into paragraphs."""
from typing import List
from ..models.segment import Segment, ParagraphSegment


class SegmentMerger:
    """Service for merging audio segments into meaningful paragraphs."""

    def merge_into_paragraphs(
        self,
        segments: List[Segment],
        paragraphs: List[str]
    ) -> List[ParagraphSegment]:
        """
        Match paragraphs with original segments to assign timestamps.

        Args:
            segments: Original whisper segments with timestamps
            paragraphs: LLM-generated paragraph texts (in order)

        Returns:
            List of paragraph segments with timestamps
        """
        if not paragraphs or len(paragraphs) < 2:
            # Fallback to original segments
            return [ParagraphSegment(s.start, s.end, s.text) for s in segments]

        paragraph_segments = []

        for para in paragraphs:
            # Extract first 10 words for matching
            para_words = ' '.join(para.strip().split()[:10]).lower()
            found = False

            # Find matching segment
            for seg in segments:
                seg_text_lower = seg.text.strip().lower()
                if para_words[:30] in seg_text_lower or seg_text_lower[:30] in para_words:
                    paragraph_segments.append(
                        ParagraphSegment(
                            start=seg.start,
                            end=seg.end,
                            text=para
                        )
                    )
                    found = True
                    break

            # Fallback: estimate timestamp
            if not found and paragraph_segments:
                prev_end = paragraph_segments[-1].end
                paragraph_segments.append(
                    ParagraphSegment(
                        start=prev_end,
                        end=prev_end + 30,
                        text=para
                    )
                )
            elif not found:
                paragraph_segments.append(
                    ParagraphSegment(start=0, end=30, text=para)
                )

        # Fix end times
        for i in range(len(paragraph_segments) - 1):
            paragraph_segments[i].end = paragraph_segments[i + 1].start

        if paragraph_segments and segments:
            paragraph_segments[-1].end = segments[-1].end

        return paragraph_segments if paragraph_segments else [
            ParagraphSegment(s.start, s.end, s.text) for s in segments
        ]
