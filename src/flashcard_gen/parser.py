import json
import re
from abc import ABC, abstractmethod

from pydantic import ValidationError
from .schema import Flashcard, CardType

class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw: str) -> Flashcard | None:
        pass

class JSONParser(BaseParser):
    def parse(self, raw: str) -> Flashcard | None:
        text = raw.strip()

        # Remove markdown fences
        text = re.sub(r"```json?\s*|\s*```", "", text)

        # Find JSON object
        match = re.search(r"\{[^{}]+\}", text)
        if not match:
            return None

        text = match.group(0)
        text = re.sub(r",\s*([}\]])", r"\1", text)  # Fix trailing comma

        try:
            data = json.loads(text)
            return Flashcard(**data)
        except:
            return None


class SimpleParser(BaseParser):
    """Parse Q:/A: format output."""

    def parse(self, raw: str) -> Flashcard | None:
        raw = raw.strip()

        q_match = re.search(r"Q:\s*(.+?)(?:\n|$)", raw, re.IGNORECASE)
        a_match = re.search(r"A:\s*(.+?)(?:\n|$)", raw, re.IGNORECASE)

        if q_match and a_match:
            front = q_match.group(1).strip()
            back = a_match.group(1).strip()
            if front and back:
                return Flashcard(front=front, back=back, type=CardType.BASIC)

        return None


class ClozeParser(BaseParser):
    """Parse C: format for cloze cards."""

    def parse(self, raw: str) -> Flashcard | None:
        match = re.search(r"C:\s*(.+?)(?:\n|$)", raw, re.IGNORECASE)

        if match:
            front = match.group(1).strip()
            if "{{c1::" in front:
                return Flashcard(front=front, back="", type=CardType.CLOZE)

        return None

# def parse_flashcards(raw: str) -> tuple[list[Flashcard], list[str]]:
#     """
#     Parse LLM output into Flashcards.
#     Handles common LLM quirks: markdown fences, preamble, trailing commas.
#
#     Returns:
#         (valid_cards, errors)
#     """
#     text = raw.strip()
#     errors = []
#
#     # Remove markdown fences
#     if "```" in text:
#         match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
#         if match:
#             text = match.group(1)
#
#     # Find JSON array or object
#     array_match = re.search(r"\[[\s\S]*\]", text)
#     object_match = re.search(r"\{[\s\S]*\}", text)
#
#     if array_match:
#         text = array_match.group(0)
#     elif object_match:
#         text = f"[{object_match.group(0)}]"  # Wrap single object in array
#     else:
#         return [], ["No JSON found in response"]
#
#     # Fix trailing commas
#     text = re.sub(r",\s*([}\]])", r"\1", text)
#
#     try:
#         data = json.loads(text)
#     except json.JSONDecodeError as e:
#         return [], [f"Invalid JSON: {e}"]
#
#     if not isinstance(data, list):
#         data = [data]
#
#     cards = []
#     for i, item in enumerate(data):
#         try:
#             cards.append(Flashcard(**item))
#         except (ValidationError, TypeError) as e:
#             errors.append(f"Card {i}: {e}")
#
#     return cards, errors
#
#
# def parse_single_card(raw: str) -> Flashcard | None:
#     """Parse a single flashcard from LLM output."""
#     cards, _ = parse_flashcards(raw)
#     return cards[0] if cards else None