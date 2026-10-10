"""
Use case 1: Python script that consumes the public Rehab-It API
and performs simple aggregations.

Run:  python use1_python_script.py
Needs: pip install requests
"""
import requests

API_URL = "https://jacquelineshin.pythonanywhere.com/api/summary/"

# 1. Call the public API (no login, no API key)
response = requests.get(API_URL, timeout=10)
print("API URL      :", API_URL)
print("HTTP status  :", response.status_code)
print("Content-Type :", response.headers.get("Content-Type"))
response.raise_for_status()

rows = response.json()   # list of {"difficulty", "label", "count"}

# 2. Show the raw data that was received
print("\nRaw data from API:")
for row in rows:
    print("  ", row)

# 3. Simple aggregations
total_exercises = sum(r["count"] for r in rows)
weighted_avg_difficulty = sum(r["difficulty"] * r["count"] for r in rows) / total_exercises
most_common = max(rows, key=lambda r: r["count"])

print("\nResults:")
print(f"  Total exercises            : {total_exercises}")
print(f"  Average difficulty (1-5)   : {weighted_avg_difficulty:.2f}")
print(f"  Most common level          : {most_common['label']} ({most_common['count']} exercises)")

print("\nShare of exercises by level:")
for r in rows:
    pct = r["count"] / total_exercises * 100
    print(f"  {r['label']:<15} {r['count']:>3}  {pct:5.1f}%")
