import torch
import numpy as np

from functools import lru_cache
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

from .models import Exercise


@lru_cache(maxsize=1)
def load_embedding_model():
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )


@lru_cache(maxsize=1)
def load_generation_model():
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32
    )

    model = model.to("cpu")
    model.eval()

    return tokenizer, model


def retrieve_exercises(query, top_k=3):
    exercises = list(
        Exercise.objects.all().values(
            "name", "description", "difficulty"
        )
    )

    if not exercises:
        return []

    documents = [
        f"{ex['name']}. {ex['description']}. "
        f"Difficulty: {ex['difficulty']}"
        for ex in exercises
    ]

    embedder = load_embedding_model()

    document_embeddings = embedder.encode(
        documents,
        normalize_embeddings=True
    )

    query_embedding = embedder.encode(
        [query],
        normalize_embeddings=True
    )[0]

    similarities = document_embeddings @ query_embedding

    top_indices = np.argsort(similarities)[::-1]

    beginner_terms = ["beginner", "easy", "low difficulty"]

    if any(term in query.lower() for term in beginner_terms):
        beginner_indices = [
            i for i in top_indices
            if exercises[i]["difficulty"] <= 3
        ]

        if beginner_indices:
            return [exercises[i] for i in beginner_indices[:top_k]]

    return [exercises[i] for i in top_indices[:top_k]]


def generate_exercise_response(query):
    print("STEP 1: Starting AI request", flush=True)

    exercises = retrieve_exercises(query)
    print("RETRIEVED EXERCISES:", exercises, flush=True)
    print("STEP 2: Exercise retrieval finished", flush=True)

    if not exercises:
        return "No exercises are currently available."

    context = "\n\n".join(
        f"Exercise: {ex['name']}\n"
        f"Description: {ex['description']}\n"
        f"Difficulty: {ex['difficulty']}"
        for ex in exercises
    )

    print("STEP 3: Loading Qwen model", flush=True)

    tokenizer, model = load_generation_model()

    print("STEP 4: Qwen model loaded", flush=True)

    messages = [
        {
            "role": "system",
            "content": (
                "You are Rehab-It's exercise information assistant. "
                "Only discuss exercises provided in the context. "
                "Do not diagnose conditions or promise recovery. "
                "Do not recommend exercising through sharp pain. "
                "For recent surgery, serious symptoms, or uncertain "
                "restrictions, advise consulting a qualified clinician. "
                "If the context is insufficient, say so."
            )
        },
        {
            "role": "user",
            "content": (
                f"Exercise information:\n{context}\n\n"
                f"Question: {query}\n\n"
                "Answer the user's question using only the exercise information provided. "
                "Consider both the user's requested difficulty level and the difficulty "
                "values of the retrieved exercises. "
                "For beginner requests, prefer lower-difficulty exercises. "
                "Do not assume the first retrieved exercise is the best recommendation. "
                "Recommend up to two suitable exercises by name and briefly explain "
                "how to perform them using their provided descriptions. "
                "Do not invent exercise instructions or claim an exercise is easy "
                "if its description indicates it requires advanced strength or balance. "
                "Keep the answer concise and complete."
            )
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1536
    )

    print("STEP 5: Generating answer", flush=True)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=180,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    print("STEP 6: Answer generated", flush=True)

    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    return tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    )