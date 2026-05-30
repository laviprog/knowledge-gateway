import hashlib
import re
from itertools import pairwise

MARKDOWN_HEADING_PATTERN = re.compile(r"(?m)(?=^#{1,6}\s+)")


def hash_content(content: str) -> str:
    """
    Build a stable content hash.
    """
    return hashlib.sha256(content.encode()).hexdigest()


def split_document_content(
    content: str,
    max_chars: int,
    overlap_chars: int,
) -> list[str]:
    """
    Split document content into markdown-aware chunks.
    """
    normalized_content = content.strip()
    if not normalized_content:
        return []

    blocks = split_content_blocks(normalized_content)
    chunks = merge_blocks_into_chunks(blocks, max_chars=max_chars)
    return add_chunk_overlap(chunks, overlap_chars=overlap_chars)


def split_content_blocks(content: str) -> list[str]:
    """
    Split content into markdown sections and paragraphs.
    """
    blocks: list[str] = []
    for section in MARKDOWN_HEADING_PATTERN.split(content):
        section = section.strip()
        if not section:
            continue

        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", section)]
        blocks.extend(paragraph for paragraph in paragraphs if paragraph)

    return blocks


def merge_blocks_into_chunks(blocks: list[str], max_chars: int) -> list[str]:
    """
    Merge content blocks into bounded chunks.
    """
    chunks: list[str] = []
    current_chunk = ""

    for block in blocks:
        if len(block) > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            chunks.extend(split_large_block(block, max_chars=max_chars))
            continue

        next_chunk = join_chunk_parts(current_chunk, block)
        if current_chunk and len(next_chunk) > max_chars:
            chunks.append(current_chunk)
            current_chunk = block
        else:
            current_chunk = next_chunk

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def split_large_block(block: str, max_chars: int) -> list[str]:
    """
    Split a large block into bounded chunks.
    """
    return [block[index : index + max_chars].strip() for index in range(0, len(block), max_chars)]


def add_chunk_overlap(chunks: list[str], overlap_chars: int) -> list[str]:
    """
    Add trailing context from previous chunks.
    """
    if overlap_chars <= 0:
        return chunks

    overlapped_chunks = [chunks[0]] if chunks else []
    for previous_chunk, chunk in pairwise(chunks):
        overlap = previous_chunk[-overlap_chars:].strip()
        overlapped_chunks.append(join_chunk_parts(overlap, chunk))

    return overlapped_chunks


def join_chunk_parts(first_part: str, second_part: str) -> str:
    """
    Join chunk parts with paragraph spacing.
    """
    if not first_part:
        return second_part
    return f"{first_part}\n\n{second_part}"
