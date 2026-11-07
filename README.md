# Peer Connections — Interview Evaluation Application

Peer Connections is a tutoring and mentoring service with more than 100 employees, interviewing over 90 applicants each hiring cycle. This application supports that process by connecting interview observers directly to the Google Sheet used to collect candidate evaluations.

## The problem

Each interview involves several observers who assess candidates and record their scores and feedback on paper. Those evaluations then have to be transferred manually into Google Sheets for the interview team to review. With more than 90 applicants per cycle and multiple observers contributing feedback, transcribing the paper evaluations is a tedious, repetitive administrative task.

## The solution

This application bridges the gap between observing an interview and collecting its results. Observers enter scores and notes through a web form, review their drafts, and submit evaluations directly to the central Google Sheet. Each submission includes the candidate, room, round, observer details, ratings, recommendation, and notes, removing the need to retype those evaluations from paper.

Administrators continue managing candidate rosters in Google Sheets. The application reads three preassigned groups, rotates them through the interview activities, and filters the candidate list by room and round. Each observer's browser session keeps its own drafts, allowing several observers to work independently while their submitted evaluations flow into the same spreadsheet.

The result is a single workflow for candidate selection, scoring, draft review, and final submission that fits the interview team's existing use of Google Sheets.

## Documentation

- **Administrators and observers:** [Interview Administration User Guide](USER_GUIDE.md) covers interview-day setup, evaluations, submissions, and troubleshooting.
- **Developers and technical reviewers:** this README covers implementation, configuration, testing, and deployment.

## Features

- Three preassigned candidate groups rotate through Tinker Toys, Mini Lessons, and Scenarios over three rounds.
- Candidate dropdowns update according to the selected room and round.
- Structured evaluations include three half-point rating controls, a work-with recommendation, optional notes, and observer details including profstaff status.
- Observers can save, review, edit, and delete drafts before submission.
- Browser sessions isolate observation histories and draft actions between visitors.
- Final submission appends pending evaluations to a shared Google Sheet.
- Candidate loading validates headers and group membership, caches results, and preserves the last successful roster during refresh failures.

## Technology stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Backend | Python, FastAPI, Uvicorn | Request handling, validation, and application server |
| Templates | Jinja2 | Server-rendered forms and observation history |
| Frontend | JavaScript, HTML, CSS | Candidate filtering, rating controls, and inline editing |
| Integration | gspread, Google service-account credentials | Read candidate groups and append evaluations |
| Configuration | Environment variables, python-dotenv | Local and hosted configuration |
| Hosting | Render | Deployed application |
| Testing | unittest, mocks, FastAPI TestClient | Integration behavior and browser-session isolation |

## How it works

1. A page request loads candidate groups from the configured spreadsheet, subject to a 60-second refresh interval.
2. The backend calculates the room assignments for all three rounds and renders the form.
3. JavaScript filters the candidate dropdown when the observer changes room or round.
4. Saving a form creates or updates an observation in the current browser session's server-side draft list.
5. Final submission appends that session's pending observations to the observations tab and marks successful entries as submitted.

The browser receives an opaque session identifier in a cookie. Evaluation contents stay on the server until exported to Google Sheets. Each draft action uses the list associated with the current session; an observation ID alone does not grant access to another session's draft.

## Run locally

Prerequisites: Python with `venv` and `pip`, a Google Cloud service account, and a Google spreadsheet containing separate candidate and observations tabs. Dependency versions are pinned in `requirements.txt`; use a Python version compatible with those pins.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Fill in the environment variables described below, then start the application from the repository root:

```bash
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. Google Sheets access is required to load the roster; the app does not substitute sample names when configuration is missing.

## Configuration

Configure these variables in local `.env` or Render Environment settings:

- `GOOGLE_CREDENTIALS`: service account JSON.
- `GOOGLE_SHEET_ID`: spreadsheet ID shared by both tabs.
- `GOOGLE_OBSERVATIONS_SHEET_NAME`: exact observations tab name (for example `sheet1`).
- `GOOGLE_INTERVIEWEES_SHEET_NAME`: exact candidate tab name (for example `Interviewees`).

Tab names are case sensitive and must be different. See `.env.example`.
Enable the Google Sheets API and share the spreadsheet with the service account as an Editor.
Observations append to columns A–K of the explicitly selected observations tab;
place observation headers in row 1 and keep this table contiguous.
Add `Profstaff` as the header in column K. The required Yes/No answer is saved
with each evaluation and remains selected after saving a draft.

## Spreadsheet layout and group rotation

The interviewees tab must have these six unique headers in row 1:

| A | B | C | D | E | F |
| --- | --- | --- | --- | --- | --- |
| Group A First Name | Group A Last Name | Group B First Name | Group B Last Name | Group C First Name | Group C Last Name |

Place each candidate below the first/last name pair for their assigned group.
Replace the old two-column headers with this layout; existing names in A–B
will belong to Group A until you move them to another pair. Columns are matched
by header, so their order can also be changed. Groups may have different sizes;
blank cells and empty groups are allowed. Names are trimmed, combined,
deduplicated within each group, and sorted for display. A name appearing in
multiple groups is treated as an error; give people with identical names distinct
labels if necessary.

Groups stay together and rotate as follows:

| Group | Round 1 | Round 2 | Round 3 |
| --- | --- | --- | --- |
| A | Mini Lessons | Scenarios | Tinker Toys |
| B | Scenarios | Tinker Toys | Mini Lessons |
| C | Tinker Toys | Mini Lessons | Scenarios |

The observations tab uses this fixed column order:

| A | B | C | D | E | F | G | H | I | J | K |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Timestamp | Candidate | Round | Room | Observer | Question 1 | Question 2 | Personal Representation | Work With? | Notes | Profstaff |

## Refresh and failure handling

Names refresh on page loads at most once per 60 seconds per server process.
Connection, header, or duplicate-group failures show a warning and retain the
last successfully loaded groups in that process. A valid tab with headers but
no names clears all groups. Restarting clears the cache. No CSV or sample-name
fallback is used.

## Session privacy and storage

Draft observations are private to each browser session. Sharing the site link
opens a separate draft list; editing, deleting, and final submission only affect
the current browser's observations. The session cookie is HttpOnly and SameSite
Strict, with Secure enabled on HTTPS. Responses are marked `no-store`.

This is browser separation, without user accounts: people sharing a browser
profile share its drafts. Drafts remain in process memory and are lost on server
restart/redeploy or when the browser session cookie is lost. Use one server
worker/instance with this storage; multiple workers need a shared session store.
Already submitted Google Sheets rows remain in the central observations tab.
Browser separation does not authenticate an observer's identity. Anyone with the application link can open a session and enter an observer name; profstaff status is self-reported and does not grant additional permissions.

Submitted observations are append-only from the application. Editing a submitted entry and submitting again appends a revision; it does not update the original row. Deleting an entry from the browser history does not delete its spreadsheet row. Administrators reconcile corrections in Google Sheets.

The app has no durable draft database, account system, or administrator dashboard for other sessions. Final submission is not idempotent: concurrent submissions or an uncertain network result can create duplicates. These are areas to address before extending the app to larger or more demanding deployments.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests
```

The suite covers candidate parsing, duplicate-group detection, round rotation, cache refresh and recovery, worksheet selection, successful and failed submissions, profstaff persistence, and browser isolation. The isolation test uses two independent clients and checks that one cannot view, edit, delete, or submit the other's observations.

Google Sheets calls are mocked in automated tests, so the suite does not require credentials or modify a live spreadsheet. A successful test run does not replace checking a deployed instance against its configured sheet.

## Render deployment

Configure the service to use the intended repository branch and set the environment variables listed above.

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Process model:** one worker and one instance while drafts use process memory.

Confirm the deployed commit includes the intended changes. Merging to a remote branch alone does not confirm a successful deployment. After deployment, verify the roster, group rotation, draft isolation in two browsers, and submission using a clearly marked test evaluation. Remove any submitted test rows afterward.

Redeployment clears unsent drafts. Coordinate deployments with observers during active interviews.

Keep service-account JSON in local environment configuration or Render environment settings. Do not commit real credentials or include candidate information in public screenshots.

## Repository structure

```text
app.py                       FastAPI routes, Sheets integration, cache, and sessions
templates/index.html         Evaluation form and observation history
static/script.js             Ratings, room/round filtering, and edit interactions
static/style.css             Application styling
static/images/               Branding assets
tests/test_google_sheets.py   Roster, cache, submission, and form tests
tests/test_sessions.py        Cross-browser ownership tests
requirements.txt             Runtime dependency pins
requirements-dev.txt         Runtime and test dependencies
.env.example                 Environment-variable template
USER_GUIDE.md                Administrator and observer instructions
test.py                      Legacy standalone prototype; not used by the app
```
