

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
    exerciseSearch,
    workoutSessionSearch,
    workoutSessionExerciseSearch,
    dataSummary,
    external_exercise_search,
    exercise_analysis,
    exercise_chart_page,
    exercise_difficulty_chart,
    ReportsRehabView,
    rehab_csv,
)
from rehab.apiViews import (
    exerciseApi,
    WorkoutSessionApi,
    httpResponseDemo,
    jsonResponseDemo,
    exerciseSummaryApi,
    sessionSummaryApi,
)
from rehab.chartViews import (
    vegaCharts,
    vegaChart1,
    vegaChart2,
)
from django.contrib.auth import views as auth_views

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
    path("exercises/search/", exerciseSearch, name="exercise_search"),
    path("workout_sessions/search/", workoutSessionSearch, name="workout_session_search"),
    path("workout_sessions/exercise-search/", workoutSessionExerciseSearch, name="workout_session_exercise_search"),
    path("data-summary/", dataSummary, name="data_summary"),
    path("api/exercises/", exerciseApi, name="exerciseApi"),
    path("api/workoutSessions/", WorkoutSessionApi.as_view(), name="workoutSessionApi"),
    path("api/httpResponse/", httpResponseDemo, name="httpResponseDemo"),
    path("api/jsonResponse/", jsonResponseDemo, name="jsonResponseDemo"),
    path("api/external-exercises/", external_exercise_search, name="external_exercise_search"),
    path("api/exercise-analysis/", exercise_analysis, name="exercise_analysis"),
    path("exercise-chart/", exercise_chart_page, name="exercise_chart_page"),
    path("exercise-chart.png", exercise_difficulty_chart, name="exercise_difficulty_chart"),
    path("vega-lite/", vegaCharts, name="vegaCharts"),
    path("vega-lite/chart1.png", vegaChart1, name="vegaChart1"),
    path("vega-lite/chart2.png", vegaChart2, name="vegaChart2"),
    path("login/", auth_views.LoginView.as_view(template_name="account/../templates/registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("reports_rehab", ReportsRehabView.as_view(), name="reports_rehab"),
    path("export/rehab_csv", rehab_csv, name="export_rehab_csv"),
]
