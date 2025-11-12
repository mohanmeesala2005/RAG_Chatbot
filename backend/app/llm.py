import os
import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# Try imports for OpenAI and Google Generative AI (Gemini)
try:
    import openai  # type: ignore
except Exception:
    openai = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore


def _build_prompt(question: str, context: List[str]) -> str:
    """Build a single prompt string from question and context chunks."""
    if not context:
        return f"Question: {question}\n\nContext: (none provided)"
    chunks = "\n\n---\n\n".join(f"Chunk {i+1}:\n{c}" for i, c in enumerate(context))
    prompt = (
        "You are a helpful assistant. Answer the user's question using ONLY the information "
        "provided in the Context below. If the answer cannot be found in the Context, say "
        "\"I don't know.\" Do not invent facts or guess.\n\n"
        f"Context:\n{chunks}\n\nQuestion: {question}\n\nAnswer:"
    )
    return prompt


def generate_answer(question: str, context: List[str]) -> str:
    """
    Generate an answer to `question` using `context` (list of text chunks).
    Priority:
      1. If GOOGLE_API_KEY (or GEMINI_API_KEY) present and google.generativeai available -> use Gemini
      2. Else if OPENAI_API_KEY present and openai available -> use OpenAI
      3. Else deterministic fallback response.
    """
    prompt = _build_prompt(question, context)

    # 1) Try Gemini via google.generativeai if configured
    gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if genai is not None and gemini_key:
        try:
            # configure the library with api key
            genai.configure(api_key=gemini_key)
            # model choice can be adjusted; 'gemini-consult' / 'gemini-pro' names vary by account
            model_name = os.environ.get("GEMINI_MODEL", "models/text-bison-001")
            # Use chat-style API if available; fall back to simple generate
            # Try chat-style API first if present
            if hasattr(genai, "chat") and hasattr(genai.chat, "create"):
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that answers based on provided context."},
                    {"role": "user", "content": prompt},
                ]
                resp = genai.chat.create(model=model_name, messages=messages)
            else:
                # fallback to generate_text
                resp = genai.generate_text(model=model_name, prompt=prompt, temperature=0.0, max_output_tokens=512)

            # extract text from response (handle multiple shapes)
            def _extract_genai_text(r):
                try:
                    # hasattr candidates
                    if hasattr(r, "candidates") and r.candidates:
                        cand = r.candidates[0]
                        if hasattr(cand, "content"):
                            return cand.content
                        if hasattr(cand, "text"):
                            return cand.text
                    # dict-like
                    if isinstance(r, dict):
                        cands = r.get("candidates") or r.get("outputs")
                        if cands:
                            first = cands[0]
                            if isinstance(first, dict):
                                return first.get("content") or first.get("text") or first.get("output")
                    # fallback to str
                    return str(r)
                except Exception:
                    return str(r)

            extracted = _extract_genai_text(resp)
            if extracted:
                return extracted.strip()
            return str(resp)
        except Exception as e:
            logger.exception("Gemini request failed, will try OpenAI if available: %s", e)

    # 2) Try OpenAI if configured
    api_key = os.environ.get("OPENAI_API_KEY")
    if openai is not None and api_key:
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers based on provided context."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=512,
            )
            text = response["choices"][0]["message"]["content"].strip()
            return text
        except Exception as e:
            logger.exception("OpenAI request failed: %s", e)

    # 3) Fallback deterministic behavior
    if not context:
        return "I don't know. No context was provided to answer the question."

    # If an LLM wasn't available, provide a simple extractive/synthetic answer from the chunks
    def _chunk_to_text(ch):
        if isinstance(ch, str):
            return ch
        if isinstance(ch, dict):
            for key in ("text", "content", "page_content", "body"):
                if key in ch and isinstance(ch[key], str):
                    return ch[key]
            # fallback to any string field
            for v in ch.values():
                if isinstance(v, str):
                    return v
            return str(ch)
        return str(ch)

    texts = [_chunk_to_text(c) for c in context]

    # Simple extractive answer: try to find sentences that mention key terms from the question
    q_tokens = [t.lower() for t in re.findall(r"\w+", question)]
    gathered = []
    for t in texts:
        # split into sentences
        sents = re.split(r'(?<=[\.!?])\s+', t)
        for s in sents:
            low = s.lower()
            if any(q in low for q in q_tokens):
                gathered.append(s.strip())
        if len(gathered) >= 3:
            break

    if not gathered:
        # nothing matched: return the first couple of chunks as a summary
        take = min(2, len(texts))
        excerpt = "\n\n".join(texts[:take])
        return f"Based on the provided context (excerpt):\n\n{excerpt}"

    # assemble extracted sentences into a short answer
    answer = " ".join(gathered[:5])
    return f"Based on the provided context: {answer}"
