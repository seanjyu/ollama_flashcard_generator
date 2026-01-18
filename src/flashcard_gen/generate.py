"""Core flashcard generation logic."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import ollama
from .schema import Flashcard, CardType, SimilarityMethod, GenerationConfig
from .parser import parse_single_card
from .duplicate_check import DuplicateChecker

# Prompts
SYSTEM_PROMPTS = {
    "basic": """Generate exactly ONE Anki flashcard from the notes.
Output ONLY valid JSON (not array):
{"front": "question", "back": "answer", "type": "basic"}
Keep answers concise (1-10 words).""",

    "cloze": """Generate exactly ONE Anki cloze flashcard from the notes.
Output ONLY valid JSON (not array):
{"front": "sentence with {{c1::hidden term}}", "back": "", "type": "cloze"}
Use {{c1::...}} to mark hidden parts.""",

    "mixed": """Generate exactly ONE Anki flashcard from the notes.
Choose either basic or cloze format:
Basic: {"front": "question", "back": "answer", "type": "basic"}
Cloze: {"front": "{{c1::term}} in context", "back": "", "type": "cloze"}
Output ONLY valid JSON.""",
}

def chunk_by_headers(content: str, max_words: int = 300) -> list[str]:
    """Split markdown into smaller chunks by H1 headers only."""
    import re

    # Split by # headers
    sections = re.split(r'(?=^# [^#])', content, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if len(section.split()) < 20:
            continue
        chunks.append(section)

    return chunks if chunks else [content]

def chunk_by_headers(content: str, max_words: int = 250) -> list[str]:
    """Split markdown into smaller chunks by headers."""
    import re

    # Split by ## or ### headers
    sections = re.split(r'(?=^#{2,3} )', content, flags=re.MULTILINE)

    chunks = []
    for section in sections:
        section = section.strip()
        if len(section.split()) < 20:  # Skip tiny sections
            continue

        # If section still too long, split by paragraphs
        if len(section.split()) > max_words:
            paragraphs = section.split('\n\n')
            buffer = ""
            for para in paragraphs:
                if len((buffer + para).split()) < max_words:
                    buffer += "\n\n" + para
                else:
                    if buffer.strip():
                        chunks.append(buffer.strip())
                    buffer = para
            if buffer.strip():
                chunks.append(buffer.strip())
        else:
            chunks.append(section)
    return chunks if chunks else [content]  # Fallback to original


def chunk_by_length(content: str, max_words: int = 300, overlap: int = 50) -> list[str]:
    """Split content into chunks with overlap for context."""
    words = content.split()

    if len(words) <= max_words:
        return [content]

    chunks = []
    start = 0

    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap  # Overlap with previous chunk

    return chunks


def generate_single_card(
        notes: str,
        model: str = "qwen2.5:3b",
        keyword: str | None = None,
        card_type: str = "basic",
        temperature: float = 0.7,
        verbose: bool = False,
) -> Flashcard | None:
    """
    Generate a single flashcard.

    Args:
        notes: Source markdown notes
        model: Ollama model name
        keyword: Optional keyword to focus on
        card_type: "basic", "cloze", or "mixed"
        temperature: Generation temperature (higher = more variety)

    Returns:
        Flashcard or None if generation/parsing failed
    """
    system = SYSTEM_PROMPTS.get(card_type, SYSTEM_PROMPTS["basic"])

    if keyword:
        system += f"\n- Focus specifically on: {keyword}"

    try:
        if verbose:
            print("Sending Ollama Request with prompt:", system)
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Generate a flashcard from:\n\n{notes}"}
            ],
            options={"temperature": temperature}
        )

        return parse_single_card(response["message"]["content"])
    except Exception:
        if verbose:
            print("Ollama Request failed")
        return None


def generate_flashcard_set(
        notes: str,
        num_cards: int = 3,
        keywords: list[str] | None = None,
        model: str = "qwen2.5:3b",
        card_type: str = "basic",
        similarity_method: SimilarityMethod = SimilarityMethod.STRING,
        string_threshold: float = 0.5,
        verbose: bool =  False,
        **kwargs
) -> list[Flashcard]:
    """
    Generate a set of unique flashcards sequentially.

    Args:
        notes: Source markdown notes
        num_cards: Number of cards to generate
        keywords: Optional keywords to ensure coverage
        model: Ollama model name
        card_type: "basic", "cloze", or "mixed"
        similarity_method: Deduplication method

    Returns:
        List of unique flashcards
    """
    checker = DuplicateChecker(method=similarity_method, string_threshold=string_threshold)
    cards: list[Flashcard] = []

    chunks = chunk_by_length(notes)
    cards_per_chunk = max(1, num_cards // len(chunks))

    for chunk in chunks:
        if verbose:
            print(f"Generating chunk: \n {chunk}")

        # Generate keyword-focused cards first
        if verbose:
            print("Generating Flashcard for each keyword")
        if keywords:
            for kw in keywords:
                if len(cards) >= num_cards:
                    if verbose:
                        print("No Keywords")
                    break
                card = generate_single_card(chunk, model, keyword=kw, card_type=card_type, **kwargs)
                if card and not checker.is_duplicate(card, cards):
                    if verbose:
                        print("Card Passed Duplicate Check")
                    cards.append(card)
                else:
                    if verbose:
                        print("Card Failed Duplicate Check")
        if verbose:
            print("Finished Generating Cards for Keywords, generating remaining cards without keywords")
        # Fill remaining slots
        attempts = 0
        max_attempts = num_cards * 3

        while len(cards) < min(len(cards) + cards_per_chunk, num_cards) and attempts < max_attempts:
            card = generate_single_card(chunk, model, card_type=card_type, verbose = verbose, **kwargs)
            if card and not checker.is_duplicate(card, cards):
                cards.append(card)
            attempts += 1

    return cards[:num_cards]


def generate_from_config(notes: str, config: GenerationConfig) -> list[Flashcard]:
    """Generate flashcards using a configuration object."""
    return generate_flashcard_set(
        notes=notes,
        num_cards=config.num_cards,
        keywords=config.keywords,
        model=config.model,
        card_type=config.card_type,
        similarity_method=config.similarity_method,
        temperature=config.temperature,
    )
