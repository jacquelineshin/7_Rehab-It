from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.views import View
from django.views.generic import ListView, DetailView
from account.models import User
from .models import Exercise, WorkoutSession, TrainingPlan
from django.db.models import Count
from django.http import JsonResponse
import matplotlib.pyplot as plt
from django.shortcuts import render
from io import BytesIO

def exercise_chart_page(request):
    return render(request, "rehab/exercise_chart.html")
def exerciseManual(request):
    exercises = Exercise.objects.all()
    template = loader.get_template("rehab/exercise_list.html")
    context = {"exercises": exercises}
    return HttpResponse(template.render(context, request))


def exerciseList(request):
    exercises = Exercise.objects.all()
    context = {"exercises": exercises}
    return render(request, "rehab/exercise_list.html", context)


class ExerciseBaseView(View):
    def get(self, request):
        exercises = Exercise.objects.all()
        context = {"exercises": exercises}
        return render(request, "rehab/exercise_list.html", context)


class ExerciseListView(ListView):
    model = Exercise
    template_name = "rehab/exercise_list.html"
    context_object_name = "exercises"


class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = "rehab/exercise_detail.html"
    context_object_name = "exercise"


class WorkoutSessionDetailView(DetailView):
    model = WorkoutSession
    template_name = "rehab/workout_session_detail.html"
    context_object_name = "session"


class TrainingPlanListView(ListView):
    model = TrainingPlan
    template_name = "rehab/training_plan_list.html"
    context_object_name = "trainingPlans"

    def get_queryset(self):
        return TrainingPlan.objects.filter(user_id=self.kwargs["user_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(User, pk=self.kwargs["user_id"])
        return context


class TrainingPlanDashboardView(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        plan = TrainingPlan.objects.filter(user_id=user, active=True).first()

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
            "user": user,
            "plan": plan,
            "sessions": sessions,
            "completedCount": completedCount,
            "totalCount": totalCount,
            "percentComplete": percentComplete,
        }
        return render(request, "rehab/training_plan_dashboard.html", context)
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

    plt.figure(figsize=(8, 5))
    plt.bar(difficulties, counts)

    plt.title("Exercises by Difficulty")
    plt.xlabel("Difficulty Level")
    plt.ylabel("Number of Exercises")
    plt.legend(["Exercises"])
    plt.tight_layout()

    buffer = BytesIO()

    plt.savefig(buffer, format="png")
    plt.close()

    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")