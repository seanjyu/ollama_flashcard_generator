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