from django.contrib import admin
from django.urls import path

from rehab.views import (
    exerciseManual,
    exerciseList,
    ExerciseBaseView,
    ExerciseListView,
    exercise_difficulty_data,
    exercise_difficulty_chart,
    exercise_chart_page,
)
urlpatterns = [
    path("admin/", admin.site.urls),

    path("exercises/manual/", exerciseManual, name="exercise_manual"),
    path("exercises/render/", exerciseList, name="exercise_render"),
    path("exercises/cbv-base/", ExerciseBaseView.as_view(), name="exercise_cbv_base"),
    path("exercises/cbv-generic/", ExerciseListView.as_view(), name="exercise_cbv_generic"),

    path(
        "exercise-data/",
        exercise_difficulty_data,
        name="exercise_difficulty_data",
    ),
    path(
        "exercise-chart/",
        exercise_difficulty_chart,
        name="exercise_difficulty_chart",
    ),
    path(
        "exercise-chart-page/",
        exercise_chart_page,
        name="exercise_chart_page",
),
]

