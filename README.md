from flashcard_gen import generate_flashcard_set

# Ollama Flashcard Generator

Generate flashcards from markdown notes using local LLMs through Ollama. Built as a foundation for a future Obsidian plugin.

The program splits markdown files into chunks and generates flashcards for each section. It supports keyword targeting for focused generation and includes duplicate checking to keep cards unique.

## Features

- Basic Q&A and cloze deletion card types
- String similarity and semantic embedding duplicate detection
- Multiple chunking strategies (header, paragraph, length, hierarchical)
- RAG support for better keyword-targeted generation
- Runs fully local via Ollama

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
flashcard-gen notes.md --rag -k "sigmoid" "relu"
```
Python - Can also call functions directly
```python
from flashcard_gen.generate import generate_flashcard_set, generate_flashcard_set_rag

cards = generate_flashcard_set(notes="## Topic\n\nContent...", num_cards=5)
cards = generate_flashcard_set_rag(notes="...", keywords=["topic1"], num_cards=5)
```

## Requirements

- Python 3.12+
- [Ollama](https://ollama.com/download) with a model installed (e.g. `ollama pull qwen2.5:3b`)

### Python Packages

- pydantic >= 2.0.0
- numpy >= 1.24.0
- ollama >= 0.1.0
- faiss-cpu >= 1.7.0 (for RAG)
- sentence-transformers >= 2.0.0 (for RAG)

These install automatically with `pip install -e .`

## Future Plans

- Obsidian plugin
- Direct Anki export
- Fine-tuned model for better card quality