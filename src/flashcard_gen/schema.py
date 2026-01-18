from enum import Enum
import re
from pydantic import BaseModel, field_validator, model_validator


class CardType(str, Enum):
    BASIC = "basic"
    CLOZE = "cloze"


class SimilarityMethod(str, Enum):
    STRING = "string"
    SEMANTIC = "semantic"
    BOTH = "both"


class Flashcard(BaseModel):
    """A single flashcard."""
    front: str
    back: str = ""
    type: CardType = CardType.BASIC

    @field_validator("front")
    @classmethod
    def front_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Front cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_card_type(self):
        """Validate based on card type."""
        if self.type == CardType.BASIC:
            if not self.back.strip():
                raise ValueError("Basic cards must have a non-empty back")
            self.back = self.back.strip()
        elif self.type == CardType.CLOZE:
            if not re.search(r"\{\{c\d+::.*?\}\}", self.front):
                raise ValueError("Cloze cards must contain {{c1::...}} pattern")
        return self

    def __eq__(self, other):
        if not isinstance(other, Flashcard):
            return False
        return self.front == other.front and self.back == other.back

    def __hash__(self):
        return hash((self.front, self.back))


class GenerationConfig(BaseModel):
    """Configuration for flashcard generation."""
    model: str = "qwen2.5:3b"
    num_cards: int = 5
    card_type: str = "basic"
    keywords: list[str] | None = None
    temperature: float = 0.7
    similarity_method: SimilarityMethod = SimilarityMethod.STRING
    string_threshold: float = 0.7
    semantic_threshold: float = 0.85