from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Count

from account.models import User
from .models import Exercise, WorkoutSession, TrainingPlan

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import requests
from django.conf import settings
from django.http import JsonResponse


def home(request):
    return render(request, "rehab/home.html")


def exerciseManual(request):
    template = loader.get_template("rehab/exercise_list.html")
    exercises = Exercise.objects.all()

    context = {
        "exercises": exercises
    }

    return HttpResponse(template.render(context, request))


def exerciseList(request):
    exercises = Exercise.objects.all()

    return render(
        request,
        "rehab/exercise_list.html",
        {"exercises": exercises}
    )


class ExerciseBaseView(View):
    def get(self, request):
        exercises = Exercise.objects.all()

        return render(
            request,
            "rehab/exercise_list.html",
            {"exercises": exercises}
        )


class ExerciseListView(ListView):
    model = Exercise
    template_name = "rehab/exercise_list.html"
    context_object_name = "exercises"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.request.POST.get("results") or self.request.GET.get("results")
        context["results"] = results
        return context


class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = "rehab/exercise_detail.html"
    context_object_name = "exercise"


class TrainingPlanListView(ListView):
    model = TrainingPlan
    template_name = "rehab/training_plan_history.html"
    context_object_name = "training_plans"

    def get_queryset(self):
        return TrainingPlan.objects.filter(active=False)


class TrainingPlanDetailView(DetailView):
    model = TrainingPlan
    template_name = "rehab/training_plan_detail.html"
    context_object_name = "training_plan"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["results"] = self.request.POST.get("results") or self.request.GET.get("results")
        context["workout_sessions"] = self.object.workout_sessions.all()
        return context


class WorkoutSessionDetailView(DetailView):
    model = WorkoutSession
    template_name = "rehab/workout_session_detail.html"
    context_object_name = "workout_session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exercises"] = self.object.exercises.all()
        return context


class TrainingPlanDashboardView(View):
    def get(self, request):
        plan = TrainingPlan.objects.filter(active=True).first()

        if plan:
            sessions = plan.workout_sessions.all()
        else:
            sessions = []

        totalCount = len(sessions)
        completedCount = 0

        for session in sessions:
            if session.completed:
                completedCount += 1

        if totalCount > 0:
            percentComplete = int(completedCount / totalCount * 100)
        else:
            percentComplete = 0

        context = {
            "plan": plan,
            "sessions": sessions,
            "completedCount": completedCount,
            "totalCount": totalCount,
            "percentComplete": percentComplete,
        }

        return render(
            request,
            "rehab/training_plan_dashboard.html",
            context
        )


def exercise_chart_page(request):
    return render(request, "rehab/exercise_chart.html")


def exercise_difficulty_data(request):
    exercise_counts = (
        Exercise.objects
        .values("difficulty")
        .annotate(count=Count("exercise_id"))
        .order_by("difficulty")
    )

    return JsonResponse(list(exercise_counts), safe=False)


def exercise_difficulty_chart(request):
    exercise_counts = (
        Exercise.objects
        .values("difficulty")
        .annotate(count=Count("exercise_id"))
        .order_by("difficulty")
    )

    difficulties = [item["difficulty"] for item in exercise_counts]
    counts = [item["count"] for item in exercise_counts]

    difficulty_labels = {
        1: "Very Easy",
        2: "Easy",
        3: "Moderate",
        4: "Difficult",
        5: "Very Difficult",
    }

    labels = [
        difficulty_labels.get(d, str(d))
        for d in difficulties
    ]

    plt.figure(figsize=(8, 5))

    plt.bar(
        labels,
        counts,
        label="Exercises"
    )

    plt.title("Exercises by Difficulty")
    plt.xlabel("Difficulty Level")
    plt.ylabel("Number of Exercises")

    plt.legend(["Exercises"])
    plt.tight_layout()

    buffer = BytesIO()

    plt.savefig(
        buffer,
        format="png"
    )

    plt.close()

    buffer.seek(0)

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )


def exerciseSearch(request):
    query = request.GET.get("q", "")

    exercises = Exercise.objects.all()

    if query:
        exercises = exercises.filter(
            name__icontains=query
        )

    context = {
        "exercises": exercises,
        "query": query,
    }

    return render(
        request,
        "rehab/exercise_search.html",
        context
    )


def workoutSessionSearch(request):
    sessions = WorkoutSession.objects.all()

    if request.method == "POST":
        completed = request.POST.get("completed")

        if completed:
            sessions = sessions.filter(
                completed__exact=True
            )

    context = {
        "sessions": sessions,
    }

    return render(
        request,
        "rehab/workout_session_search.html",
        context
    )


def workoutSessionExerciseSearch(request):
    query = request.GET.get("q", "")

    sessions = WorkoutSession.objects.all()

    if query:
        sessions = sessions.filter(
            exercises__name__icontains=query
        ).distinct()

    context = {
        "sessions": sessions,
        "query": query,
    }

    return render(
        request,
        "rehab/workout_session_exercise_search.html",
        context
    )


def dataSummary(request):
    total_exercises = Exercise.objects.count()

    session_summary = (
        WorkoutSession.objects
        .values("completed")
        .annotate(
            count=Count("workout_session_id")
        )
        .order_by("completed")
    )

    context = {
        "total_exercises": total_exercises,
        "session_summary": session_summary,
    }

    return render(
        request,
        "rehab/data_summary.html",
        context
    )


EXTERNAL_URL = "https://api.exerciseapi.dev/v1/exercises"


def fetch_external_exercises(query):
    response = requests.get(
        EXTERNAL_URL,
        params={"q": query, "category": "physical_therapy", "limit": 5},
        headers={"X-API-Key": settings.EXERCISE_API_KEY},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def external_exercise_search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse(
            {"error": "Please provide a search term using ?q="},
            status=400
        )

    try:
        data = fetch_external_exercises(query)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "The exercise API timed out."}, status=504)
    except requests.exceptions.RequestException:
        return JsonResponse({"error": "Unable to retrieve exercise data."}, status=502)

    return JsonResponse(data)


def exercise_analysis(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse(
            {"error": "Please provide a search term using ?q="},
            status=400
        )

    # 1. Get external exercise data
    try:
        external_data = fetch_external_exercises(query)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "The exercise API timed out."}, status=504)
    except requests.exceptions.RequestException:
        return JsonResponse(
            {"error": "Unable to retrieve external exercise data."},
            status=502
        )

    # 2. Process external results
    external_results = []
    for exercise in external_data.get("data", []):
        external_results.append({
            "name": exercise.get("name"),
            "primary_muscles": exercise.get("primaryMuscles", []),
        })

    # 3. Search Rehab-It database
    internal_results = []
    for exercise in Exercise.objects.filter(name__icontains=query):
        internal_results.append({
            "name": exercise.name,
            "description": exercise.description,
            "difficulty": exercise.difficulty,
        })

    # 4. Compare the two sources
    internal_names = {item["name"].lower() for item in internal_results}
    overlapping = [
        item["name"] for item in external_results
        if item["name"] and item["name"].lower() in internal_names
    ]

    average_difficulty = (
        round(
            sum(item["difficulty"] for item in internal_results)
            / len(internal_results),
            2
        )
        if internal_results
        else None
    )

    # 5. Return combined analysis
    return JsonResponse({
        "query": query,
        "external_results": external_results,
        "rehab_it_results": internal_results,
        "analysis": {
            "external_match_count": len(external_results),
            "internal_match_count": len(internal_results),
            "total_match_count": len(external_results) + len(internal_results),
            "average_internal_difficulty": average_difficulty,
            "overlapping_exercise_names": overlapping,
            "overlap_count": len(overlapping),
        },
    })
