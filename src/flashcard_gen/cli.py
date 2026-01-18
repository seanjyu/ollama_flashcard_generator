"""Command-line interface."""

import argparse
import json
import sys
from pathlib import Path

from .generate import generate_flashcard_set
from .schema import SimilarityMethod


def main():
    parser = argparse.ArgumentParser(
        description="Generate Anki flashcards from markdown notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flashcard-gen notes.md
  flashcard-gen notes.md -n 10 -k "mitosis" "ATP"
  flashcard-gen notes.md -t cloze -o cards.json
  flashcard-gen notes.md --semantic-dedup
        """
    )

    parser.add_argument("file", help="Markdown file (or - for stdin)")
    parser.add_argument("-n", "--num", type=int, default=5, help="Number of cards (default: 5)")
    parser.add_argument("-k", "--keywords", nargs="+", help="Keywords to focus on")
    parser.add_argument("-t", "--type", choices=["basic", "cloze", "mixed"],
                        default="basic", help="Card type (default: basic)")
    parser.add_argument("-m", "--model", default="qwen2.5:3b", help="Ollama model")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--semantic-dedup", action="store_true",
                        help="Use semantic similarity for deduplication")
    parser.add_argument("--format", choices=["json", "csv", "anki"],
                        default="json", help="Output format (default: json)")

    args = parser.parse_args()

    # Read input
    if args.file == "-":
        notes = sys.stdin.read()
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        notes = path.read_text()

    if not notes.strip():
        print("Error: Empty input", file=sys.stderr)
        sys.exit(1)

    # Check Ollama
    try:
        import ollama
        ollama.list()
    except Exception as e:
        print(f"Error: Cannot connect to Ollama. Is it running?\n{e}", file=sys.stderr)
        sys.exit(1)

    # Generate
    similarity = SimilarityMethod.BOTH if args.semantic_dedup else SimilarityMethod.STRING

    cards = generate_flashcard_set(
        notes=notes,
        num_cards=args.num,
        keywords=args.keywords,
        model=args.model,
        card_type=args.type,
        similarity_method=similarity,
    )

    if not cards:
        print("Warning: No cards generated", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format == "json":
        output = json.dumps([c.model_dump() for c in cards], indent=2)
    elif args.format == "csv":
        lines = ["front,back,type"]
        for c in cards:
            front = c.front.replace('"', '""')
            back = c.back.replace('"', '""')
            lines.append(f'"{front}","{back}","{c.type.value}"')
        output = "\n".join(lines)
    elif args.format == "anki":
        # Anki tab-separated import format
        output = "\n".join(f"{c.front}\t{c.back}" for c in cards)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {len(cards)} cards to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
