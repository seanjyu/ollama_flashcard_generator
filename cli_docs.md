# Ollama Flashcard Generator CLI

## Basic Usage

```bash
flashcard-gen <file> [options]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `file` | Path to markdown file, or `-` for stdin |

## Options

| Flag | Long | Default | Description |
|------|------|---------|-------------|
| `-n` | `--num` | `5` | Number of cards to generate |
| `-k` | `--keywords` | None | Keywords to focus on (space-separated) |
| `-t` | `--type` | `basic` | Card type: `basic`, `cloze`, or `mixed` |
| `-m` | `--model` | `qwen2.5:3b` | Ollama model to use |
| `-o` | `--output` | stdout | Output file path |
| | `--format` | `json` | Output format: `json`, `csv`, or `anki` |
| | `--semantic-dedup` | off | Enable semantic duplicate detection |

## Examples

### Generate 5 basic flashcards

```bash
flashcard-gen notes.md
```

### Generate 10 cards focused on specific topics

```bash
flashcard-gen notes.md -n 10 -k "mitosis" "cell division" "chromosomes"
```

### Generate cloze deletion cards

```bash
flashcard-gen notes.md -t cloze
```

### Generate mixed card types

```bash
flashcard-gen notes.md -t mixed -n 8
```

### Save to file

```bash
flashcard-gen notes.md -o cards.json
```

### Export as CSV

```bash
flashcard-gen notes.md --format csv -o cards.csv
```

### Export for Anki import (tab-separated)

```bash
flashcard-gen notes.md --format anki -o cards.txt
```

### Use a different model

```bash
flashcard-gen notes.md -m phi3:mini
flashcard-gen notes.md -m qwen2.5:7b
flashcard-gen notes.md -m llama3.2:3b
```

### Enable semantic deduplication

```bash
flashcard-gen notes.md --semantic-dedup
```

### Read from stdin (pipe)

```bash
cat notes.md | flashcard-gen -
echo "## Topic\n\nSome content here" | flashcard-gen - -n 2
```

### Combine multiple options

```bash
flashcard-gen lecture.md -n 15 -k "photosynthesis" "ATP" -t cloze -m qwen2.5:3b -o bio_cards.json
```

## Output Formats

### JSON (default)

```json
[
  {
    "front": "What organelle produces ATP?",
    "back": "Mitochondria",
    "type": "basic"
  }
]
```

### CSV

```csv
front,back,type
"What organelle produces ATP?","Mitochondria","basic"
```

### Anki (tab-separated)

```
What organelle produces ATP?	Mitochondria
```

Import in Anki: File → Import → Select the `.txt` file

## Requirements

- Ollama must be running (`ollama serve`)
- Model must be pulled first (`ollama pull qwen2.5:3b`)

## Troubleshooting

### "Cannot connect to Ollama"

```bash
# Start Ollama
ollama serve

# Or check if already running
ollama list
```

### "Model not found"

```bash
# Pull the model first
ollama pull qwen2.5:3b
```

### Empty output

- Check if your markdown file has content
- Try a larger model (`qwen2.5:7b`)
- Lower the duplicate threshold (requires code change)