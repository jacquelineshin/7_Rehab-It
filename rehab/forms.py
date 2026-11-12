
from django import forms
from .models import TrainingPlan
from .models import WorkoutSession, Exercise

class TrainingPlanForm(forms.ModelForm):

    class Meta:
        model = TrainingPlan

        fields = [
            "name",
            "start_date",
            "end_date",
        ]

        labels = {
            "name": "Training Plan Name",
            "start_date": "Start Date",
            "end_date": "End Date",
        }

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Example: Beginner Rehabilitation Plan"
            }),

            "start_date": forms.DateInput(attrs={
                "type": "date"
            }),

            "end_date": forms.DateInput(attrs={
                "type": "date"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "End date cannot be before the start date."
                )

        return cleaned_data

class WorkoutSessionForm(forms.ModelForm):

    exercises = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Exercises"
    )

    class Meta:
        model = WorkoutSession

        fields = [
            "name",
            "date",
            "exercises",
        ]

        labels = {
            "name": "Session Name",
            "date": "Session Date",
        }

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Example: Lower Body Strength"
            }),

            "date": forms.DateInput(attrs={
                "type": "date"
            }),
        }

class WorkoutReflectionForm(forms.ModelForm):

    class Meta:
        model = WorkoutSession

        fields = [
            "difficulty_rating",
            "reflection_notes"
        ]

        labels = {
            "difficulty_rating": "How difficult was this workout?",
            "reflection_notes": "How did your workout go?"
        }

        widgets = {
            "difficulty_rating": forms.RadioSelect(),
            "reflection_notes": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "How did you feel during the workout? "
                        "What felt easier or more challenging? "
                        "Did you notice any pain or fatigue?"
                    )
                }
            )
        }
