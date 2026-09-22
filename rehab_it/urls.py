

from django.contrib import admin
from django.urls import path

from rehab.views import (
    exerciseManual,
    exerciseList,
    ExerciseBaseView,
    ExerciseListView,
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("exercises/manual/", exerciseManual, name="exercise_manual"),
    path("exercises/render/", exerciseList, name="exercise_render"),
    path("exercises/cbv-base/", ExerciseBaseView.as_view(), name="exercise_cbv_base"),
    path("exercises/cbv-generic/", ExerciseListView.as_view(), name="exercise_cbv_generic"),
]
