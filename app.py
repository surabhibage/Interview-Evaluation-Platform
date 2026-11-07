from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Literal, Optional
from datetime import datetime
import os
import uuid
import json
import logging
import secrets
from time import monotonic
from threading import Lock
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_spreadsheet():
    credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return gspread.authorize(credentials).open_by_key(os.environ["GOOGLE_SHEET_ID"])


def get_sheet():
    title = os.environ["GOOGLE_OBSERVATIONS_SHEET_NAME"].strip()
    if not title:
        raise ValueError("GOOGLE_OBSERVATIONS_SHEET_NAME must not be empty")
    interviewees_title = os.environ["GOOGLE_INTERVIEWEES_SHEET_NAME"].strip()
    if title == interviewees_title:
        raise ValueError("Observations and interviewees must use different tabs")
    return get_spreadsheet().worksheet(title)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CANDIDATE_CACHE_SECONDS = 60
_candidate_cache = {"key": None, "groups": [[], [], []], "error": None, "expires_at": 0}
_candidate_cache_lock = Lock()


def parse_candidate_rows(rows):
    required = [
        (f"Group {group} First Name", f"Group {group} Last Name")
        for group in "ABC"
    ]
    if not rows:
        raise ValueError("Interviewees tab is empty")
    headers = [str(value).strip() for value in rows[0]]
    if any(headers.count(header) != 1 for pair in required for header in pair):
        raise ValueError("Interviewees tab requires unique Group A/B/C First Name and Last Name headers")
    groups = []
    assigned = set()
    for pair in required:
        first_index, last_index = (headers.index(header) for header in pair)
        names = set()
        for row in rows[1:]:
            first = str(row[first_index]).strip() if first_index < len(row) else ""
            last = str(row[last_index]).strip() if last_index < len(row) else ""
            name = f"{first} {last}".strip()
            if name:
                names.add(name)
        if assigned & names:
            raise ValueError("A candidate appears in more than one group")
        assigned.update(names)
        groups.append(sorted(names))
    return groups


def candidate_data():
    # Throttle retries as well as successful reads; never use CSV or sample names.
    key = (os.getenv("GOOGLE_SHEET_ID"), os.getenv("GOOGLE_INTERVIEWEES_SHEET_NAME"))
    with _candidate_cache_lock:
        if _candidate_cache["key"] != key:
            _candidate_cache.update(key=key, groups=[[], [], []], error=None, expires_at=0)
        if monotonic() >= _candidate_cache["expires_at"]:
            try:
                title = (key[1] or "").strip()
                if not title:
                    raise ValueError("GOOGLE_INTERVIEWEES_SHEET_NAME must be set")
                rows = get_spreadsheet().worksheet(title).get_all_values()
                groups = parse_candidate_rows(rows)
                _candidate_cache.update(
                    groups=groups,
                    error=None if any(groups) else "The interviewees tab contains no candidate names. Add names below the headers.",
                )
            except Exception:
                logger.exception("Unable to load interviewee names from Google Sheets")
                message = (
                    "Could not refresh interviewee names. Check the Google Sheets connection, "
                    "GOOGLE_INTERVIEWEES_SHEET_NAME, and the six Group A/B/C First Name / "
                    "Last Name headers. Each candidate must appear in only one group."
                )
                if any(_candidate_cache["groups"]):
                    message += " Showing the last successfully loaded list."
                _candidate_cache["error"] = message + " Retrying on a page load after 60 seconds."
            _candidate_cache["expires_at"] = monotonic() + CANDIDATE_CACHE_SECONDS
        return [list(group) for group in _candidate_cache["groups"]], _candidate_cache["error"]


# Keep each preassigned group together as it rotates through all three rooms.
def get_round_room_assignments():
    (group_a, group_b, group_c), _ = candidate_data()

    return {
        "Round 1": {
            "Tinker Toys": sorted(group_c),
            "Mini Lessons": sorted(group_a),
            "Scenarios": sorted(group_b)
        },
        "Round 2": {
            "Tinker Toys": sorted(group_b),
            "Mini Lessons": sorted(group_c),
            "Scenarios": sorted(group_a)
        },
        "Round 3": {
            "Tinker Toys": sorted(group_a),
            "Mini Lessons": sorted(group_b),
            "Scenarios": sorted(group_c)
        }
    }

def format_score(val: float):
    return int(val) if val.is_integer() else val

# Drafts are private to an opaque browser session, never a shared visitor list.
_browser_drafts = {}
SESSION_COOKIE = "observation_session"


@app.middleware("http")
async def browser_session(request: Request, call_next):
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id or session_id not in _browser_drafts:
        session_id = secrets.token_urlsafe(32)
        _browser_drafts[session_id] = []
    request.state.observations = _browser_drafts[session_id]
    response = await call_next(request)
    response.set_cookie(
        SESSION_COOKIE, session_id, httponly=True, samesite="strict",
        secure=request.url.scheme == "https", path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return response


def get_observations(request):
    return request.state.observations


def get_observations_by_round(observations):
    rounds = ["Round 1", "Round 2", "Round 3"]
    return {
        r: [obs for obs in reversed(observations) if obs.get("round") == r]
        for r in rounds
    }

def count_pending(observations):
    return sum(1 for obs in observations if not obs.get("submitted_to_sheets"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    observations = get_observations(request)
    assignments = get_round_room_assignments()
    observed_names = [obs["candidate"] for obs in observations]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "assignments_json": json.dumps(assignments),
            "names_error": candidate_data()[1],
            "observations": observations,
            "observations_by_round": get_observations_by_round(observations),
            "observed_names": observed_names,
            "pending_count": count_pending(observations),
            "success_msg": None,
            "error_msg": None,
            "last_observer": "",
            "last_room": "Tinker Toys",
            "last_round": "Round 1"
        }
    )

@app.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    edit_id: Optional[str] = Form(None),
    observer_name: str = Form(...),
    profstaff: Literal["Yes", "No"] = Form(...),
    room: str = Form(...),
    round_num: str = Form(..., alias="round"),
    candidate: str = Form(...),
    teamwork: float = Form(...),
    initiative: float = Form(...),
    personal_rep: float = Form(...),
    work_with: Optional[str] = Form("Yes"),
    comments: Optional[str] = Form("")
):
    observations = get_observations(request)
    entry_data = {
        "observer_name": observer_name.strip(),
        "profstaff": profstaff,
        "room": room,
        "round": round_num,
        "candidate": candidate,
        "teamwork": format_score(teamwork),
        "initiative": format_score(initiative),
        "personal_rep": format_score(personal_rep),
        "work_with": work_with,
        "comments": comments.strip() if comments else "",
        "submitted_to_sheets": False
    }

    if edit_id:
        # Update existing observation
        updated = False
        for obs in observations:
            if obs.get("id") == edit_id:
                obs.update(entry_data)
                obs["submitted_to_sheets"] = False
                updated = True
                break
        if not updated:
            raise HTTPException(status_code=404, detail="Observation not found")
        msg = f"Updated draft observation for {candidate}!"
    else:
        # Create new observation with unique id
        entry_data["id"] = uuid.uuid4().hex[:8]
        observations.append(entry_data)
        msg = f"Draft observation for {candidate} ({round_num}, {room}) saved!"

    assignments = get_round_room_assignments()
    observed_names = [obs["candidate"] for obs in observations]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "assignments_json": json.dumps(assignments),
            "names_error": candidate_data()[1],
            "observations": observations,
            "observations_by_round": get_observations_by_round(observations),
            "observed_names": observed_names,
            "pending_count": count_pending(observations),
            "success_msg": msg,
            "error_msg": None,
            "last_observer": observer_name.strip(),
            "last_profstaff": profstaff,
            "last_room": room,
            "last_round": round_num
        }
    )

@app.post("/delete/{obs_id}", response_class=HTMLResponse)
async def delete_observation(request: Request, obs_id: str):
    observations = get_observations(request)
    deleted_candidate = ""
    for obs in observations:
        if obs.get("id") == obs_id:
            deleted_candidate = obs.get("candidate", "")
            break
    if not any(obs.get("id") == obs_id for obs in observations):
        raise HTTPException(status_code=404, detail="Observation not found")
    observations[:] = [obs for obs in observations if obs.get("id") != obs_id]

    assignments = get_round_room_assignments()
    observed_names = [obs["candidate"] for obs in observations]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "assignments_json": json.dumps(assignments),
            "names_error": candidate_data()[1],
            "observations": observations,
            "observations_by_round": get_observations_by_round(observations),
            "observed_names": observed_names,
            "pending_count": count_pending(observations),
            "success_msg": f"Deleted observation for {deleted_candidate}.",
            "error_msg": None,
            "last_observer": "",
            "last_room": "Tinker Toys",
            "last_round": "Round 1"
        }
    )

@app.post("/final-submit", response_class=HTMLResponse)
async def final_submit(request: Request):
    observations = get_observations(request)
    pending = [obs for obs in observations if not obs.get("submitted_to_sheets")]

    if not pending:
        msg = None
        err = "No pending observations to submit to Google Sheets."
    else:
        try:
            sheet = get_sheet()
            if sheet is None:
                raise RuntimeError("Google Sheets connection returned no worksheet")
            rows_to_insert = []
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for obs in pending:
                rows_to_insert.append([
                    now_str,
                    obs["candidate"],
                    obs["round"],
                    obs["room"],
                    obs["observer_name"],
                    obs["teamwork"],
                    obs["initiative"],
                    obs["personal_rep"],
                    obs["work_with"],
                    obs["comments"],
                    obs.get("profstaff", "")
                ])

            sheet.append_rows(
                rows_to_insert,
                value_input_option="RAW",
                insert_data_option="INSERT_ROWS",
                table_range="A1:K",
            )
            for obs in pending:
                obs["submitted_to_sheets"] = True

            msg = f"🎉 Success! All {len(rows_to_insert)} observation(s) have been permanently submitted to Google Sheets!"
            err = None
        except Exception as e:
            print("Failed to connect or submit to Google Sheets:", e)
            msg = None
            err = (
                "Could not connect or submit to Google Sheets. Check GOOGLE_CREDENTIALS "
                "and GOOGLE_SHEET_ID, check GOOGLE_OBSERVATIONS_SHEET_NAME and "
                "GOOGLE_INTERVIEWEES_SHEET_NAME, confirm the Google Sheets API is enabled, and "
                "share the spreadsheet with the service account as an Editor. "
                "Your drafts have been kept; please try again."
            )

    assignments = get_round_room_assignments()
    observed_names = [obs["candidate"] for obs in observations]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "assignments_json": json.dumps(assignments),
            "names_error": candidate_data()[1],
            "observations": observations,
            "observations_by_round": get_observations_by_round(observations),
            "observed_names": observed_names,
            "pending_count": count_pending(observations),
            "success_msg": msg,
            "error_msg": err,
            "last_observer": "",
            "last_room": "Tinker Toys",
            "last_round": "Round 1"
        }
    )
