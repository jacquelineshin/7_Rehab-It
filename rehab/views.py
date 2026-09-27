from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.views import View
from django.views.generic import ListView, DetailView

from account.models import User
from .models import Exercise, WorkoutSession, TrainingPlan


def home(request):
    return render(request, "rehab/home.html")


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
    context_object_name = "workout_session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exercises"] = self.object.exercises.all()
        return context


class TrainingPlanDetailView(DetailView):
    model = TrainingPlan
    template_name = "rehab/training_plan_detail.html"
    context_object_name = "training_plan"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workout_sessions"] = self.object.workout_sessions.all()
        return context


class TrainingPlanListView(ListView):
    model = TrainingPlan
    template_name = "rehab/training_plan_history.html"
    context_object_name = "training_plans"

    def get_queryset(self):
        return TrainingPlan.objects.filter(active=False)


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