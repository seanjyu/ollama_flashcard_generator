"""
Prompts
Note smaller llms tend to do better with the simple format.
- Basic Simple
Generate question flashcards in a simple format.

- Basic JSON
Generate question flashcards in a JSON format.

- Cloze Simple
Generate Cloze type flashcard in simple format.

- Cloze JSON
Generate Cloze type flashcard in JSON format.
"""

PROMPTS = {
    "basic_simple": """Generate ONE flashcard.

Format:
Q: [question ending with ?]
A: [short answer]

Example:
Q: What is the output range of sigmoid?
A: 0 to 1

Generate from:""",

    "basic_json": """Generate ONE flashcard as JSON:
{"front": "question?", "back": "answer", "type": "basic"}

Generate from:""",

    "cloze_simple": """Generate ONE cloze flashcard.

Format:
C: [sentence with {{c1::hidden term}}]

Example:
C: The {{c1::mitochondria}} produces ATP.

Generate from:""",

    "cloze_json": """Generate ONE cloze flashcard as JSON:
{"front": "sentence with {{c1::hidden}}", "back": "", "type": "cloze"}

Generate from:""",
}