import re

def chunk_text(text: str, chunk_size: int = 500) -> list:
    """
    Chunk text into pieces no larger than chunk_size.
    Prefer splitting at sentence boundaries. If a single sentence exceeds
    chunk_size, split it into smaller pieces. Uses a small overlap between
    chunks to preserve context.
    """

    if not text:
        return []

    # normalize whitespace/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []

    # simple sentence splitter (keeps punctuation)
    sentences = re.split(r'(?<=[\.\?\!])\s+', text)

    overlap = min(50, max(0, chunk_size // 10))  # ~10% overlap, capped
    chunks = []
    current = ""

    def flush_current():
        nonlocal current
        if current:
            chunks.append(current.strip())
            current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        # If adding the sentence stays within size, append it
        if len(current) + (1 if current else 0) + len(sent) <= chunk_size:
            current = (current + " " + sent).strip() if current else sent
            continue

        # Otherwise, flush current chunk and start a new one.
        if current:
            flush_current()

        # If the sentence itself is small enough, start new chunk with it
        if len(sent) <= chunk_size:
            # start with an overlap from previous chunk if available
            if chunks and overlap > 0:
                prefix = chunks[-1][-overlap:]
                current = (prefix + " " + sent).strip()
            else:
                current = sent
            # if current now exceeds chunk_size due to prefix, handle below
        else:
            # Sentence longer than chunk_size: split it into pieces
            start = 0
            step = chunk_size - overlap if chunk_size > overlap else chunk_size
            while start < len(sent):
                part = sent[start:start + chunk_size]
                chunks.append(part.strip())
                start += step
            current = ""

    # final flush
    if current:
        flush_current()

    return chunks
