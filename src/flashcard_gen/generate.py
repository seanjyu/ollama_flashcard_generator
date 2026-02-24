"""Core flashcard generation logic."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import ollama
from .schema import Flashcard, CardType, SimilarityMethod, GenerationConfig
from .parser import BaseParser, SimpleParser, JSONParser, ClozeParser
from .prompts import PROMPTS
from .duplicate_check import DuplicateChecker
from .rag import FAISSRetriever
from .chunker import (
    BaseChunker,
    ChunkByHeader,
    ChunkByParagraph,
    ChunkByLength,
    ChunkHeaderThenParagraph,
)

def get_parser(card_type: str, output_format: str) -> BaseParser:
    """Get appropriate parser for card type and format."""
    if card_type == "cloze":
        return ClozeParser()
    elif output_format == "json":
        return JSONParser()
    return SimpleParser()


def generate_single_card(
        notes: str,
        model: str = "qwen2.5:3b",
        card_type: str = "basic",
        output_format: str = "simple",
        keyword: str | None = None,
        temperature: float = 0.7,
        verbose: bool = False,
) -> Flashcard | None:
    """Generate a single flashcard."""
    prompt_key = f"{card_type}_{output_format}"
    prompt = PROMPTS.get(prompt_key, PROMPTS["basic_simple"])

    if keyword:
        prompt += f"\nFocus on: {keyword}"

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": notes}
            ],
            options={"temperature": temperature}
        )

        raw = response["message"]["content"]

        if verbose:
            print(f"[DEBUG] Raw: {raw}")

        parser = get_parser(card_type, output_format)
        return parser.parse(raw)

    except Exception as e:
        if verbose:
            print(f"[DEBUG] Error: {e}")
        return None


def generate_flashcard_set(
        notes: str,
        num_cards: int = 5,
        keywords: list[str] | None = None,
        model: str = "qwen2.5:3b",
        card_type: str = "basic",
        output_format: str = "simple",
        chunker: BaseChunker | None = None,
        string_threshold: float = 0.7,
        temperature: float = 0.7,
        verbose: bool = False,
) -> list[Flashcard]:
    """Generate a set of flashcards with chunking."""
    chunker = chunker or ChunkHeaderThenParagraph()
    chunks = chunker.chunk(notes)

    if verbose:
        print(f"[DEBUG] Created {len(chunks)} chunks")

    checker = DuplicateChecker(method=SimilarityMethod.STRING, string_threshold=string_threshold)
    cards: list[Flashcard] = []

    # Keyword cards first
    if keywords:
        for kw in keywords:
            if len(cards) >= num_cards:
                break

            best_chunk = max(chunks, key=lambda c: c.content.lower().count(kw.lower()))

            card = generate_single_card(
                best_chunk.content,
                model=model,
                card_type=card_type,
                output_format=output_format,
                keyword=kw,
                temperature=temperature,
                verbose=verbose
            )

            if card and not checker.is_duplicate(card, cards):
                cards.append(card)

    # Fill from chunks
    for chunk in chunks:
        if len(cards) >= num_cards:
            break

        attempts = 0
        while len(cards) < num_cards and attempts < 3:
            card = generate_single_card(
                chunk.content,
                model=model,
                card_type=card_type,
                output_format=output_format,
                temperature=temperature,
                verbose=verbose
            )

            if card and not checker.is_duplicate(card, cards):
                cards.append(card)
                break
            attempts += 1

    return cards


def generate_flashcard_set_rag(
        notes: str,
        num_cards: int = 5,
        keywords: list[str] | None = None,
        model: str = "qwen2.5:3b",
        card_type: str = "basic",
        output_format: str = "simple",
        chunker: BaseChunker | None = None,
        string_threshold: float = 0.7,
        temperature: float = 0.7,
        verbose: bool = False,
) -> list[Flashcard]:
    """Generate flashcards using RAG retrieval."""
    chunker = chunker or ChunkHeaderThenParagraph()

    retriever = FAISSRetriever()
    retriever.index_document(notes, chunker=chunker)

    if verbose:
        print(f"[RAG] Indexed {len(retriever.chunks)} chunks")

    checker = DuplicateChecker(method=SimilarityMethod.STRING, string_threshold=string_threshold)
    cards: list[Flashcard] = []

    # Keyword-focused cards first
    if keywords:
        for kw in keywords:
            if len(cards) >= num_cards:
                break

            relevant = retriever.retrieve(kw, k=2)
            context = "\n\n".join([c.content for c in relevant])

            if verbose:
                print(f"[RAG] Keyword '{kw}' retrieved {len(relevant)} chunks")

            card = generate_single_card(
                context,
                model=model,
                card_type=card_type,
                output_format=output_format,
                keyword=kw,
                temperature=temperature,
                verbose=verbose
            )

            if card and not checker.is_duplicate(card, cards):
                cards.append(card)

    # Fill remaining from all chunks
    if len(cards) < num_cards:
        if verbose:
            print(f"[RAG] Filling remaining {num_cards - len(cards)} cards from chunks")

        for chunk in retriever.get_all_chunks():
            if len(cards) >= num_cards:
                break

            attempts = 0
            while len(cards) < num_cards and attempts < 3:
                card = generate_single_card(
                    chunk.content,
                    model=model,
                    card_type=card_type,
                    output_format=output_format,
                    temperature=temperature,
                    verbose=verbose
                )

                if card and not checker.is_duplicate(card, cards):
                    cards.append(card)
                    break
                attempts += 1

    return cards
