import re

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Exercise


localModelName = "Qwen/Qwen2.5-1.5B-Instruct"
groqUrl = "https://api.groq.com/openai/v1/chat/completions"
groqModelName = "llama-3.1-8b-instant"
maxInputLength = 500

localTokenizer = None
localModel = None

blockedPhrases = [
    "ignore previous",
    "ignore all previous",
    "ignore the above",
    "disregard previous",
    "system prompt",
    "you are now",
    "pretend to be",
    "jailbreak",
    "developer mode",
]

emergencyWords = [
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "trouble breathing",
    "numbness",
    "can't feel",
    "fainted",
    "passed out",
    "heard a pop",
    "bone sticking",
    "suicide",
]

emergencyMessage = (
    "This sounds like it could be serious. Please stop exercising and contact a doctor right away, "
    "or call 911 if it is an emergency. Rehab-It can't help with this."
)

systemPrompt = (
    "You are an assistant for Rehab-It!, an exercise recovery application. "
    "Give general information, do not diagnose injuries, and prioritize safety. "
    "Use clear, concise language. Always answer with these three sections: "
    "Recommendation, What to do, When to seek help."
)

examples = [
    {
        "user": "My ankle feels mildly sore after a walk. What should I do?",
        "assistant": (
            "Recommendation: Take it easy and avoid activities that worsen pain.\n"
            "What to do: Rest, monitor symptoms, and return gradually when comfortable.\n"
            "When to seek help: Get medical advice if pain worsens, swelling is significant, "
            "or you cannot bear weight."
        ),
    },
    {
        "user": "My shoulder hurts when I lift weights. Should I continue?",
        "assistant": (
            "Recommendation: Stop the movement that causes pain.\n"
            "What to do: Rest the shoulder and avoid painful movements. Do not push through pain.\n"
            "When to seek help: See a doctor or physical therapist if pain worsens, limits movement, "
            "or does not improve after a few days."
        ),
    },
]


def cleanInput(text):
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def checkInput(text):
    if text == "":
        return "Please type a question."

    if len(text) > maxInputLength:
        return "Please keep your question under " + str(maxInputLength) + " characters."

    lowerText = text.lower()

    for phrase in blockedPhrases:
        if phrase in lowerText:
            return "Sorry, that question can't be answered. Please ask about exercise or recovery."

    return None


def isEmergency(text):
    lowerText = text.lower()

    for word in emergencyWords:
        if word in lowerText:
            return True

    return False


def cleanOutput(text):
    text = text.replace("<|im_end|>", "").replace("<|endoftext|>", "")
    text = text.strip()

    if "When to seek help:" in text:
        start = text.index("When to seek help:")
        end = text.find("\n", start)
        if end != -1:
            text = text[:end]

    return text.strip()


def checkOutput(text):
    if text == "":
        return False

    if "Recommendation:" not in text:
        return False

    return True


def loadLocalModel():
    global localTokenizer, localModel

    if localModel is None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        localTokenizer = AutoTokenizer.from_pretrained(localModelName)
        localModel = AutoModelForCausalLM.from_pretrained(localModelName, dtype="auto")

        if torch.backends.mps.is_available():
            localModel = localModel.to("mps")

    return localTokenizer, localModel


def askLocalModel(question):
    tokenizer, model = loadLocalModel()

    messages = [{"role": "system", "content": systemPrompt}]

    for example in examples:
        messages.append({"role": "user", "content": example["user"]})
        messages.append({"role": "assistant", "content": example["assistant"]})

    messages.append({"role": "user", "content": question})

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False,
        eos_token_id=tokenizer.convert_tokens_to_ids("<|im_end|>"),
    )

    newTokens = outputs[0][inputs["input_ids"].shape[1]:]
    answer = tokenizer.decode(newTokens, skip_special_tokens=True)

    return cleanOutput(answer)


def askGroq(prompt):
    if not settings.GROQ_API_KEY:
        return None, "The Groq API key is missing. Add GROQ_API_KEY to your .env file."

    headers = {
        "Authorization": "Bearer " + settings.GROQ_API_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "model": groqModelName,
        "messages": [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 300,
        "temperature": 0.3,
    }

    try:
        response = requests.post(groqUrl, headers=headers, json=body, timeout=15)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return None, "The AI service took too long to respond. Please try again."
    except requests.exceptions.HTTPError:
        return None, "The AI service returned an error (" + str(response.status_code) + "). Check the API key."
    except requests.exceptions.RequestException:
        return None, "Could not reach the AI service. Please try again later."
    except (KeyError, IndexError, ValueError):
        return None, "The AI service sent back something we couldn't read."

    answer = answer.replace("**", "").replace("#", "").strip()

    if answer == "":
        return None, "The AI service sent back an empty answer."

    return answer, None


@login_required
def askRehab(request):
    question = ""
    answer = None
    error = None

    if request.method == "POST":
        question = cleanInput(request.POST.get("question", ""))
        error = checkInput(question)

        if error is None:
            if isEmergency(question):
                answer = emergencyMessage
            else:
                try:
                    answer = askLocalModel(question)
                except Exception:
                    error = "The local AI model could not run. Please try again."

                if answer is not None and not checkOutput(answer):
                    answer = None
                    error = "The AI gave an answer we couldn't use. Please try asking in a different way."

    context = {
        "question": question,
        "answer": answer,
        "error": error,
        "modelName": localModelName,
    }

    return render(request, "rehab/askRehab.html", context)


@login_required
def exerciseCoach(request):
    exercises = Exercise.objects.all().order_by("name")
    selectedExercise = None
    note = ""
    answer = None
    error = None

    if request.method == "POST":
        exerciseId = request.POST.get("exercise", "")
        note = cleanInput(request.POST.get("note", ""))

        if exerciseId.isdigit():
            selectedExercise = Exercise.objects.filter(pk=exerciseId).first()

        if selectedExercise is None:
            error = "Please pick an exercise."
        elif note != "":
            error = checkInput(note)

        if error is None and isEmergency(note):
            answer = emergencyMessage
        elif error is None:
            prompt = (
                "Explain how to do this rehab exercise safely.\n"
                "Exercise: " + selectedExercise.name + "\n"
                "Description: " + selectedExercise.description + "\n"
                "Difficulty (1-10): " + str(selectedExercise.difficulty) + "\n"
            )

            if note != "":
                prompt = prompt + "User note: " + note + "\n"

            prompt = prompt + (
                "Answer with these sections: How to do it (3 short steps), "
                "Common mistakes, Easier version, When to stop. Keep it under 150 words."
            )

            answer, error = askGroq(prompt)

    context = {
        "exercises": exercises,
        "selectedExercise": selectedExercise,
        "note": note,
        "answer": answer,
        "error": error,
        "modelName": groqModelName,
    }

    return render(request, "rehab/exerciseCoach.html", context)
