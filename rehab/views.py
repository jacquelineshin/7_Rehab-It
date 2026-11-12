import csv
from datetime import datetime
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView

from .decorators import api_login_required
from .models import Exercise, WorkoutSession, TrainingPlan
from .forms import TrainingPlanForm, WorkoutSessionForm, WorkoutReflectionForm

from django.shortcuts import render
# ---------- PUBLIC pages ----------

def home(request):
    return render(request, "rehab/home.html")



from django.contrib.auth.decorators import login_required


@login_required
def exercise_chart_page(request):

    # Find the user's most recent active training plan
    plan = (
        TrainingPlan.objects
        .filter(
            account=request.user,
            active=True
        )
        .order_by("-start_date")
        .first()
    )

    # Default values when no active plan exists
    total_count = 0
    completed_count = 0
    percent_complete = 0

    if plan:

        sessions = plan.workout_sessions.all()

        total_count = sessions.count()

        completed_count = sessions.filter(
            completed=True
        ).count()

        if total_count > 0:
            percent_complete = round(
                (completed_count / total_count) * 100
            )

    # Get the user's five most recent workout sessions,
    # including sessions from finished training plans
    recent_sessions = (
        WorkoutSession.objects
        .filter(
            trainingplan__account=request.user,
            completed=True
        )
        .distinct()
        .order_by("-date", "-pk")[:5]
    )

    # Get completed workouts with difficulty ratings
    rated_sessions = (
        WorkoutSession.objects
        .filter(
            trainingplan__account=request.user,
            completed=True,
            difficulty_rating__isnull=False
        )
        .distinct()
        .order_by("date", "pk")
    )

    # Prepare data for the difficulty-over-time chart
    difficulty_labels = [
        session.date.strftime("%b %d, %Y")
        for session in rated_sessions
    ]

    difficulty_values = [
        session.difficulty_rating
        for session in rated_sessions
    ]


    # Dates of completed workouts belonging to this user
    completed_workout_dates = list(
        WorkoutSession.objects
        .filter(
            trainingplan__account=request.user,
            completed=True
        )
        .values_list("date", flat=True)
        .distinct()
    )

    # Convert dates into strings for JavaScript
    calendar_dates = [
        date.isoformat()
        for date in completed_workout_dates
    ]

    context = {
        "plan": plan,
        "totalCount": total_count,
        "completedCount": completed_count,
        "percentComplete": percent_complete,
        "recent_sessions": recent_sessions,
        "difficulty_labels": difficulty_labels,
        "difficulty_values": difficulty_values,
        "calendar_dates": calendar_dates,
    }


    return render(
        request,
        "rehab/exercise_chart.html",
        context
    )



# ---------- PROTECTED pages ----------

def exerciseManual(request):
    template = loader.get_template("rehab/exercise_list.html")
    exercises = Exercise.objects.all()

    context = {
        "exercises": exercises
    }

    return HttpResponse(template.render(context, request))


@login_required
def exerciseList(request):
    exercises = Exercise.objects.all()

    return render(
        request,
        "rehab/exercise_list.html",
        {"exercises": exercises}
    )


class ExerciseBaseView(LoginRequiredMixin, View):
    def get(self, request):
        exercises = Exercise.objects.all()

        return render(
            request,
            "rehab/exercise_list.html",
            {"exercises": exercises}
        )


class ExerciseListView(LoginRequiredMixin, ListView):
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


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = Exercise
    template_name = "rehab/exercise_detail.html"
    context_object_name = "exercise"


class TrainingPlanListView(LoginRequiredMixin, ListView):
    model = TrainingPlan
    template_name = "rehab/training_plan_history.html"
    context_object_name = "training_plans"

    def get_queryset(self):
        return TrainingPlan.objects.filter(
            account=self.request.user,
            active=False
        ).order_by("-start_date")



class TrainingPlanDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):

        training_plan = get_object_or_404(
            TrainingPlan,
            pk=pk,
            account=request.user
        )

        workout_sessions = (
            training_plan.workout_sessions
            .prefetch_related("exercises")
            .order_by("date")
        )

        total_count = workout_sessions.count()

        completed_count = workout_sessions.filter(
            completed=True
        ).count()

        if total_count > 0:
            percent_complete = round(
                (completed_count / total_count) * 100
            )
        else:
            percent_complete = 0

        return render(
            request,
            "rehab/training_plan_detail.html",
            {
                "training_plan": training_plan,
                "workout_sessions": workout_sessions,
                "totalCount": total_count,
                "completedCount": completed_count,
                "percentComplete": percent_complete,
            }
        )



class WorkoutSessionDetailView(LoginRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = "rehab/workout_session_detail.html"
    context_object_name = "workout_session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exercises"] = self.object.exercises.all()
        return context



class TrainingPlanCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = TrainingPlanForm()

        return render(
            request,
            "rehab/training_plan_form.html",
            {"form": form}
        )

    def post(self, request):
        form = TrainingPlanForm(request.POST)

        if form.is_valid():
            from account.models import User as RehabUser

            # Find or create a custom user linked by name
            first_name = request.user.first_name or request.user.username
            last_name = request.user.last_name or "Account"

            rehab_user, created = RehabUser.objects.get_or_create(
                first_name=first_name,
                last_name=last_name
            )

            training_plan = form.save(commit=False)
            training_plan.user_id = rehab_user
            training_plan.account = request.user
            training_plan.save()

            return redirect("training_plan_dashboard")

        return render(
            request,
            "rehab/training_plan_form.html",
            {"form": form}
        )


class TrainingPlanUpdateView(LoginRequiredMixin, View):

    def get_plan(self, request, pk):
        return get_object_or_404(
            TrainingPlan,
            pk=pk,
            account=request.user
        )

    def get(self, request, pk):
        plan = self.get_plan(request, pk)

        form = TrainingPlanForm(instance=plan)

        return render(
            request,
            "rehab/training_plan_form.html",
            {
                "form": form,
                "editing": True,
                "plan": plan
            }
        )

    def post(self, request, pk):
        plan = self.get_plan(request, pk)

        form = TrainingPlanForm(
            request.POST,
            instance=plan
        )

        if form.is_valid():
            form.save()

            return redirect("training_plan_dashboard")

        return render(
            request,
            "rehab/training_plan_form.html",
            {
                "form": form,
                "editing": True,
                "plan": plan
            }
        )

class TrainingPlanFinishView(LoginRequiredMixin, View):

    def post(self, request, pk):
        plan = get_object_or_404(
            TrainingPlan,
            pk=pk,
            account=request.user,
            active=True
        )

        plan.active = False
        plan.save(update_fields=["active"])

        return redirect("training_plan_history")

class WorkoutSessionCreateView(LoginRequiredMixin, View):

    def get_plan(self, request, pk):
        return get_object_or_404(
            TrainingPlan,
            pk=pk,
            account=request.user
        )

    def get(self, request, pk):
        plan = self.get_plan(request, pk)
        form = WorkoutSessionForm()

        return render(
            request,
            "rehab/workout_session_form.html",
            {
                "form": form,
                "plan": plan
            }
        )

    def post(self, request, pk):
        plan = self.get_plan(request, pk)
        form = WorkoutSessionForm(request.POST)

        if form.is_valid():
            session = form.save()
            plan.workout_sessions.add(session)

            return redirect("training_plan_dashboard")

        return render(
            request,
            "rehab/workout_session_form.html",
            {
                "form": form,
                "plan": plan
            }
        )

class WorkoutSessionCompleteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        session = get_object_or_404(
            WorkoutSession,
            pk=pk,
            trainingplan__account=request.user
        )

        session.completed = True
        session.save(update_fields=["completed"])

        return redirect("training_plan_dashboard")

class WorkoutSessionUpdateView(LoginRequiredMixin, View):

    def get_session(self, request, plan_pk, pk):
        plan = get_object_or_404(
            TrainingPlan,
            pk=plan_pk,
            account=request.user
        )

        session = get_object_or_404(
            plan.workout_sessions,
            pk=pk
        )

        return plan, session

    def get(self, request, plan_pk, pk):
        plan, session = self.get_session(
            request, plan_pk, pk
        )

        form = WorkoutSessionForm(instance=session)

        return render(
            request,
            "rehab/workout_session_form.html",
            {
                "form": form,
                "plan": plan,
                "editing": True
            }
        )

    def post(self, request, plan_pk, pk):
        plan, session = self.get_session(
            request, plan_pk, pk
        )

        form = WorkoutSessionForm(
            request.POST,
            instance=session
        )

        if form.is_valid():
            form.save()
            return redirect("training_plan_dashboard")

        return render(
            request,
            "rehab/workout_session_form.html",
            {
                "form": form,
                "plan": plan,
                "editing": True
            }
        )

class WorkoutSessionDeleteView(LoginRequiredMixin, View):

    def get_session(self, request, plan_pk, pk):
        plan = get_object_or_404(
            TrainingPlan,
            pk=plan_pk,
            account=request.user
        )

        session = get_object_or_404(
            plan.workout_sessions,
            pk=pk
        )

        return plan, session

    def get(self, request, plan_pk, pk):
        plan, session = self.get_session(
            request, plan_pk, pk
        )

        return render(
            request,
            "rehab/workout_session_confirm_delete.html",
            {
                "plan": plan,
                "session": session
            }
        )

    def post(self, request, plan_pk, pk):
        plan, session = self.get_session(
            request, plan_pk, pk
        )

        # Remove the session from this plan only.
        plan.workout_sessions.remove(session)

        # Delete the session record only if no plans use it.
        if not session.trainingplan_set.exists():
            session.delete()

        return redirect("training_plan_dashboard")

class TrainingPlanDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        plan = TrainingPlan.objects.filter(
            account=request.user,
            active=True
        ).order_by("-start_date").first()

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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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

    labels = [difficulty_labels.get(d, str(d)) for d in difficulties]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, counts, label="Exercises")
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


# ---------- PROTECTED JSON APIs (use the external API key) ----------

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


@api_login_required
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


@api_login_required
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


class ReportsWorkoutView(TemplateView):
    template_name = "rehab/reports_workout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workoutsession_exercises"] = (
            WorkoutSession.objects
            .values("name")
            .order_by("name")
        )
        return context


class ReportsRehabView(TemplateView):
    template_name = "rehab/reports_rehab.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["workoutsession_exercises"] = (
            WorkoutSession.objects.values("name")
        )

        context["trainingplan_workoutsessions"] = (
            TrainingPlan.objects.values("name")
        )

        context["total_exercises"] = Exercise.objects.count()
        context["total_workout_sessions"] = WorkoutSession.objects.count()
        context["total_training_plans"] = TrainingPlan.objects.count()

        return context

def rehab_csv(request):
    rehab_csv_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    rehab_file = f"rehab_{rehab_csv_time}.csv"
    rehab_response = HttpResponse(content_type="text/csv")
    rehab_response["Content-Disposition"] = f"attachment; filename={rehab_file}"
    rehab_response
    rehab_writer = csv.writer(rehab_response)
    rehab_writer.writerow(["name"])
    rehab_rows = (
        Exercise.objects
        .values_list("name")
    )
    for table in rehab_rows:
        rehab_writer.writerow(table)
    return rehab_response

def rehab_json(request):
    rehab_json_data = list(
        Exercise.objects
        .values("name")
    )
    rehab_json_information = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_exercises": len(rehab_json_data),
        "exercises": rehab_json_data,
    }
    rehab_response = JsonResponse(rehab_json_information)
    rehab_json_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    rehab_file = f"rehab_{rehab_json_time}.json"
    rehab_response["Content-Disposition"] = f"attachment; filename={rehab_file}"
    return rehab_response


def pubmed_research(request):
    query = request.GET.get("q", "").strip()
    articles = []
    error = None

    if query:
        try:
            response = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmode": "json",
                    "retmax": 5,
                },
                timeout=10,
            )
            response.raise_for_status()

            article_ids = response.json()["esearchresult"]["idlist"]

            if article_ids:
                details = requests.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(article_ids),
                        "retmode": "json",
                    },
                    timeout=10,
                )
                details.raise_for_status()
                results = details.json()["result"]

                for article_id in article_ids:
                    article = results[article_id]
                    articles.append({
                        "title": article.get("title", ""),
                        "journal": article.get("fulljournalname", ""),
                        "date": article.get("pubdate", ""),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/",
                    })

        except (requests.exceptions.RequestException, ValueError, KeyError):
            error = "Unable to retrieve PubMed articles right now."

    return render(
        request,
        "rehab/pubmed_research.html",
        {
            "query": query,
            "articles": articles,
            "error": error,
        },
    )
from django.shortcuts import render
from .ai_service import generate_exercise_response



def ai_assistant(request):
    question = ""
    answer = None
    exercises = []
    error = None

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if not question:
            error = "Please describe your exercise goals."

        elif len(question) > 500:
            error = "Please keep your request under 500 characters."

        else:
            try:
                from .ai_service import retrieve_exercises

                exercises = retrieve_exercises(question, top_k=3)
                print("EXERCISE FINDER RESULTS:", exercises, flush=True)
                if not exercises:
                    error = "No exercises are currently available."

            except Exception:
                error = "Unable to find exercises right now. Please try again."
                import logging
                logging.getLogger(__name__).exception(
                    "Exercise Finder failed"
                )

    return render(
        request,
        "rehab/ai_assistant.html",
        {
            "question": question,
            "answer": answer,
            "exercises": exercises,
            "error": error,
        },
    )

class WorkoutReflectionView(LoginRequiredMixin, View):

    def get_session(self, request, pk):
        return get_object_or_404(
            WorkoutSession,
            pk=pk,
            trainingplan__account=request.user,
            completed=True
        )

    def get(self, request, pk):
        session = self.get_session(request, pk)

        form = WorkoutReflectionForm(instance=session)

        return render(
            request,
            "rehab/workout_reflection_form.html",
            {
                "form": form,
                "session": session
            }
        )

    def post(self, request, pk):
        session = self.get_session(request, pk)

        form = WorkoutReflectionForm(
            request.POST,
            instance=session
        )

        if form.is_valid():
            form.save()

            return redirect("training_plan_dashboard")

        return render(
            request,
            "rehab/workout_reflection_form.html",
            {
                "form": form,
                "session": session
            }
        )
