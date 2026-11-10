# P1-A9 Part 3
## Step 3.1: Define 5 Realistic App Inputs

Test Cases
1. Normal request - "Give me a workout to strengthen my legs."
2. Specific request - "Give me a 20 minute upper-body workout."
3. Vague request - "Help me get in better shape."
4. Limited ability request - "Give me a low-impact workout without jumping."
5. Contradictory request - "Give me a high-intensity workout that is easy on my joints and doesn't involve any strenuous movements."

## Step 3.2: Evaluate Outputs

### Test Case 1

**Test Input:**

"Give me a workout to strengthen my legs."

**Expected Behavior:**

The model should recommend exercises and descriptions that will make the user's legs stronger.

**Actual Output:**

Recommendation: Incorporate leg exercises into your routine.

What to do: Choose exercises like squats, lunges, and calf raises.
When to seek help: Consult with a healthcare provider before starting any new exercise program.

**Quality Notes:**
- **Output Quality:** The response is clear and relevant.
- **Correctness/Usefulness:** The suggested exercises are correct because they are leg-strengthening exercises. The response could be more useful by including more instructions on how to perform the exercises and reps/sets.
- **Structure:** The structure is logical and organized.
- **Weaknesses:** The response is too general and lacked step-by-step information.

**Latency:** ~6.0 seconds

---

### Test Case 2

**Test Input:**

"Give me a 20 minute upper-body workout."

**Expected Behavior:**

The model shoud recommend upper body exercises and explain how to perform them so that the workout will take approximately 20 minutes.

**Actual Output:**

Recommendation: Warm up with light cardio (e.g., walking) for 5 minutes.

What to do: Perform exercises like squats, lunges, and arm curls to warm up your muscles.

When to seek help: After warming up, cool down with stretching and gentle foam rolling.

**Quality Notes:**
- **Output Quality:** Very low-quality response. The response was irrelevant to the prompt, as it recommended mostly lower-body exercises only including warm-ups and a cool-down.
- **Correctness/Usefulness:** The response was incorrect, as it recommended cardio and leg exercises instead of upper-body exercises. Additionally, it recommended the user to cool down after warming up, which does not make sense. This is not useful for the user.
- **Structure:** The structure is logical and organized.
- **Weaknesses:** Entirely missing information that would answer the request.

**Latency:** ~6.5 seconds

---

### Test Case 3

**Test Input:**

"Help me get in better shape."

**Expected Behavior:**

Provide general information about healthy habits.

**Actual Output:**

Recommendation: Exercise regularly, eat well, and maintain good posture.
What to do: Set realistic goals, choose appropriate exercises, and stay consistent with your routine.
When to seek help: Consider consulting a fitness professional for personalized guidance.

**Quality Notes:**
- **Output Quality:** The response is clear and relevant.
- **Correctness/Usefulness:** The response is accurate and provides useful general information. However, it lacks specific workout plans.
- **Structure:** The structure is logical and organized.
- **Weaknesses:** The model does not ask any follow-up questions to better understand the user's specific goals for more specific recommendations.

**Latency:** ~1.4 seconds

---

### Test Case 4

**Test Input:**

"Give me a low-impact workout without jumping."

**Expected Behavior:**

The model should provide low-impact exercises that don't include any jumps.

**Actual Output:**

Recommendation: Yoga
What to do: Practice gentle poses, focus on breathing, and listen to your body.
When to seek help: Consult with a healthcare provider before starting any new exercise program.

**Quality Notes:**
- **Output Quality:** The response is relevant because yoga is generally low-impact and does not involve jumping.
- **Correctness/Usefulness:** The recommendation makes sense and the guidelines are somewhat useful. However, it would be more useful if the model provided specific poses and how to perform them.
- **Structure:** The structure is logical and organized.
- **Weaknesses:** The recommendation is general and did not include any specific exercises.

**Latency:** ~1.2 seconds

---

### Test Case 5

**Test Input:**

"Give me a high-intensity workout that is easy on my joints and doesn't involve any strenuous movements."

**Expected Behavior:**

The model should recognize that the request is contradictory. If it is unable to ask follow-up questions, it should provide modifications to a usually high-intensity workout that would be easier on the joints.

**Actual Output:**

Recommendation: High-intensity interval training (HIIT) with short bursts of intense activity followed by periods of rest.

What to do: Start with 30 seconds of high-intensity activity like sprinting or jumping jacks, then switch to shorter intervals of moderate activity for 15-30 seconds, followed by another 15-30 seconds of rest.

When to seek help: Consult a healthcare provider before starting HIIT unless you have specific health concerns.

**Quality Notes:**
- **Output Quality:** The response is relevant to the high-intensity part of the request, but not the other parts.
- **Correctness/Usefulness:** The recommendations are not appropriate for the user's request because the workout would not be easy on their joints and does include strenuous movement.
- **Structure:** The structure is logical and organized.
- **Weaknesses:** The model failed to recognize the conflicting aspects of the request and only focused on the first part of the input.

**Latency:** ~3.0 seconds

## Step 3.3: Failure Analysis

### Failure Case 1: Test Case 2

Test Case 2 result in poor answer quality and an irrelevant response. The model did not follow the instructions in the request. The request specified an upper-body workout, and the generated response provided irrelevant exercises that were not for the upper-body. A possibility for the reason this error occurred is because the model failed to understand and accurately interpret the instructions, perhaps not recognizing the "upper-body" specification. Therefore, it could not properly follow these instructions in its generated response.

### Failure Case 2: Test Case 5

Test Case 5 resulted in poor answer quality and safety risk. The model failed to recognize and adhere to the user's restrictions provided in the request. It only focused on the first part of the request, "high-intensity workout," and ignored the rest. It did not understand that the request had conflicting aspects. This is not helpful for the user because the workout provided is not suitable for them, as they would have specified that they need workouts that are not strenuous. This could have happened because the model struggle to interpret multiple different constraints in the same request.

## Step 3.4: Improvement Attempt

I attempted to improve the response for the request in Test Case 2 through prompt improvement.

The original prompt was the following:

systemPrompt = (
    "You are Rehab-It's exercise and recovery assistant. "
    "Provide general exercise information, not medical diagnoses. "
    "Prioritize safety and never recommend exercising through pain. "
    "Always use EXACTLY these three headings, each followed by a short answer:\n"
    "Recommendation:\n"
    "What to do:\n"
    "When to seek help:\n"
    "Keep answers brief and use simple language. "
    "Do not invent detailed exercise instructions when uncertain. "
    "If you lack enough information, say so."
)

The revised prompt was the following:


systemPrompt = (
    "You are Rehab-It's exercise and recovery assistant. "
    "Provide general exercise information, not medical diagnoses. "
    "Prioritize safety and never recommend exercising through pain. "

    "Carefully follow ALL requirements in the user's question. "
    "Pay particular attention to the requested body area, workout "
    "duration, exercise type, intensity, and physical restrictions. "

    "For upper-body workouts, recommend upper-body exercises. "
    "For lower-body workouts, recommend lower-body exercises. "
    "Do not substitute unrelated exercises. "
    "Respect restrictions such as no jumping or low-impact movements. "
    "Never recommend exercises that contradict a user's restrictions. "

    "If the user's requirements conflict, ask a clarifying question "
    "instead of guessing. For example, high intensity and no strenuous "
    "movement may conflict, so clarify what the user means. "

    "When recommending a workout, provide specific relevant exercises "
    "and brief descriptions. Follow requested durations when possible. "
    "Do not invent detailed exercise instructions when uncertain. "

    "Your response MUST contain all three headings below. "
    "Never omit a heading, even if the answer is brief. "
    "Put the recommended workout under Recommendation. "
    "Put the exercises and instructions under What to do. "
    "Put appropriate safety guidance under When to seek help. "
    "Use the exact heading names and put each heading on its own line:\n"
    "Recommendation:\n"
    "What to do:\n"
    "When to seek help:\n"

    "Keep answers brief and use simple language. "
    "If you lack enough information, say so. "
    "Do not diagnose injuries or promise recovery."
)

The original generated response to the request "Give me a 20 minute upper-body workout" was the following:

Recommendation: Warm up with light cardio (e.g., walking) for 5 minutes.

What to do: Perform exercises like squats, lunges, and arm curls to warm up your muscles.

When to seek help: After warming up, cool down with stretching and gentle foam rolling.



The revised generated response to the same request was the following:

Recommendation: Warm up with some light cardio (e.g., walking) for 5 minutes.

What to do: Perform 10 reps of each exercise:

1. Push-ups - 3 sets of 8-12 reps
2. Dumbbell rows - 3 sets of 12-15 reps
3. Bicep curls - 3 sets of 12-15 reps
4. Tricep extensions - 3 sets of 12-15 reps

When to seek help: Ensure proper form and warm-up before starting any exercise routine. Consult a healthcare professional if there are any concerns about your fitness level or health history.



The output improved tremendously based on the improved prompt. The original response was incorrect and irrelevant to the request. The request was for an upper-body workout, and the model recommended mostly lower-body exercises without any specific instruction. On the other hand, the revised response provided arm exercises, which are relevant to the request of an upper-body workout. It also provided specific instructions on sets and reps of each exercise, which is more helpful to the user.