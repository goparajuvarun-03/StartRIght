"""
StartRight - In-Memory Data Store with JSON Persistence
=======================================================
No database. Data lives in two JSON files under ./data/.

IMPORTANT FOR STREAMLIT CLOUD:
Streamlit Community Cloud has an EPHEMERAL filesystem - files written here
are preserved while the app process is alive but are wiped when the app
restarts (which happens on push, on inactivity, on platform maintenance).
For a demo / pilot this is acceptable. For production, replace this module
with a real DB (Postgres + SQLAlchemy etc).
"""

import json
import os
import threading
from datetime import datetime
from uuid import uuid4

from checklist_config import default_responses

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

_lock = threading.Lock()

DEFAULT_USERS = {
    "priya":   {"password": "pm123",  "name": "Priya Sharma",  "role": "pm",  "email": "priya.sharma@example.com"},
    "rahul":   {"password": "pm123",  "name": "Rahul Verma",   "role": "pm",  "email": "rahul.verma@example.com"},
    "anita":   {"password": "pmo123", "name": "Anita Reddy",   "role": "pmo", "email": "anita.reddy@example.com"},
    "vikram":  {"password": "pmo123", "name": "Vikram Singh",  "role": "pmo", "email": "vikram.singh@example.com"},
}


def _ensure_files():
    """Always make sure users.json contains the demo accounts and
    projects.json is a valid dict, even if a prior run left junk on disk."""
    os.makedirs(DATA_DIR, exist_ok=True)

    existing_users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                existing_users = json.load(f)
                if not isinstance(existing_users, dict):
                    existing_users = {}
        except (json.JSONDecodeError, OSError):
            existing_users = {}
    merged = {**existing_users}
    for uname, u in DEFAULT_USERS.items():
        merged[uname] = u
    with open(USERS_FILE, "w") as f:
        json.dump(merged, f, indent=2)

    rewrite_projects = not os.path.exists(PROJECTS_FILE)
    if not rewrite_projects:
        try:
            with open(PROJECTS_FILE, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    rewrite_projects = True
        except (json.JSONDecodeError, OSError):
            rewrite_projects = True
    if rewrite_projects:
        with open(PROJECTS_FILE, "w") as f:
            json.dump({}, f, indent=2)


def _load(path):
    """Load JSON file. If missing or corrupt, re-create defaults and retry."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("not a dict")
            return data
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        _ensure_files()
        with open(path, "r") as f:
            return json.load(f)


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)


_ensure_files()


# ---------------------------------------------------------------------------
# User API
# ---------------------------------------------------------------------------
def get_user(username):
    users = _load(USERS_FILE)
    return users.get(username)


def list_users(role=None):
    users = _load(USERS_FILE)
    if role:
        return {u: data for u, data in users.items() if data["role"] == role}
    return users


def authenticate(username, password):
    user = get_user(username)
    if user and user["password"] == password:
        return user
    return None


def user_name(username):
    u = get_user(username)
    return u["name"] if u else username


# ---------------------------------------------------------------------------
# Project API
# ---------------------------------------------------------------------------
STATUS_DRAFT             = "Draft"
STATUS_PENDING_REVIEW    = "Pending PMO Review"
STATUS_GAPS_IDENTIFIED   = "Gaps Identified"
STATUS_ACTIVE            = "Active"


def _now():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def create_project(*, name, code, description, manager_username,
                   sponsor, business_unit, start_date, end_date, stakeholders):
    with _lock:
        projects = _load(PROJECTS_FILE)
        pid = uuid4().hex[:8]
        projects[pid] = {
            "id": pid,
            "name": name,
            "code": code,
            "description": description,
            "manager": manager_username,
            "sponsor": sponsor,
            "business_unit": business_unit,
            "start_date": str(start_date) if start_date else "",
            "end_date": str(end_date) if end_date else "",
            "stakeholders": stakeholders,
            "status": STATUS_DRAFT,
            "created_at": _now(),
            "updated_at": _now(),
            "kickoff_at": "",
            "kickoff_notes": "",
            "checklist": default_responses(),
            "gaps": [],
            "history": [{"at": _now(), "actor": manager_username, "event": "Project created in Draft status"}],
            "review_round": 0,
            "approval": None,
        }
        _save(PROJECTS_FILE, projects)
        return projects[pid]


def get_project(pid):
    projects = _load(PROJECTS_FILE)
    return projects.get(pid)


def all_projects():
    projects = _load(PROJECTS_FILE)
    return sorted(projects.values(), key=lambda p: p["created_at"], reverse=True)


def projects_for_user(username, role):
    items = all_projects()
    if role == "pmo":
        return items
    return [p for p in items if p["manager"] == username or username in p.get("stakeholders", [])]


def save_checklist(pid, responses, kickoff_at, kickoff_notes, *, actor, submit=False):
    with _lock:
        projects = _load(PROJECTS_FILE)
        proj = projects[pid]
        proj["checklist"] = responses
        proj["kickoff_at"] = kickoff_at
        proj["kickoff_notes"] = kickoff_notes
        proj["updated_at"] = _now()

        if submit:
            proj["status"] = STATUS_PENDING_REVIEW
            proj["review_round"] += 1
            for gap in proj.get("gaps", []):
                gap["resolved"] = True
            event = f"Submitted for PMO review (round {proj['review_round']})"
        else:
            event = "Checklist saved as draft"

        proj.setdefault("history", []).append({"at": _now(), "actor": actor, "event": event})
        _save(PROJECTS_FILE, projects)
        return proj


def submit_review(pid, gaps, *, actor, approve=False, remarks=""):
    with _lock:
        projects = _load(PROJECTS_FILE)
        proj = projects[pid]

        if approve:
            proj["status"] = STATUS_ACTIVE
            proj["approval"] = {"by": actor, "at": _now(), "remarks": remarks}
            event = "Project approved - status moved to Active"
        else:
            for g in gaps:
                proj.setdefault("gaps", []).append({
                    "item_id": g["item_id"],
                    "comment": g["comment"],
                    "raised_by": actor,
                    "raised_at": _now(),
                    "resolved": False,
                })
            proj["status"] = STATUS_GAPS_IDENTIFIED
            event = f"Review submitted with {len(gaps)} gap(s) - returned to PM"

        proj["updated_at"] = _now()
        proj.setdefault("history", []).append({"at": _now(), "actor": actor, "event": event})
        _save(PROJECTS_FILE, projects)
        return proj


def open_gaps(project):
    return [g for g in project.get("gaps", []) if not g.get("resolved")]
