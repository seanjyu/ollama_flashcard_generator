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
| `-v` | `--verbose` | off | Print debug info |
| | `--format` | `json` | Export format: `json`, `csv`, or `anki` |
| | `--output-format` | `simple` | LLM output format: `simple` (Q:/A:) or `json` |
| | `--rag` | off | Enable RAG for context retrieval |
| | `--chunker` | `hierarchical` | Chunking strategy: `header`, `paragraph`, `length`, or `hierarchical` |
| | `--threshold` | `0.7` | Duplicate detection threshold (0.0-1.0) |
| | `--temperature` | `0.7` | LLM temperature (higher = more variety) |

## Examples

### Generate 5 basic flashcards
```bash
flashcard-gen notes.md
```

### Generate 10 cards focused on specific topics
```bash
flashcard-gen notes.md -n 10 -k "sigmoid" "activation function" "relu"
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

### Use RAG for better keyword targeting
```bash
flashcard-gen notes.md --rag -k "sigmoid" "relu" "activation"
```

### Choose chunking strategy
```bash
# Split by headers only
flashcard-gen notes.md --chunker header

# Split by paragraph
flashcard-gen notes.md --chunker paragraph

# Split by word count
flashcard-gen notes.md --chunker length

# Headers first, then paragraphs if too long (default)
flashcard-gen notes.md --chunker hierarchical
```

### Adjust duplicate detection
```bash
# Stricter (fewer similar cards allowed)
flashcard-gen notes.md --threshold 0.5

# More permissive (only reject near-duplicates)
flashcard-gen notes.md --threshold 0.9
```

### Use a different model
Note this requires that the model be installed through Ollama.
```bash
flashcard-gen notes.md -m phi3:mini
flashcard-gen notes.md -m qwen2.5:7b
flashcard-gen notes.md -m llama3.2:3b
```

### Use JSON output format from LLM
```bash
flashcard-gen notes.md --output-format json
```

### Enable verbose debugging
```bash
flashcard-gen notes.md -v
```

### Read from stdin (pipe)
```bash
cat notes.md | flashcard-gen -
echo "## Topic\n\nSome content here" | flashcard-gen - -n 2
```

### Combine multiple options
```bash
flashcard-gen lecture.md -n 10 -k "sigmoid" "relu" -t basic --rag --chunker header --threshold 0.8 --temperature 0.5 -v -o cards.json
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

## Chunking Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| `header` | Split by markdown headers (# ## ###) | Well-structured notes |
| `paragraph` | Split by paragraphs | Prose-heavy content |
| `length` | Split by word count | Very long documents |
| `hierarchical` | Headers first, then paragraphs if needed | General purpose (default) |

## Requirements

- Ollama must be running (`ollama serve`)
- Model must be pulled first (`ollama pull qwen2.5:3b`)
- For RAG: `faiss-cpu` and `sentence-transformers` packages

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

### Only getting 1 card

- Duplicate threshold may be too low
- Try `--threshold 0.8` or higher

### Empty output

- Check if your markdown file has content
- Try `--verbose` to see what's happening