# 7_Rehab-It

## Project Description

Rehab-It is an AI-assisted rehabilitation application designed to provide personalized exercise guidance and support recovery.

## Project Goals

- Provide personalized rehabilitation guidance
- Help users perform exercises correctly
- Encourage exercise consistency and adherence
- Make rehabilitation resources more accessible

## Documentation

Project documentation, wireframes, branching strategy, and weekly progress notes are located in the `docs/` directory...

## API

Our API returns exercise and workout session data as JSON.

### Exercises (function based view)

`/api/exercises/`

You can filter with these:
- `name` - search exercises by name (ex. `/api/exercises/?name=squat`)
- `difficulty` - exact difficulty (ex. `/api/exercises/?difficulty=5`)
- `minDifficulty` and `maxDifficulty` - difficulty range (ex. `/api/exercises/?minDifficulty=4&maxDifficulty=8`)

If difficulty isn't a number it returns a 400 error.

### Workout Sessions (class based view)

`/api/workoutSessions/`

You can filter with these:
- `completed` - true or false (ex. `/api/workoutSessions/?completed=false`)
- `exercise` - sessions that have a certain exercise (ex. `/api/workoutSessions/?exercise=squat`)

### HttpResponse vs JsonResponse

- `/api/httpResponse/` - uses HttpResponse, content type is `text/html`
- `/api/jsonResponse/` - uses JsonResponse, content type is `application/json`

Both return the same exercise data, only the content type is different.
## UI Improvements

The Rehab-It interface was updated with custom CSS to create a more consistent and user-friendly design. The home, exercise list, and exercise difficulty dashboard use consistent colors, spacing, typography, and card-style layouts to improve readability and navigation. The exercise difficulty dashboard also displays exercise data as a visual chart, making it easier for users to understand the distribution of exercises across difficulty levels.
