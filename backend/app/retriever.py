from typing import List
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

_CHUNKS = []

def store_chunks(chunks: list):
    global _CHUNKS
    _CHUNKS = chunks

def _extract_text(chunk) -> str:
    if isinstance(chunk, str):
        return chunk
    if isinstance(chunk, dict):
        for key in ("text", "content", "page_content", "body"):
            if key in chunk and isinstance(chunk[key], str):
                return chunk[key]
        # fall back to any stringifiable fields
        for v in chunk.values():
            if isinstance(v, str):
                return v
        return str(chunk)
    return str(chunk)

def retrieve_relevant_chunks(query: str, top_k: int = 5) -> List:
    """
    Return the top_k most relevant chunks for the query.
    Tries to use sklearn's TF-IDF + cosine similarity; if sklearn isn't available,
    falls back to a simple token-overlap scoring.
    Returned items preserve the original chunk objects (string or dict).
    """
    if not _CHUNKS:
        return []

    texts = [_extract_text(c) for c in _CHUNKS]

    # Try TF-IDF + cosine similarity first
    try:

        vectorizer = TfidfVectorizer(stop_words="english")
        doc_mat = vectorizer.fit_transform(texts)
        query_vec = vectorizer.transform([query])
        # cosine similarity via dot product since vectors are L2-normalized by default in Tfidf
        sims = (doc_mat @ query_vec.T).toarray().ravel()
        if np.all(sims == 0):
            # no overlap found; fall back to token scoring below
            raise ValueError("Empty TF-IDF similarities")
        ranked_idx = list(np.argsort(-sims))
    except Exception:
        # Fallback: simple token overlap scoring
        def _tokens(s: str):
            return set(re.findall(r"\w+", s.lower()))
        q_tokens = _tokens(query)
        scores = []
        for t in texts:
            dt = _tokens(t)
            scores.append(len(q_tokens & dt))
        # sort by score desc, then by original order
        ranked_idx = sorted(range(len(scores)), key=lambda i: (-scores[i], i))

    # Build result preserving original chunk structure
    selected = []
    for i in ranked_idx:
        if len(selected) >= top_k:
            break
        selected.append(_CHUNKS[i])

    return selected
