import re
from abc import ABC, abstractmethod
from .schema import Chunk

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, content: str) -> list[Chunk]:
        pass

class ChunkByHeader(BaseChunker):
    def __init__(self):
        pass

    def chunk(self, content: str) -> list[Chunk]:
        """Split markdown by headers."""
        sections = re.split(r'(?=^#{1,4} )', content, flags=re.MULTILINE)

        chunks = []
        for section in sections:
            section = section.strip()
            if len(section.split()) < 20:
                continue

            header_match = re.match(r'^(#{1,4} .+)$', section, re.MULTILINE)
            header = header_match.group(1) if header_match else None

            chunks.append(Chunk(content=section, header=header, level="header"))

        return chunks if chunks else [Chunk(content=content)]


# OLD
# def chunk_by_headers(content: str) -> list[Chunk]:
#     """Split markdown by headers."""
#     sections = re.split(r'(?=^#{1,4} )', content, flags=re.MULTILINE)
#
#     chunks = []
#     for section in sections:
#         section = section.strip()
#         if len(section.split()) < 20:
#             continue
#
#         header_match = re.match(r'^(#{1,4} .+)$', section, re.MULTILINE)
#         header = header_match.group(1) if header_match else None
#
#         chunks.append(Chunk(content=section, header=header, level="header"))
#
#     return chunks if chunks else [Chunk(content=content)]

class ChunkByParagraph(BaseChunker):
    def __init__(self, max_words:int, header: str | None = None):
        self.max_words = max_words
        self.header = header

    def chunk(self, content: str) -> list[Chunk]:
        """Split content into paragraphs up to max_words."""
        paragraphs = content.split('\n\n')  # Split by double newline
        chunks = []
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len((current + " " + para).split()) <= self.max_words:
                current += "\n\n" + para if current else para
            else:
                if current.strip():
                    chunks.append(Chunk(
                        content=current.strip(),
                        header=self.header,
                        level="paragraph"
                    ))
                current = para

        if current.strip():
            chunks.append(Chunk(
                content=current.strip(),
                header=self.header,
                level="paragraph"
            ))

        return chunks if chunks else [Chunk(content=content, header=self.header)]

# OLD
# def chunk_by_paragraphs(chunk: Chunk, max_words: int = 300) -> list[Chunk]:
#     """Split a chunk into paragraphs if too long."""
#     if len(chunk.content.split()) <= max_words:
#         return [chunk]
#
#     paragraphs = chunk.content.split('\n\n')
#     chunks = []
#     current = ""
#
#     for para in paragraphs:
#         if len((current + para).split()) <= max_words:
#             current += "\n\n" + para
#         else:
#             if current.strip():
#                 chunks.append(Chunk(
#                     content=current.strip(),
#                     header=chunk.header,
#                     level="paragraph"
#                 ))
#             current = para
#
#     if current.strip():
#         chunks.append(Chunk(
#             content=current.strip(),
#             header=chunk.header,
#             level="paragraph"
#         ))
#
#     return chunks if chunks else [chunk]

class ChunkHeaderThenParagraph(BaseChunker):
    def __init__(self, max_words: int = 300):
        self.header_chunker = ChunkByHeader()
        self.paragraph_chunker = ChunkByParagraph(max_words=max_words)
        self.max_words = max_words

    def chunk(self, content: str) -> list[Chunk]:
        """
        Hierarchical chunking:
        1. Split by headers
        2. Split long sections by paragraphs
        """
        header_chunks = self.header_chunker.chunk(content)

        final_chunks = []
        for chunk in header_chunks:
            if len(chunk.content.split()) > self.max_words:
                # Pass header to paragraph chunker
                self.paragraph_chunker.header = chunk.header
                sub_chunks = self.paragraph_chunker.chunk(chunk.content)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)

        return final_chunks

# OLD
# def chunk_header_then_paragraph(content: str, max_words: int = 300) -> list[Chunk]:
#     """
#     Hierarchical chunking:
#     1. Split by headers
#     2. Split long sections by paragraphs
#     """
#     # Level 1: Headers
#     header_chunks = chunk_by_headers(content)
#
#     # Level 2: Paragraphs (if needed)
#     final_chunks = []
#     for chunk in header_chunks:
#         final_chunks.extend(chunk_by_paragraphs(chunk, max_words))
#
#     return final_chunks

class ChunkByLength(BaseChunker):
    def __init__(self, max_words: int = 300, overlap: int = 25, header: str | None = None):
        self.max_words = max_words
        self.overlap = min(overlap, max_words // 2)
        self.header = header

    def chunk(self, content: str) -> list[Chunk]:
        words = content.split()

        if len(words) <= self.max_words:
            return [Chunk(
                        content=content,
                        header=self.header,
                        level="length"
                    )]

        chunks = []
        start = 0

        while start < len(words):
            end = min(start + self.max_words, len(words))
            single_content = " ".join(words[start:end])
            chunks.append(Chunk(
                content=single_content,
                header=self.header,
                level="length"
            ))

            # Stop if we've reached the end
            if end >= len(words):
                break

            start = end - self.overlap  # Overlap with previous chunk

        return chunks

# OLD
# def chunk_by_length(content: str, max_words: int = 300, overlap: int = 50) -> list[str]:
#     """Split content into same sized chunks."""
#     words = content.split()
#
#     if len(words) <= max_words:
#         return [content]
#
#     chunks = []
#     start = 0
#
#     while start < len(words):
#         end = start + max_words
#         chunk = " ".join(words[start:end])
#         chunks.append(chunk)
#         start = end - overlap  # Overlap with previous chunk
#
#     return chunks