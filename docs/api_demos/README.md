

## Use 1: Python script

A Python script calls the public /api/summary/ endpoint with requests, with no login or key. It prints the raw JSON rows, then computes the total number of exercises, the average difficulty weighted by count, the most common level, and each level’s percentage share

![Screenshot 2026-10-10 at 5.31.55 PM.png](../screenshots/Screenshot%202026-10-10%20at%205.31.55%E2%80%AFPM.png)

## Use 2: Google Sheets

A Google Apps Script fetches the public API and writes the rows into a sheet. Spreadsheet formulas then compute total exercises, weighted average difficulty, and the most common level, and a column chart is built from the imported data

![Screenshot 2026-10-10 at 5.51.27 PM.png](../screenshots/Screenshot%202026-10-10%20at%205.51.27%E2%80%AFPM.png)
![Screenshot 2026-10-10 at 5.52.27 PM.png](../screenshots/Screenshot%202026-10-10%20at%205.52.27%E2%80%AFPM.png)

## Use 3: Statistical Analysis

A Jupyter notebook loads the API into a pandas DataFrame, rebuilds one row per exercise from the counts, and computes the mean, median, mode, standard deviation, min and max difficulty. It also shows the percent share per level and plots the data.

![Screenshot 2026-10-10 at 6.04.07 PM.png](../screenshots/Screenshot%202026-10-10%20at%206.04.07%E2%80%AFPM.png)
![Screenshot 2026-10-10 at 6.04.15 PM.png](../screenshots/Screenshot%202026-10-10%20at%206.04.15%E2%80%AFPM.png)
![Screenshot 2026-10-10 at 6.04.23 PM.png](../screenshots/Screenshot%202026-10-10%20at%206.04.23%E2%80%AFPM.png)
