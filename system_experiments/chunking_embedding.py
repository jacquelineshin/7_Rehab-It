#!/usr/bin/env python
# coding: utf-8

# In[13]:


import argparse
import gc
import hashlib
import re
import time

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ settings
DATA_PATH = "exercises.csv"
OUTPUT_PATH = "system_results.csv"
TOP_K = 3                      # how many chunks are retrieved for each query

# 3 embedding models of different sizes (different vector dimensions)
EMBEDDERS = [
    ("sentence-transformers/all-MiniLM-L6-v2", 384),
    ("BAAI/bge-base-en-v1.5", 768),
    ("BAAI/bge-large-en-v1.5", 1024),
]
# bge models work better when the query starts with this instruction
QUERY_PREFIX = {"BAAI/bge-base-en-v1.5": "Represent this sentence for searching relevant passages: ",
                "BAAI/bge-large-en-v1.5": "Represent this sentence for searching relevant passages: "}

# 3 chunking strategies
CHUNKERS = ["record", "sentence", "fixed"]
FIXED_SIZE = 400               # characters per chunk for the "fixed" strategy
FIXED_OVERLAP = 80             # characters shared between neighbouring fixed chunks

GENERATOR = "Qwen/Qwen2.5-0.5B-Instruct"   # the small model chosen in Part 1
MAX_NEW_TOKENS = 150

QUERIES = [
    "Gentle stretches for a stiff lower back",
    "Exercises I can do at home without any equipment",
    "How do I strengthen my shoulder after surgery?",
    "Low-impact exercise to build leg strength",
    "My hip hurts when I walk. What exercises might help?",
]

# Optional: words that SHOULD appear in a good top-3 result, to help you score.
# Example: {"Gentle stretches for a stiff lower back": ["back", "stretch"]}
EXPECTED_KEYWORDS = {}


# ------------------------------------------------------------------ data
def load_records(path):
    """Return a list of {"source", "text"} records, one per exercise or paragraph."""
    if path.endswith(".txt"):
        raw = open(path, encoding="utf-8").read()
        paras = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
        return [{"source": f"paragraph {i + 1}", "text": p} for i, p in enumerate(paras)]
    df = pd.read_csv(path)
    records = []
    for _, r in df.iterrows():
        text = f"{r['name']}: {r['description']} (Difficulty {r['difficulty']} of 5)"
        records.append({"source": str(r["name"]), "text": text})
    return records


# ------------------------------------------------------------------ chunking
def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def make_chunks(records, strategy):
    """Return a list of {"source", "text"} chunks for one chunking strategy."""
    if strategy == "record":          # one chunk per exercise / paragraph (whole record)
        return [dict(r) for r in records]
    if strategy == "sentence":        # one chunk per sentence (small, loses the exercise name)
        return [{"source": r["source"], "text": s}
                for r in records for s in split_sentences(r["text"])]
    if strategy == "fixed":           # fixed-size windows over the whole corpus (can cut records apart)
        corpus = "\n".join(r["text"] for r in records)
        chunks, start = [], 0
        while start < len(corpus):
            piece = corpus[start:start + FIXED_SIZE].strip()
            if piece:
                chunks.append({"source": "corpus", "text": piece})
            start += FIXED_SIZE - FIXED_OVERLAP
        return chunks
    raise ValueError(strategy)


# ------------------------------------------------------------------ embedding
class HashEmbedder:
    """Tiny stand-in used only by --dry-run so the pipeline can be tested offline."""
    def __init__(self, dim):
        self.dim = dim

    def encode(self, texts, normalize_embeddings=True):
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in re.findall(r"[a-z]+", t.lower()):
                out[i, int(hashlib.md5(w.encode()).hexdigest(), 16) % self.dim] += 1
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.maximum(norms, 1e-9)


def load_embedder(name, dim, dry_run):
    if dry_run:
        return HashEmbedder(dim)
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


def retrieve(embedder, index, chunks, query, prefix):
    start = time.perf_counter()
    q = embedder.encode([prefix + query], normalize_embeddings=True)[0]
    scores = index @ q
    top = np.argsort(-scores)[:TOP_K]
    results = [(chunks[i], float(scores[i])) for i in top]
    return results, time.perf_counter() - start


# ------------------------------------------------------------------ generation
def load_generator(dry_run):
    if dry_run:
        return None
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float32 if device == "cpu" else torch.float16
    tok = AutoTokenizer.from_pretrained(GENERATOR)
    model = AutoModelForCausalLM.from_pretrained(GENERATOR, torch_dtype=dtype).to(device)
    model.eval()
    return tok, model, device


def generate_answer(gen, query, retrieved):
    if gen is None:
        return "[dry run: generation skipped]", 0.0
    import torch
    tok, model, device = gen
    context = "\n".join(f"- {c['text']}" for c, _ in retrieved)
    messages = [
        {"role": "system", "content": "Answer the question using only the context. "
                                      "If the context does not help, say you do not know."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt").to(device)
    start = time.perf_counter()
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    seconds = time.perf_counter() - start
    text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    return text, seconds


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="test the pipeline without downloading models")
    args, _ = ap.parse_known_args()   # ignores extra arguments added by Jupyter/IPython

    records = load_records(DATA_PATH)
    print(f"Loaded {len(records)} records from {DATA_PATH}")
    gen = load_generator(args.dry_run)
    if gen is not None:                       # warm-up so the first timing is not inflated
        generate_answer(gen, "warm up", [({"text": "warm up"}, 0.0)])

    rows = []
    for name, dim in EMBEDDERS:
        embedder = load_embedder(name, dim, args.dry_run)
        embedder.encode(["warm up"], normalize_embeddings=True)
        prefix = QUERY_PREFIX.get(name, "")
        for strategy in CHUNKERS:
            chunks = make_chunks(records, strategy)
            t0 = time.perf_counter()
            index = np.asarray(embedder.encode([c["text"] for c in chunks], normalize_embeddings=True))
            index_seconds = time.perf_counter() - t0
            print(f"{name} | {strategy}: {len(chunks)} chunks, index built in {index_seconds:.2f}s")
            for query in QUERIES:
                retrieved, r_time = retrieve(embedder, index, chunks, query, prefix)
                answer, g_time = generate_answer(gen, query, retrieved)
                shown = "\n".join(f"[{i + 1}] (score {s:.2f}) {c['text']}" for i, (c, s) in enumerate(retrieved))
                kws = EXPECTED_KEYWORDS.get(query)
                hit = "" if not kws else ("Yes" if any(k.lower() in shown.lower() for k in kws) else "No")
                rows.append({
                    "Embedding Model": name,
                    "Embedding Dimensions": dim,
                    "Chunking Strategy": strategy,
                    "Number of Chunks": len(chunks),
                    "Query": query,
                    "Retrieved Chunks (top 3)": shown,
                    "Answer": answer,
                    "Retrieval Latency (s)": round(r_time, 4),
                    "Generation Latency (s)": round(g_time, 2),
                    "Total Latency (s)": round(r_time + g_time, 2),
                    "Index Build Time (s)": round(index_seconds, 2),
                    "Expected keyword in top 3?": hit,
                    "Retrieved Context Quality (1-10)": "",
                    "Answer Quality (1-10)": "",
                    "Notes": "",
                })
        del embedder
        gc.collect()

    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Saved {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

