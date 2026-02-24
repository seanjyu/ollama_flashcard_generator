from .schema import Flashcard, CardType, SimilarityMethod, Chunk
# from .parser import parse_flashcards
from .generate import (
    generate_single_card,
    generate_flashcard_set,
    generate_flashcard_set_rag,
)
from .duplicate_check import DuplicateChecker

__all__ = [
    "Flashcard",
    "CardType",
    "SimilarityMethod",
    # "parse_flashcards",
    "generate_single_card",
    "generate_flashcard_set",
    "DuplicateChecker",
    "Chunk",
]

__version__ = "0.1.0"