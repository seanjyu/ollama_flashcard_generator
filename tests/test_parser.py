# Make sure that pytest is installed

from flashcard_gen.parser import parse_flashcards

class TestParseFlashcards:
    """Tests for parse_flashcards function."""

    def test_valid_json_array(self):
        raw = '[{"front": "What is X?", "back": "Y", "type": "basic"}]'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 1
        assert len(errors) == 0
        assert cards[0].front == "What is X?"
        assert cards[0].back == "Y"

    def test_multiple_cards(self):
        raw = '''[
            {"front": "Q1?", "back": "A1", "type": "basic"},
            {"front": "Q2?", "back": "A2", "type": "basic"}
        ]'''
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 2

    def test_markdown_fence(self):
        raw = '```json\n[{"front": "Q?", "back": "A", "type": "basic"}]\n```'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 1

    def test_markdown_fence_no_language(self):
        raw = '```\n[{"front": "Q?", "back": "A", "type": "basic"}]\n```'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 1

    def test_preamble_text(self):
        raw = 'Here are the flashcards:\n[{"front": "Q?", "back": "A", "type": "basic"}]'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 1

    def test_trailing_comma(self):
        raw = '[{"front": "Q?", "back": "A", "type": "basic"},]'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 1

    def test_single_object_wrapped(self):
        raw = '{"front": "Q?", "back": "A", "type": "basic"}'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 1

    def test_invalid_json_returns_error(self):
        raw = 'not json at all'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 0
        assert len(errors) == 1
        assert "No JSON found" in errors[0]

    def test_malformed_json_returns_error(self):
        raw = '[{"front": "Q?", "back": ]'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 0
        assert "Invalid JSON" in errors[0]

    def test_skips_invalid_cards(self):
        raw = '''[
            {"front": "Valid?", "back": "Yes", "type": "basic"},
            {"front": "", "back": "Empty front", "type": "basic"},
            {"front": "Also valid?", "back": "Yes", "type": "basic"}
        ]'''
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 2
        assert len(errors) == 1

    def test_empty_back_for_basic_fails(self):
        raw = '[{"front": "Q?", "back": "", "type": "basic"}]'
        cards, errors = parse_flashcards(raw)
        assert len(cards) == 0
        assert len(errors) == 1