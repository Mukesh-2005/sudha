# Online Voting System

A Flask + SQLite web app for college elections: students authenticate with
their Student ID, cast exactly one vote, and admins watch results tally live.

## Setup

```
py -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python init_db.py   # creates voting.db with sample data
venv\Scripts\python app.py       # http://127.0.0.1:5000
```

## Sample logins

| Student ID | Password  |
|------------|-----------|
| S1001      | pass1001  |
| S1002      | pass1002  |
| S1003      | pass1003  |
| S1004      | pass1004  |
| S1005      | pass1005  |

Admin panel: `/admin` — username `admin`, password `admin123`.

## Architecture

Browser (HTML/CSS/JS) ↔ Flask backend (`/`, `/login`, `/vote`,
`/confirmation`, `/admin`, `/results`) ↔ SQLite (`voting.db`).

## Database schema

**students**: `STUDENT_ID` (PK), `STUDENT_NAME`, `DEPARTMENT`, `YEAR`,
`PASSWORD`, `VOTE_STATUS`, `VOTED_FOR` (FK → candidates.CANDIDATE_ID)

**candidates**: `CANDIDATE_ID` (PK), `CANDIDATE_NAME`, `PARTY`, `VOTE_COUNT`

`PASSWORD` was added beyond the original ID-only design so a Student ID
alone (which isn't secret) can't be used to vote on someone else's behalf.

## Flow

Login → check `VOTE_STATUS` → if not voted, show ballot → submit vote →
update `VOTE_COUNT` + `VOTE_STATUS` in one transaction → confirmation page.
Admin logs in separately and watches `/results`, which auto-refreshes
every 5 seconds.

## Notes for production use

This is a teaching/demo build. Before using it for a real election:
switch `app.secret_key` and the admin password to environment variables,
hash student passwords (e.g. with `werkzeug.security`) instead of storing
them in plaintext, and serve behind a real WSGI server (gunicorn/waitress)
instead of the Flask dev server.
