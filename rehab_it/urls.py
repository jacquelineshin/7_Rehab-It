

from django.contrib import admin
from django.urls import path

from rehab.views import (
    exerciseManual,
    exerciseList,
    ExerciseBaseView,
    TrainingPlanListView,
    home,
    ExerciseDetailView,
    WorkoutSessionDetailView,
    TrainingPlanDetailView,
    TrainingPlanDashboardView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("exercises/manual/", exerciseManual, name="exercise_manual"),
    path("exercises/render/", exerciseList, name="exercise_render"),
    path("exercises/cbv-base/", ExerciseBaseView.as_view(), name="exercise_cbv_base"),
    path("training_plan_history/", TrainingPlanListView.as_view(), name="training_plan_history"),
    path("training_plan_dashboard/", TrainingPlanDashboardView.as_view(), name="training_plan_dashboard"),
    path("training_plan_detail/<int:pk>", TrainingPlanDetailView.as_view(), name="training_plan_detail"),
    path("exercise/detail/<int:pk>", ExerciseDetailView.as_view(), name="exercise_detail"),
    path("workout_session/detail/<int:pk>", WorkoutSessionDetailView.as_view(), name="workout_session_detail"),
]
