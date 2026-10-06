import json

from django.http import HttpResponse, JsonResponse
from django.views import View

from .models import Exercise, WorkoutSession


def exerciseApi(request):
    exercises = Exercise.objects.all()

    name = request.GET.get("name")
    difficulty = request.GET.get("difficulty")
    minDifficulty = request.GET.get("minDifficulty")
    maxDifficulty = request.GET.get("maxDifficulty")

    if name:
        exercises = exercises.filter(name__icontains=name)

    if difficulty:
        if not difficulty.isdigit():
            return JsonResponse({"error": "difficulty has to be a number"}, status=400)
        exercises = exercises.filter(difficulty=difficulty)

    if minDifficulty:
        if not minDifficulty.isdigit():
            return JsonResponse({"error": "minDifficulty has to be a number"}, status=400)
        exercises = exercises.filter(difficulty__gte=minDifficulty)

    if maxDifficulty:
        if not maxDifficulty.isdigit():
            return JsonResponse({"error": "maxDifficulty has to be a number"}, status=400)
        exercises = exercises.filter(difficulty__lte=maxDifficulty)

    exerciseList = []

    for exercise in exercises:
        exerciseList.append({
            "id": exercise.exercise_id,
            "name": exercise.name,
            "description": exercise.description,
            "difficulty": exercise.difficulty,
        })

    return JsonResponse({
        "count": len(exerciseList),
        "exercises": exerciseList,
    })


class WorkoutSessionApi(View):
    def get(self, request):
        sessions = WorkoutSession.objects.all()

        completed = request.GET.get("completed")
        exercise = request.GET.get("exercise")

        if completed == "true":
            sessions = sessions.filter(completed=True)
        elif completed == "false":
            sessions = sessions.filter(completed=False)

        if exercise:
            sessions = sessions.filter(exercises__name__icontains=exercise).distinct()

        sessionList = []

        for session in sessions:
            exerciseNames = []

            for sessionExercise in session.exercises.all():
                exerciseNames.append(sessionExercise.name)

            sessionList.append({
                "id": session.workout_session_id,
                "name": session.name,
                "date": str(session.date),
                "completed": session.completed,
                "exercises": exerciseNames,
            })

        return JsonResponse({
            "count": len(sessionList),
            "workoutSessions": sessionList,
        })


def httpResponseDemo(request):
    exercises = Exercise.objects.all()
    exerciseList = []

    for exercise in exercises:
        exerciseList.append({
            "id": exercise.exercise_id,
            "name": exercise.name,
            "difficulty": exercise.difficulty,
        })

    return HttpResponse(json.dumps(exerciseList))


def jsonResponseDemo(request):
    exercises = Exercise.objects.all()
    exerciseList = []

    for exercise in exercises:
        exerciseList.append({
            "id": exercise.exercise_id,
            "name": exercise.name,
            "difficulty": exercise.difficulty,
        })

    return JsonResponse(exerciseList, safe=False)


def getExerciseSummary():
    exercises = Exercise.objects.all().order_by("difficulty")
    difficultyCounts = {}

    for exercise in exercises:
        if exercise.difficulty in difficultyCounts:
            difficultyCounts[exercise.difficulty] += 1
        else:
            difficultyCounts[exercise.difficulty] = 1

    summary = []

    for difficulty in difficultyCounts:
        summary.append({
            "difficulty": difficulty,
            "count": difficultyCounts[difficulty],
        })

    return summary


def getSessionSummary():
    sessions = WorkoutSession.objects.all().order_by("date")
    dateCounts = {}

    for session in sessions:
        date = str(session.date)

        if date in dateCounts:
            dateCounts[date] += 1
        else:
            dateCounts[date] = 1

    summary = []

    for date in dateCounts:
        summary.append({
            "date": date,
            "count": dateCounts[date],
        })

    return summary


def exerciseSummaryApi(request):
    response = JsonResponse(getExerciseSummary(), safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def sessionSummaryApi(request):
    response = JsonResponse(getSessionSummary(), safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response
