from django.db import models


# Create your models here.


class User(models.Model):
    """
    Represents basic information about the user, including the email that would make their account unique.
    Specifies that a user can have
    """
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name="unique_user_name"
            )
        ]


class Evaluation(models.Model):
    """
    Represents information about the user's injury so that a suitable rehabilitation program can be created.
    Ensures the associated evaluations are deleted when a user is deleted.
    """
    evaluation_id = models.AutoField(primary_key=True)
    injury_name = models.CharField(max_length=100, default="")
    injury_description = models.CharField(max_length=100)
    pain_level = models.IntegerField()
    date = models.DateField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.injury_name} - {self.user_id.first_name} {self.user_id.last_name} - {self.date}"

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "date"],
                name="unique_user_evaluation_date"
            )
        ]