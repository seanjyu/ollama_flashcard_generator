# Ollama Flashcard Generator

Generate flashcards from markdown notes using local LLMs through Ollama. Built as a foundation for a future Obsidian plugin.

The program splits markdown files into chunks and generates flashcards for each section. It supports keyword targeting for focused generation and includes duplicate checking to keep cards unique.

## Features

- Basic Q&A and cloze deletion card types
- String similarity and semantic embedding duplicate detection
- Chunked processing for long documents
- Runs fully local via Ollama

## Limitations

- Card quality varies by model (bigger models = better results)
- Focus was on structured generation, LLM may still produce odd outputs sometimes

## Install
Clone repo
```
git clone git@github.com:seanjyu/ollama_flashcard_generator.git
cd ollama_flashcard_generator
```
Install package
```
pip install -e .
```

## Usage
CLI - Also see [cli docs](cli_docs.md).
```bash
flashcard-gen notes.md -n 5
```
Python - Can also call functions directly
```python
from flashcard_gen import generate_flashcard_set
cards = generate_flashcard_set("## Topic\n\nContent...", num_cards=5)
```

## Requirements

- Python 3.12+
- [Ollama](https://ollama.com/download) with a model installed (e.g. `ollama pull qwen2.5:3b`)

### Python Packages

- pydantic >= 2.0.0
- numpy >= 1.24.0
- ollama >= 0.1.0

These install automatically with `pip install -e .`
## Future Plans

- Obsidian plugin
- Direct Anki export
- Fine-tuned model for better card quality



