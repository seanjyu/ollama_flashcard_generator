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

#OLD
# def generate_single_card(
#         notes: str,
#         model: str = "qwen2.5:3b",
#         keyword: str | None = None,
#         card_type: str = "basic",
#         temperature: float = 0.7,
#         verbose: bool = False,
# ) -> Flashcard | None:
#     """
#     Generate a single flashcard.
#
#     Args:
#         notes: Source markdown notes
#         model: Ollama model name
#         keyword: Optional keyword to focus on
#         card_type: "basic", "cloze", or "mixed"
#         temperature: Generation temperature (higher = more variety)
#
#     Returns:
#         Flashcard or None if generation/parsing failed
#     """
#     system = SYSTEM_PROMPTS.get(card_type, SYSTEM_PROMPTS["basic"])
#
#     if keyword:
#         system += f"\n- Focus specifically on: {keyword}"
#
#     try:
#         if verbose:
#             print("Sending Ollama Request with prompt:", system)
#         response = ollama.chat(
#             model=model,
#             messages=[
#                 {"role": "system", "content": system},
#                 {"role": "user", "content": f"Generate a flashcard from:\n\n{notes}"}
#             ],
#             options={"temperature": temperature}
#         )
#
#         return parse_single_card(response["message"]["content"])
#     except Exception:
#         if verbose:
#             print("Ollama Request failed")
#         return None
#
#
# def generate_flashcard_set(
#         notes: str,
#         num_cards: int = 3,
#         keywords: list[str] | None = None,
#         model: str = "qwen2.5:3b",
#         card_type: str = "basic",
#         similarity_method: SimilarityMethod = SimilarityMethod.STRING,
#         string_threshold: float = 0.5,
#         verbose: bool =  False,
#         **kwargs
# ) -> list[Flashcard]:
#     """
#     Generate a set of unique flashcards sequentially.
#
#     Args:
#         notes: Source markdown notes
#         num_cards: Number of cards to generate
#         keywords: Optional keywords to ensure coverage
#         model: Ollama model name
#         card_type: "basic", "cloze", or "mixed"
#         similarity_method: Deduplication method
#
#     Returns:
#         List of unique flashcards
#     """
#     checker = DuplicateChecker(method=similarity_method, string_threshold=string_threshold)
#     cards: list[Flashcard] = []
#
#     chunks = chunk_by_length(notes)
#     cards_per_chunk = max(1, num_cards // len(chunks))
#
#     for chunk in chunks:
#         if verbose:
#             print(f"Generating chunk: \n {chunk}")
#
#         # Generate keyword-focused cards first
#         if verbose:
#             print("Generating Flashcard for each keyword")
#         if keywords:
#             for kw in keywords:
#                 if len(cards) >= num_cards:
#                     if verbose:
#                         print("No Keywords")
#                     break
#                 card = generate_single_card(chunk, model, keyword=kw, card_type=card_type, **kwargs)
#                 if card and not checker.is_duplicate(card, cards):
#                     if verbose:
#                         print("Card Passed Duplicate Check")
#                     cards.append(card)
#                 else:
#                     if verbose:
#                         print("Card Failed Duplicate Check")
#         if verbose:
#             print("Finished Generating Cards for Keywords, generating remaining cards without keywords")
#         # Fill remaining slots
#         attempts = 0
#         max_attempts = num_cards * 3
#
#         while len(cards) < min(len(cards) + cards_per_chunk, num_cards) and attempts < max_attempts:
#             card = generate_single_card(chunk, model, card_type=card_type, verbose = verbose, **kwargs)
#             if card and not checker.is_duplicate(card, cards):
#                 cards.append(card)
#             attempts += 1
#
#     return cards[:num_cards]
#
# def generate_flashcards_with_rag(
#         content: str,
#         keywords: list[str] | None = None,
#         num_cards: int = 5,
#         model: str = "qwen2.5:3b",
#         card_type: str = "basic",
#         cards_per_chunk: int = 2,
#         max_words: int = 300,
#         string_threshold: float = 0.7,
#         temperature: float = 0.7,
#         verbose: bool = False,
# ) -> list[Flashcard]:
#     """
#     Generate flashcards using RAG for context retrieval.
#
#     Args:
#         content: Full markdown document
#         keywords: Optional keywords for targeted retrieval
#         num_cards: Number of cards to generate
#         model: Ollama model name
#         cards_per_chunk: Cards per chunk when no keywords
#         max_words: Max words per chunk
#         string_threshold: Duplicate detection threshold
#         temperature: LLM temperature
#         verbose: Print debug info
#
#     Returns:
#         List of flashcards
#     """
#     # Build index
#     if verbose:
#         print("[RAG] Indexing document...")
#
#     retriever = FAISSRetriever()
#     retriever.index_document(content, max_words)
#
#     if verbose:
#         print(f"[RAG] Created {len(retriever.chunks)} chunks")
#         for i, chunk in enumerate(retriever.chunks):
#             print(f"  [{i}] {chunk.level}: {chunk.header or 'No header'} ({len(chunk.content.split())} words)")
#
#     checker = DuplicateChecker(method=SimilarityMethod.STRING, string_threshold=string_threshold)
#     cards: list[Flashcard] = []
#
#     if keywords:
#         # Retrieve relevant chunks per keyword
#         if verbose:
#             print(f"[RAG] Generating cards for keywords: {keywords}")
#
#         for keyword in keywords:
#             if len(cards) >= num_cards:
#                 break
#
#             relevant = retriever.retrieve(keyword, k=2)
#
#             if verbose:
#                 print(f"[RAG] Keyword '{keyword}' matched:")
#                 for chunk in relevant:
#                     print(f"    - {chunk.header or 'No header'}")
#
#             context = "\n\n".join([c.content for c in relevant])
#
#             card = generate_single_card(
#                 context,
#                 model=model,
#                 keyword=keyword,
#                 card_type=card_type,
#                 temperature=temperature,
#                 verbose=verbose
#             )
#
#             if card and not checker.is_duplicate(card, cards):
#                 cards.append(card)
#                 if verbose:
#                     print(f"[RAG] Added card: {card.front[:50]}...")
#     else:
#         # No keywords — generate from each chunk
#         if verbose:
#             print("[RAG] No keywords, generating from all chunks")
#
#         for chunk in retriever.get_all_chunks():
#             if len(cards) >= num_cards:
#                 break
#
#             if verbose:
#                 print(f"[RAG] Processing: {chunk.header or 'No header'}")
#
#             for _ in range(cards_per_chunk):
#                 if len(cards) >= num_cards:
#                     break
#
#                 card = generate_single_card(
#                     chunk.content,
#                     model=model,
#                     temperature=temperature,
#                     verbose=verbose
#                 )
#
#                 if card and not checker.is_duplicate(card, cards):
#                     cards.append(card)
#                     if verbose:
#                         print(f"[RAG] Added card: {card.front[:50]}...")
#
#     if verbose:
#         print(f"[RAG] Generated {len(cards)} cards total")
#
#     return cards
#
#
# def generate_from_config(notes: str, config: GenerationConfig) -> list[Flashcard]:
#     """Generate flashcards using a configuration object."""
#     return generate_flashcard_set(
#         notes=notes,
#         num_cards=config.num_cards,
#         keywords=config.keywords,
#         model=config.model,
#         card_type=config.card_type,
#         similarity_method=config.similarity_method,
#         temperature=config.temperature,
#     )
