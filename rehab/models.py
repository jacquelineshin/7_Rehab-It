from django.db import models

from account.models import User


# Create your models here.


class Exercise(models.Model):
    """
    Represents an individual exercise that a user might perform during a workout session.
    Specifies that an exercise can be present in many workout sessions, and a workout session can have many exercises.
    """
    exercise_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.IntegerField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "difficulty"],
                name="unique_exercise_difficulty"
            )
        ]


class WorkoutSession(models.Model):
    """
    Represents a workout session for a user's rehabilitation.
    Includes the exercises that will be performed during a workout session.
    """
    workout_session_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="")
    date = models.DateField()
    completed = models.BooleanField(default=False)
    exercises = models.ManyToManyField(Exercise)

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "date"],
                name="unique_workout_session_date"
            )
        ]


class TrainingPlan(models.Model):
    """
    Represents the breakdown of the training plan for a user's rehabilitation.
    Includes the specific user that the training plan belongs to.
    Ensures a user does not have two training plan with the same name and start date.
    Includes the workout sessions involved in the training plan.
    """
    training_plan_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_sessions = models.ManyToManyField(WorkoutSession)

    def __str__(self):
        return f"{self.name} - {self.user_id.first_name} {self.user_id.last_name}"

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "name", "start_date"],
                name="unique_user_training_plan"
            )
        ]