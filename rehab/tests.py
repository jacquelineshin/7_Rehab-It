from django.test import TestCase

from .models import Exercise, WorkoutSession


class ApiTests(TestCase):
    def setUp(self):
        squat = Exercise.objects.create(name="Squat", description="squat", difficulty=3)
        pushup = Exercise.objects.create(name="Pushup", description="pushup", difficulty=7)

        legDay = WorkoutSession.objects.create(name="Leg Day", date="2026-09-01", completed=True)
        legDay.exercises.add(squat)

        armDay = WorkoutSession.objects.create(name="Arm Day", date="2026-09-03", completed=False)
        armDay.exercises.add(pushup)

    def testExerciseApi(self):
        response = self.client.get("/api/exercises/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

    def testExerciseFilter(self):
        response = self.client.get("/api/exercises/?minDifficulty=5")
        self.assertEqual(response.json()["exercises"][0]["name"], "Pushup")

        response = self.client.get("/api/exercises/?difficulty=hard")
        self.assertEqual(response.status_code, 400)

    def testWorkoutSessionFilter(self):
        response = self.client.get("/api/workoutSessions/?completed=false")
        self.assertEqual(response.json()["workoutSessions"][0]["name"], "Arm Day")

        response = self.client.get("/api/workoutSessions/?exercise=squat")
        self.assertEqual(response.json()["workoutSessions"][0]["name"], "Leg Day")

    def testContentTypes(self):
        httpResponse = self.client.get("/api/httpResponse/")
        jsonResponse = self.client.get("/api/jsonResponse/")

        self.assertEqual(httpResponse["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(jsonResponse["Content-Type"], "application/json")

    def testSummaryApis(self):
        response = self.client.get("/api/summary/")
        self.assertEqual(response.json(), [
            {"difficulty": 3, "count": 1},
            {"difficulty": 7, "count": 1},
        ])

        response = self.client.get("/api/sessionSummary/")
        self.assertEqual(response.json(), [
            {"date": "2026-09-01", "count": 1},
            {"date": "2026-09-03", "count": 1},
        ])

    def testChartPages(self):
        response = self.client.get("/vega-lite/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/vega-lite/chart1.png")
        self.assertEqual(response["Content-Type"], "image/png")

        response = self.client.get("/vega-lite/chart2.png")
        self.assertEqual(response["Content-Type"], "image/png")
