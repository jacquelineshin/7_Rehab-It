from django.contrib import admin
from .models import TrainingPlan, WorkoutSession, Exercise


admin.site.register(TrainingPlan)
admin.site.register(WorkoutSession)
admin.site.register(Exercise)