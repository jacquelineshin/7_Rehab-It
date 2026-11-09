
import argparse
import random
import statistics
import time

import numpy as np
import pandas as pd

from chunking_embedding import QUERIES, QUERY_PREFIX, TOP_K, load_embedder, load_records, make_chunks

EXERCISES = "exercises.csv"
ADDED = "additional_exercises.csv"
EXTRA = "extra_exercises_for_scaling.csv"

EMBEDDERS = [                                   # add ("BAAI/bge-large-en-v1.5", 1024) if memory allows
    ("sentence-transformers/all-MiniLM-L6-v2", 384),
    ("BAAI/bge-base-en-v1.5", 768),
]
REPEATS = 5                                     # each retrieval is timed this many times; the median is reported

# Answer key: exercises that count as relevant for each query (the rest of the top 3 counts as noise)
RELEVANT = {
    QUERIES[0]: ["Pelvic Tilt", "Knee-to-Chest Stretch", "Cat-Cow Stretch", "Child's Pose", "Seated Lower Back Rotation Stretch"],
    QUERIES[2]: ["Pendulum Swing", "Isometric Shoulder External Rotation", "Wall Slide", "Band External Rotation", "Scapular Squeeze"],
    QUERIES[3]: ["Chair Squat", "Straight Leg Raise", "Wall Sit", "Step-Up", "Calf Raise", "Stationary Bike"],
    QUERIES[4]: ["Clamshell", "Side-Lying Leg Lift", "Standing Hip Abduction", "Hip Flexor Stretch", "Figure-4 Stretch"],
}
# Query 2 (equipment-free) is judged by what the description says
KEYWORD_RULE = {QUERIES[1]: ["no equipment", "only your body weight"]}
# Look-alike exercises that should NOT rank first (counted separately as "distractors")
TRAPS = {
    QUERIES[0]: ["Plank", "Dead Bug"],
    QUERIES[2]: ["Push-Up", "Plank", "Overhead Dumbbell Press"],
    QUERIES[3]: ["Jump Squat", "Burpee", "Single-Leg Squat", "Bulgarian Split Squat"],
    QUERIES[4]: ["Hip Hinge", "Reverse Lunge"],
}


def is_relevant(query, chunk):
    if query in KEYWORD_RULE:
        text = chunk["text"].lower()
        return any(k in text for k in KEYWORD_RULE[query])
    return chunk["source"] in RELEVANT.get(query, [])


def build_datasets():
    full = load_records(EXERCISES)
    try:
        added_names = set(pd.read_csv(ADDED)["name"].astype(str))
        small = [r for r in full if r["source"] not in added_names]
    except FileNotFoundError:
        small = full[:10]
    small_random = random.Random(42).sample(full, 20)
    extra = load_records(EXTRA)
    return {"small_original": small, "small_random20": small_random, "medium": full, "large": full + extra}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args, _ = ap.parse_known_args()

    datasets = build_datasets()
    print({k: len(v) for k, v in datasets.items()})
    rows = []
    for name, dim in EMBEDDERS:
        embedder = load_embedder(name, dim, args.dry_run)
        embedder.encode(["warm up"], normalize_embeddings=True)
        prefix = QUERY_PREFIX.get(name, "")
        for ds_name, records in datasets.items():
            chunks = make_chunks(records, "record")
            index = np.asarray(embedder.encode([c["text"] for c in chunks], normalize_embeddings=True))
            for query in QUERIES:
                times = []
                for _ in range(REPEATS):
                    t0 = time.perf_counter()
                    q = embedder.encode([prefix + query], normalize_embeddings=True)[0]
                    scores = index @ q
                    top = np.argsort(-scores)[:TOP_K]
                    times.append(time.perf_counter() - t0)
                got = [chunks[i] for i in top]
                rel = [is_relevant(query, c) for c in got]
                first = next((i + 1 for i, r in enumerate(rel) if r), None)
                traps = [c["source"] for c in got if c["source"] in TRAPS.get(query, [])]
                rows.append({
                    "Dataset": ds_name, "Dataset Size": len(chunks),
                    "Embedding Model": name, "Query": query,
                    "Top 3 Retrieved": " | ".join(f"{c['source']} ({scores[i]:.2f})" for c, i in zip(got, top)),
                    "Relevant in Top 3": sum(rel),
                    "Precision@3": round(sum(rel) / TOP_K, 2),
                    "Found a Relevant Result (Hit@3)": int(any(rel)),
                    "Rank of First Relevant": first if first else "none",
                    "Noise (irrelevant in Top 3)": TOP_K - sum(rel),
                    "Look-alike Distractors in Top 3": ", ".join(traps),
                    "Top-1 Similarity": round(float(scores[top[0]]), 3),
                    "Retrieval Latency (s, median)": round(statistics.median(times), 4),
                })
        del embedder

    df = pd.DataFrame(rows)
    df.to_csv("part2_scaling_results.csv", index=False, encoding="utf-8-sig")
    summary = (df.groupby(["Embedding Model", "Dataset"], sort=False)
                 .agg(Dataset_Size=("Dataset Size", "first"),
                      Avg_Precision_at_3=("Precision@3", "mean"),
                      Hit_Rate=("Found a Relevant Result (Hit@3)", "mean"),
                      Avg_Noise_per_Query=("Noise (irrelevant in Top 3)", "mean"),
                      Avg_Top1_Similarity=("Top-1 Similarity", "mean"),
                      Median_Latency_s=("Retrieval Latency (s, median)", "median"))
                 .round(3).reset_index())
    summary.to_csv("part2_scaling_summary.csv", index=False)
    print(summary.to_string(index=False))
    print("Saved part2_scaling_results.csv and part2_scaling_summary.csv")


if __name__ == "__main__":
    main()
