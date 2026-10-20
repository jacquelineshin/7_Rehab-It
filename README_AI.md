# Rehab-It AI Features

We added two AI features (you have to be logged in to use them). The code is in `rehab/aiViews.py`.

1. **Ask Rehab-It** (`/ai/ask/`) - answers exercise and recovery questions using a local Hugging Face model,
   `Qwen/Qwen2.5-1.5B-Instruct`. We picked it because it scored the best in our notebook.
2. **Exercise Coach** (`/ai/coach/`) - gives tips on how to do an exercise from our database safely, using the
   Groq API (`llama-3.1-8b-instant`).

## Data Input

- Ask Rehab-It: the user types a question in a text box (max 500 characters).
- Exercise Coach: the user picks an exercise from a dropdown and can add a short note. The exercise info comes
  from our database.

## Preprocessing

- We remove HTML tags and extra spaces from the user's text before sending it to a model.
- The local model gets a system prompt and two example answers (few-shot prompting worked best in our notebook).
- Groq gets a prompt with the exercise name, description and difficulty from our database.

## Safety Guardrails

- Empty or too long questions are rejected.
- Prompt injection phrases like "ignore previous instructions" are blocked.
- If someone mentions an emergency (like chest pain or trouble breathing), we tell them to see a doctor or
  call 911 instead of asking the model.
- Both models are told not to diagnose and to put safety first.
- If the local model gives a broken or empty answer, we show an error message instead.
- The Groq call has a timeout and handles errors like a bad API key or no internet.

## How to Run

1. `pip install -r requirements.txt`
2. Get a free API key from https://console.groq.com and add `GROQ_API_KEY=your-key-here` to your `.env` file.
3. `python manage.py runserver`

The first question takes about a minute because the model (about 3 GB) has to download and load. This only
runs locally since the model is too big for PythonAnywhere.
