"""
StartRight - Streamlit edition
==============================
A single-file Streamlit application that digitises the CDO's StartRight
project-initiation workflow.

    Step 1  Project creation (PM)              -> Draft
    Step 2  Checklist completion + kickoff     -> Pending PMO Review
    Step 3  PMO review (gap comments)          -> Gaps Identified / back to PM
    Step 4  PMO approval                       -> Active

Run locally:        streamlit run streamlit_app.py
Deploy to cloud:    push to GitHub, then on https://share.streamlit.io point
                    a new app at your repo + this file.
"""

import streamlit as st

import store
from checklist_config import CHECKLIST, get_all_items, get_item_by_id


# ---------------------------------------------------------------------------
# Page config + light branding CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="StartRight",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,400..900,0..100&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
    /* =====================================================
       PALETTE - warm editorial, confident colour
       ===================================================== */
    :root {
        --cream:     #F4F6F9;   /* page background - cool light slate */
        --paper:     #E9EDF3;
        --paper-2:   #DDE3EC;
        --line:      #D2D9E3;
        --ink:       #14181F;
        --ink-soft:  #36404F;
        --grey:      #5E6673;
        --grey-soft: #9AA0AC;

        --teal:        #1F4E79;   /* primary - corporate navy-blue */
        --teal-light:  #DCE7F2;
        --terracotta:  #2563A6;   /* secondary action - steel blue */
        --terracotta-light: #DCE7F2;
        --mustard:     #B7791F;   /* amber - in-review */
        --mustard-light: #FBEFD6;
        --forest:      #2F7A4D;   /* green - active/approved */
        --forest-light: #D7EBDF;
        --plum:        #7A3B5C;
        --plum-light:  #EDD4DF;
        --slate:       #334155;   /* sidebar */
    }

    /* =====================================================
       BASE — typography + background
       ===================================================== */
    html, body, [class*="css"], .stApp {
        font-family: 'Manrope', system-ui, sans-serif;
        color: var(--ink);
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 6%,  rgba(31, 78, 121, 0.05) 0%, transparent 42%),
            radial-gradient(circle at 90% 94%, rgba(51, 65, 85, 0.05) 0%, transparent 45%),
            var(--cream);
    }

    h1, h2, h3, h4 {
        font-family: 'Fraunces', Georgia, serif;
        font-weight: 600;
        font-variation-settings: "opsz" 96, "SOFT" 50;
        letter-spacing: -0.015em;
        color: var(--ink);
    }
    h1 { font-weight: 500; font-variation-settings: "opsz" 144, "SOFT" 100; }
    h4 { font-family: 'Manrope', sans-serif; text-transform: uppercase;
         letter-spacing: 0.08em; font-size: 0.78rem; color: var(--grey); }

    /* =====================================================
       BADGES — bright, saturated, joyful
       ===================================================== */
    .sr-badge {
        display: inline-block;
        padding: 4px 13px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        border-radius: 999px;
        border: 1.5px solid;
        font-family: 'Manrope', sans-serif;
    }
    .sr-badge-draft   { background: var(--paper-2);          color: var(--ink-soft);   border-color: var(--line); }
    .sr-badge-review  { background: var(--mustard-light);    color: #8a5a00;           border-color: var(--mustard); }
    .sr-badge-gaps    { background: var(--terracotta-light); color: var(--terracotta); border-color: var(--terracotta); }
    .sr-badge-active  { background: var(--forest-light);     color: var(--forest);     border-color: var(--forest); }

    /* =====================================================
       STEPPER — coloured progress chips
       ===================================================== */
    .sr-step {
        display: inline-block;
        padding: 8px 16px;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1.5px solid var(--line);
        border-radius: 999px;
        font-size: 0.82rem;
        font-family: 'Manrope', sans-serif;
        font-weight: 500;
        background: rgba(255,255,255,0.5);
        color: var(--grey);
        transition: transform 0.15s ease;
    }
    .sr-step b {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        margin-right: 6px;
    }
    .sr-step-done {
        background: var(--forest-light);
        border-color: var(--forest);
        color: var(--forest);
    }
    .sr-step-current {
        background: var(--mustard);
        border-color: var(--mustard);
        color: #fff;
        font-weight: 700;
        box-shadow: 0 6px 18px -6px rgba(217, 160, 60, 0.7);
        transform: translateY(-1px);
    }
    .sr-step-current b { color: #fff; }
    .sr-step-future { background: rgba(255,255,255,0.4); color: var(--grey-soft); border-style: dashed; }

    /* =====================================================
       GAP BOXES — warm coral accent
       ===================================================== */
    .sr-gap-box {
        background: linear-gradient(135deg, var(--terracotta-light), #fef1ea);
        border-left: 4px solid var(--terracotta);
        padding: 10px 14px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 0.88rem;
        color: var(--ink);
        box-shadow: 0 2px 8px rgba(217, 79, 43, 0.08);
    }
    .sr-gap-box b { color: var(--terracotta); }

    .sr-muted { color: var(--grey); font-size: 0.85rem; }

    /* =====================================================
       STREAMLIT WIDGET OVERRIDES
       ===================================================== */
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--ink) 0%, #0e1320 100%);
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not([style*="background"]),
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #F1E9D7 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2 { color: #fff !important; }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: rgba(241, 233, 215, 0.55) !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-size: 0.7rem;
    }
    /* sidebar buttons */
    section[data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.06) !important;
        color: #F1E9D7 !important;
        border: 1px solid rgba(241, 233, 215, 0.18) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(217, 160, 60, 0.15) !important;
        border-color: var(--mustard) !important;
        color: #fff !important;
    }

    /* Primary buttons in main area — bold terracotta */
    .stApp button[kind="primary"],
    .stApp button[data-testid="baseButton-primary"],
    .stApp button[data-testid="stBaseButton-primary"],
    .stApp button[data-testid="stBaseButton-primaryFormSubmit"] {
        background: var(--terracotta) !important;
        border: 1.5px solid var(--terracotta) !important;
        color: #fff !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
        box-shadow: 0 6px 16px -8px rgba(217, 79, 43, 0.6);
        transition: all 0.15s ease;
    }
    .stApp button[kind="primary"]:hover,
    .stApp button[data-testid="baseButton-primary"]:hover,
    .stApp button[data-testid="stBaseButton-primary"]:hover,
    .stApp button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background: #b8401f !important;
        border-color: #b8401f !important;
        box-shadow: 0 10px 22px -8px rgba(217, 79, 43, 0.75);
        transform: translateY(-1px);
    }

    /* Secondary buttons */
    .stApp .main button[kind="secondary"],
    .stApp .main button[data-testid="baseButton-secondary"],
    .stApp .main button[data-testid="stBaseButton-secondary"],
    .stApp .main button[data-testid="stBaseButton-secondaryFormSubmit"] {
        background: #fff !important;
        color: var(--teal) !important;
        border: 1.5px solid var(--teal) !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.15s ease;
    }
    .stApp .main button[kind="secondary"]:hover,
    .stApp .main button[data-testid="baseButton-secondary"]:hover,
    .stApp .main button[data-testid="stBaseButton-secondary"]:hover,
    .stApp .main button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        background: var(--teal-light) !important;
        color: var(--teal) !important;
    }

    /* Cards / containers with borders */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(26, 31, 46, 0.04), 0 8px 24px -12px rgba(26, 31, 46, 0.08);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid var(--line);
        padding-bottom: 0;
        flex-wrap: wrap;            /* let section tabs wrap instead of overflowing */
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 14px;
        font-family: 'Manrope', sans-serif;
        font-weight: 600;
        font-size: 0.86rem;
        color: var(--grey);
        background: #EDF1F6;
        border: 1px solid var(--line);
        border-bottom: none;
        border-radius: 7px 7px 0 0;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--teal);
        background: var(--teal-light);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: var(--teal) !important;
        border-color: var(--teal) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 14px; }

    /* Input fields — force dark, readable text on white */
    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #14181F !important;
        -webkit-text-fill-color: #14181F !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        font-family: 'Manrope', sans-serif !important;
    }
    /* The actual text the user types + selected values in dropdowns */
    .stTextInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input,
    .stNumberInput input {
        caret-color: var(--teal) !important;
    }
    /* placeholder text should be a soft grey, not invisible */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stDateInput input::placeholder,
    .stTimeInput input::placeholder {
        color: #9AA0AC !important;
        -webkit-text-fill-color: #9AA0AC !important;
        opacity: 1 !important;
    }
    /* selected value shown inside select / multiselect pills */
    .stMultiSelect span[data-baseweb="tag"],
    .stMultiSelect span[data-baseweb="tag"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stDateInput input:focus,
    .stTimeInput input:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 3px rgba(31, 78, 121, 0.14) !important;
    }

    /* Field labels */
    .stTextInput label, .stTextArea label, .stDateInput label, .stTimeInput label,
    .stMultiSelect label, .stRadio label, .stSelectbox label {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        color: var(--ink-soft) !important;
        letter-spacing: 0.01em;
    }

    /* Radio buttons in checklist — tight pill style so 4 options fit on one row */
    .stRadio > div { gap: 3px !important; flex-wrap: wrap; }
    .stRadio div[role="radiogroup"] {
        gap: 4px !important;
        flex-wrap: nowrap !important;
    }
    .stRadio div[role="radiogroup"] label {
        background: #fff;
        border: 1.5px solid var(--line);
        padding: 3px 10px !important;
        border-radius: 999px;
        transition: all 0.12s ease;
        cursor: pointer;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        white-space: nowrap;
    }
    .stRadio div[role="radiogroup"] label:hover {
        border-color: var(--teal);
        background: var(--teal-light);
    }

    /* Alerts — warmer palette */
    .stAlert {
        border-radius: 10px !important;
        border-width: 1.5px !important;
        font-family: 'Manrope', sans-serif !important;
    }

    /* Expanders */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {
        font-family: 'Fraunces', serif !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
        color: var(--ink) !important;
    }

    /* Page-top "Welcome" / flash message custom polish */
    [data-testid="stNotificationContentSuccess"] {
        background: var(--forest-light) !important;
        color: var(--forest) !important;
    }
    [data-testid="stNotificationContentWarning"] {
        background: var(--mustard-light) !important;
        color: #8a5a00 !important;
    }
    [data-testid="stNotificationContentError"] {
        background: var(--terracotta-light) !important;
        color: var(--terracotta) !important;
    }
    [data-testid="stNotificationContentInfo"] {
        background: var(--teal-light) !important;
        color: var(--teal) !important;
    }

    /* Stepper container — tight horizontal layout */
    .sr-stepper-wrap {
        margin: 4px 0 8px;
    }

    /* Make project rows feel like editorial cards */
    [data-testid="stVerticalBlockBorderWrapper"] h3 {
        margin-top: 0 !important;
        margin-bottom: 4px !important;
        font-weight: 500 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


STATUS_BADGE_CLASS = {
    store.STATUS_DRAFT:           "sr-badge-draft",
    store.STATUS_PENDING_REVIEW:  "sr-badge-review",
    store.STATUS_GAPS_IDENTIFIED: "sr-badge-gaps",
    store.STATUS_ACTIVE:          "sr-badge-active",
}


def status_badge(status: str) -> str:
    return f'<span class="sr-badge {STATUS_BADGE_CLASS.get(status, "sr-badge-draft")}">{status}</span>'


# ---------------------------------------------------------------------------
# Session-state defaults + navigation helpers
# ---------------------------------------------------------------------------
def init_state():
    st.session_state.setdefault("user", None)         # {"username","name","role"}
    st.session_state.setdefault("page", "dashboard")
    st.session_state.setdefault("current_pid", None)
    st.session_state.setdefault("flash", None)        # ("success"/"error"/"info", "msg")


def go(page: str, pid: str | None = None):
    st.session_state.page = page
    if pid is not None:
        st.session_state.current_pid = pid
    st.rerun()


def flash(category: str, msg: str):
    st.session_state.flash = (category, msg)


def render_flash():
    if st.session_state.flash:
        cat, msg = st.session_state.flash
        if cat == "success": st.success(msg)
        elif cat == "error": st.error(msg)
        elif cat == "info":  st.info(msg)
        elif cat == "warning": st.warning(msg)
        st.session_state.flash = None


init_state()


# ---------------------------------------------------------------------------
# Login page
# ---------------------------------------------------------------------------
def page_login():
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("# StartRight.")
        st.caption("CDO · PROJECT INITIATION WORKFLOW")
        st.markdown(
            "Move project initiation out of **scattered mailboxes** "
            "and into a single space — with checklists, reviews, gap closure "
            "and approvals in one place."
        )
        st.markdown("---")
        st.markdown("**Demo accounts**")
        st.markdown(
            """
            | Username | Password | Role |
            |---|---|---|
            | `priya` | `pm123` | Project Manager |
            | `rahul` | `pm123` | Project Manager |
            | `anita` | `pmo123` | PMO Reviewer |
            | `vikram` | `pmo123` | PMO Reviewer |
            """
        )

    with right:
        st.markdown("## Sign in")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username").strip().lower()
            password = st.text_input("Password", type="password").strip()
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

            if submitted:
                user = store.authenticate(username, password)
                if not user:
                    st.error("Invalid credentials. Try one of the demo accounts on the left.")
                else:
                    st.session_state.user = {
                        "username": username,
                        "name": user["name"],
                        "role": user["role"],
                    }
                    st.session_state.page = "dashboard"
                    flash("success", f"Welcome, {user['name']}.")
                    st.rerun()


# ---------------------------------------------------------------------------
# Sidebar (visible when logged in)
# ---------------------------------------------------------------------------
def render_sidebar():
    u = st.session_state.user
    with st.sidebar:
        st.markdown("## StartRight.")
        st.caption("CDO · Project Initiation")
        role_colour = {"pm": "#D9A03C", "pmo": "#D94F2B"}.get(u["role"], "#F1E9D7")
        st.markdown(
            f"<div style='margin-top: 8px;'><b style='font-size:1rem;'>{u['name']}</b><br>"
            f"<span style='display:inline-block;padding:2px 10px;margin-top:4px;"
            f"background:{role_colour};color:#1A1F2E;border-radius:999px;"
            f"font-size:0.7rem;font-weight:700;letter-spacing:0.1em;'>"
            f"{u['role'].upper()}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        if st.button("📊 Dashboard", use_container_width=True):
            go("dashboard")
        if u["role"] == "pm":
            if st.button("➕ New project", use_container_width=True):
                go("create")
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.session_state.current_pid = None
            flash("info", "You have been logged out.")
            st.rerun()

        with st.expander("ℹ️ About this demo"):
            st.caption(
                "Data is stored in local JSON files. On Streamlit Cloud the "
                "filesystem is ephemeral — projects will reset if the app "
                "restarts. Replace `store.py` with a real DB for production."
            )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def page_dashboard():
    u = st.session_state.user
    projects = store.projects_for_user(u["username"], u["role"])

    st.markdown("# Dashboard")
    st.caption(
        "Projects you manage or are a stakeholder of."
        if u["role"] == "pm"
        else "All projects across the organization."
    )

    buckets = {
        "Draft":              [p for p in projects if p["status"] == store.STATUS_DRAFT],
        "Pending PMO Review": [p for p in projects if p["status"] == store.STATUS_PENDING_REVIEW],
        "Gaps Identified":    [p for p in projects if p["status"] == store.STATUS_GAPS_IDENTIFIED],
        "Active":             [p for p in projects if p["status"] == store.STATUS_ACTIVE],
    }

    tab_labels = [
        f"All ({len(projects)})",
        f"Draft ({len(buckets['Draft'])})",
        f"Pending Review ({len(buckets['Pending PMO Review'])})",
        f"Gaps ({len(buckets['Gaps Identified'])})",
        f"Active ({len(buckets['Active'])})",
    ]
    tab_data = [
        ("all",     projects),
        ("draft",   buckets["Draft"]),
        ("review",  buckets["Pending PMO Review"]),
        ("gaps",    buckets["Gaps Identified"]),
        ("active",  buckets["Active"]),
    ]

    tabs = st.tabs(tab_labels)
    for tab, (key_prefix, data) in zip(tabs, tab_data):
        with tab:
            render_project_list(data, key_prefix=key_prefix)


def render_project_list(items, *, key_prefix=""):
    if not items:
        st.info("No projects in this category yet.")
        return
    for p in items:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 1])
            with c1:
                st.markdown(f"### {p['name']}")
                st.markdown(
                    f"<span class='sr-muted'><b>{p['code']}</b> · "
                    f"Manager: {store.user_name(p['manager'])} · "
                    f"Sponsor: {p['sponsor']} · "
                    f"Updated: {p['updated_at']}</span>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(status_badge(p["status"]), unsafe_allow_html=True)
            with c3:
                # Each project may appear in both the "All" tab AND its status tab
                # so the button key MUST include the tab prefix to stay unique.
                btn_key = f"open_{key_prefix}_{p['id']}"
                if st.button("Open →", key=btn_key, use_container_width=True):
                    go("detail", pid=p["id"])


# ---------------------------------------------------------------------------
# Step 1 - Create project
# ---------------------------------------------------------------------------
def page_create_project():
    if st.session_state.user["role"] != "pm":
        st.error("Only Project Managers can create projects.")
        return

    st.markdown("# Create a new project")
    st.caption("Step 1 of 4 · basic details and stakeholders. Will be saved in **Draft** status.")

    candidates = {**store.list_users("pm"), **store.list_users("pmo")}
    options = list(candidates.keys())
    fmt = lambda u: f"{candidates[u]['name']} ({candidates[u]['role'].upper()})"

    with st.form("create_project_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Project name *")
        code = c2.text_input("Project code *", placeholder="e.g., CDO-2026-014")

        description = st.text_area("Description", height=80,
                                   placeholder="One-line description of the project objective.")

        c1, c2 = st.columns(2)
        sponsor = c1.text_input("Executive sponsor *", placeholder="Name of sponsoring leader")
        business_unit = c2.text_input("Business unit", placeholder="e.g., Data Platform")

        c1, c2 = st.columns(2)
        start_date = c1.date_input("Planned start date", value=None)
        end_date = c2.date_input("Planned end date", value=None)

        stakeholders = st.multiselect(
            "Stakeholders",
            options=options,
            format_func=fmt,
            help="Include PMO reviewers and team members who should see this project.",
        )

        c1, c2 = st.columns([1, 1])
        cancel = c1.form_submit_button("Cancel", use_container_width=True)
        submit = c2.form_submit_button("Create project (Draft)", type="primary",
                                       use_container_width=True)

        if cancel:
            go("dashboard")
        if submit:
            if not name or not code or not sponsor:
                st.error("Project name, project code, and sponsor are required.")
            else:
                proj = store.create_project(
                    name=name, code=code, description=description,
                    manager_username=st.session_state.user["username"],
                    sponsor=sponsor, business_unit=business_unit,
                    start_date=start_date, end_date=end_date,
                    stakeholders=stakeholders,
                )
                flash("success", f"Project '{proj['name']}' created in Draft. Complete the checklist next.")
                go("detail", pid=proj["id"])


# ---------------------------------------------------------------------------
# Project detail view (read-only summary + entry points)
# ---------------------------------------------------------------------------
def render_stepper(status):
    """Render the 4-step workflow indicator."""
    steps = [
        ("Step 1", "Project created", True),
        ("Step 2", "Checklist & kickoff", status in (
            store.STATUS_PENDING_REVIEW, store.STATUS_GAPS_IDENTIFIED, store.STATUS_ACTIVE
        )),
        ("Step 3", "PMO review", status in (store.STATUS_GAPS_IDENTIFIED, store.STATUS_ACTIVE)),
        ("Step 4", "Approval · Active", status == store.STATUS_ACTIVE),
    ]
    current_idx = {
        store.STATUS_DRAFT:             1,
        store.STATUS_PENDING_REVIEW:    2,
        store.STATUS_GAPS_IDENTIFIED:   1,
        store.STATUS_ACTIVE:           -1,
    }.get(status, -1)

    html = '<div class="sr-stepper-wrap">'
    for i, (num, title, done) in enumerate(steps):
        if i == current_idx:
            cls = "sr-step sr-step-current"
        elif done:
            cls = "sr-step sr-step-done"
        else:
            cls = "sr-step sr-step-future"
        html += f'<span class="{cls}"><b>{num}</b> &middot; {title}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def page_project_detail():
    pid = st.session_state.current_pid
    p = store.get_project(pid) if pid else None
    if not p:
        st.error("Project not found.")
        if st.button("Back to dashboard"):
            go("dashboard")
        return

    u = st.session_state.user
    open_gaps = store.open_gaps(p)

    # ----- header -----
    head_l, head_r = st.columns([4, 1])
    with head_l:
        st.markdown(f"# {p['name']}")
        st.caption(
            f"**{p['code']}** · Manager: {store.user_name(p['manager'])} · Created {p['created_at']}"
        )
    with head_r:
        st.markdown(status_badge(p["status"]), unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            go("dashboard")

    render_stepper(p["status"])
    st.markdown("")

    # ----- contextual call-to-action -----
    if p["status"] == store.STATUS_DRAFT and u["username"] == p["manager"]:
        c = st.container(border=True)
        c.warning("**Next action:** Complete the initiation checklist and schedule the kickoff with PMO and team.")
        if c.button("Open checklist →", type="primary"):
            go("checklist", pid=pid)
    elif p["status"] == store.STATUS_PENDING_REVIEW and u["role"] == "pmo":
        c = st.container(border=True)
        c.info("**Next action:** Review the checklist, raise gap comments, or approve to make Active.")
        if c.button("Open review →", type="primary"):
            go("review", pid=pid)
    elif p["status"] == store.STATUS_PENDING_REVIEW:
        st.info("The checklist is with the PMO team for review.")
    elif p["status"] == store.STATUS_GAPS_IDENTIFIED and u["username"] == p["manager"]:
        c = st.container(border=True)
        c.warning(f"**Next action:** PMO has raised **{len(open_gaps)} gap(s)**. Address them in the checklist and resubmit.")
        if c.button("Address gaps →", type="primary"):
            go("checklist", pid=pid)
    elif p["status"] == store.STATUS_ACTIVE:
        appr = p.get("approval") or {}
        msg = f"**Project is Active.** Approved by **{store.user_name(appr.get('by', '—'))}** on {appr.get('at', '—')}."
        if appr.get("remarks"):
            msg += f"  \n_\"{appr['remarks']}\"_"
        st.success(msg)

    # ----- two-column layout -----
    main, side = st.columns([2, 1], gap="large")

    with main:
        with st.container(border=True):
            st.markdown("### Project details")
            st.write(p["description"] or "—")
            c1, c2 = st.columns(2)
            c1.markdown(f"**Sponsor**  \n{p['sponsor'] or '—'}")
            c2.markdown(f"**Business unit**  \n{p['business_unit'] or '—'}")
            c1.markdown(f"**Planned start**  \n{p['start_date'] or '—'}")
            c2.markdown(f"**Planned end**  \n{p['end_date'] or '—'}")
            c1.markdown(f"**Project manager**  \n{store.user_name(p['manager'])}")
            c2.markdown(f"**Review round**  \n{p['review_round']}")

        with st.container(border=True):
            st.markdown("### Stakeholders")
            if not p.get("stakeholders"):
                st.markdown("<span class='sr-muted'>No stakeholders added.</span>", unsafe_allow_html=True)
            else:
                for s in p["stakeholders"]:
                    su = store.get_user(s) or {"name": s, "role": "?"}
                    st.markdown(f"- **{su['name']}**  ·  _{su['role'].upper()}_")

        with st.container(border=True):
            head_l, head_r = st.columns([3, 1])
            head_l.markdown("### Checklist summary")
            if p["status"] in (store.STATUS_DRAFT, store.STATUS_GAPS_IDENTIFIED) and u["username"] == p["manager"]:
                if head_r.button("Edit checklist", key="edit_cl_btn"):
                    go("checklist", pid=pid)

            if open_gaps:
                st.markdown("**Open gaps raised by PMO:**")
                for g in open_gaps:
                    item = get_item_by_id(g["item_id"])
                    label = item["text"] if item else g["item_id"]
                    st.markdown(
                        f"<div class='sr-gap-box'><b>{label}:</b> {g['comment']}"
                        f"<br><span class='sr-muted'>{store.user_name(g['raised_by'])} · {g['raised_at']}</span></div>",
                        unsafe_allow_html=True,
                    )
                st.markdown("")

            for section in CHECKLIST:
                with st.expander(section["section"], expanded=False):
                    for item in section["items"]:
                        resp = p["checklist"].get(item["id"], {"response": "", "note": ""})
                        label_map = {"yes": "✅ Yes", "no": "❌ No", "na": "➖ N/A", "": "⏳ Pending"}
                        line = f"**{item['text']}**"
                        if item["mandatory"]:
                            line += " <span style='color:#a4282c'>*</span>"
                        st.markdown(line + f"  \n{label_map.get(resp['response'], '⏳ Pending')}",
                                    unsafe_allow_html=True)
                        if resp["note"]:
                            st.caption(f"Note: {resp['note']}")

            st.markdown("---")
            c1, c2 = st.columns(2)
            c1.markdown(f"**Kickoff scheduled**  \n{p['kickoff_at'] or '—'}")
            c2.markdown(f"**Kickoff notes**  \n{p['kickoff_notes'] or '—'}")

    with side:
        with st.container(border=True):
            st.markdown("### Activity")
            for h in reversed(p.get("history", [])):
                st.markdown(
                    f"<span class='sr-muted'>{h['at']}</span>  \n"
                    f"**{store.user_name(h['actor'])}** · {h['event']}",
                    unsafe_allow_html=True,
                )
                st.markdown("---")


# ---------------------------------------------------------------------------
# Step 2 - Checklist edit (PM)
# ---------------------------------------------------------------------------
def page_checklist():
    pid = st.session_state.current_pid
    p = store.get_project(pid) if pid else None
    u = st.session_state.user

    if not p:
        st.error("Project not found.")
        return
    if p["manager"] != u["username"]:
        st.error("Only the project manager can edit the checklist.")
        if st.button("← Back to project"):
            go("detail", pid=pid)
        return
    if p["status"] not in (store.STATUS_DRAFT, store.STATUS_GAPS_IDENTIFIED):
        st.info("Checklist can only be edited in Draft or Gaps Identified status.")
        if st.button("← Back to project"):
            go("detail", pid=pid)
        return

    head_l, head_r = st.columns([4, 1])
    head_l.markdown("# Initiation Checklist")
    head_l.caption(f"{p['name']} · **{p['code']}**")
    head_l.markdown(status_badge(p["status"]), unsafe_allow_html=True)
    if head_r.button("← Back to project"):
        go("detail", pid=pid)

    open_gaps_list = store.open_gaps(p)
    if open_gaps_list:
        with st.container(border=True):
            st.warning(f"**{len(open_gaps_list)} open gap(s) raised by PMO** — please address before resubmitting.")
            for g in open_gaps_list:
                item = get_item_by_id(g["item_id"])
                label = item["text"] if item else g["item_id"]
                st.markdown(
                    f"- **{label}:** {g['comment']}  \n"
                    f"  <span class='sr-muted'>{store.user_name(g['raised_by'])} · {g['raised_at']}</span>",
                    unsafe_allow_html=True,
                )

    gap_item_ids = {g["item_id"] for g in open_gaps_list}

    with st.form("checklist_form"):
        responses = {}
        resp_options = ["—", "Yes", "No", "N/A"]
        resp_to_value = {"—": "", "Yes": "yes", "No": "no", "N/A": "na"}
        value_to_resp = {v: k for k, v in resp_to_value.items()}

        st.markdown(
            "<p class='sr-muted'>Complete each section using the tabs below. "
            "Items marked <span style='color:#B7791F;font-weight:700;'>*</span> are mandatory "
            "and must be answered <b>Yes</b> before you can submit.</p>",
            unsafe_allow_html=True,
        )

        # Build short tab labels: section number + a flag if it has any open gaps.
        def short_label(section, idx):
            num = section["section"].split(".")[0].strip()
            # short keyword from the section name
            name = section["section"].split(".", 1)[1].strip() if "." in section["section"] else section["section"]
            words = name.split()
            short = " ".join(words[:2])
            has_gap = any(it["id"] in gap_item_ids for it in section["items"])
            flag = " ⚠️" if has_gap else ""
            return f"{num}. {short}{flag}"

        section_tabs = st.tabs(
            [short_label(s, i) for i, s in enumerate(CHECKLIST)] + ["📅 Kickoff"]
        )

        # ---- one tab per checklist section ----
        for tab, section in zip(section_tabs[:-1], CHECKLIST):
            with tab:
                st.markdown(f"##### {section['section']}")
                for item in section["items"]:
                    current = p["checklist"].get(item["id"], {"response": "", "note": ""})
                    current_label = value_to_resp.get(current["response"], "—")

                    pieces = []
                    if item["id"] in gap_item_ids:
                        pieces.append('<span style="margin-right:6px;">⚠️</span>')
                    pieces.append(f'<b>{item["text"]}</b>')
                    if item["mandatory"]:
                        pieces.append('<span style="color:#B7791F;font-weight:700;margin-left:4px;">*</span>')
                    label_html = "".join(pieces)

                    with st.container(border=True):
                        st.markdown(label_html, unsafe_allow_html=True)
                        c1, c2 = st.columns([2, 3])
                        chosen = c1.radio(
                            "Response",
                            resp_options,
                            index=resp_options.index(current_label),
                            key=f"resp_{item['id']}",
                            horizontal=True,
                            label_visibility="collapsed",
                        )
                        note = c2.text_input(
                            "Note / evidence link",
                            value=current["note"],
                            key=f"note_{item['id']}",
                            placeholder="Reference document, link, or note",
                            label_visibility="collapsed",
                        )

                        for g in open_gaps_list:
                            if g["item_id"] == item["id"]:
                                st.markdown(
                                    f"<div class='sr-gap-box'><b>PMO gap · {store.user_name(g['raised_by'])} · {g['raised_at']}</b>"
                                    f"<br>{g['comment']}</div>",
                                    unsafe_allow_html=True,
                                )

                    responses[item["id"]] = {"response": resp_to_value[chosen], "note": note.strip()}

        # ---- final tab: kickoff meeting ----
        with section_tabs[-1]:
            st.markdown("##### Kickoff Meeting")
            c1, c2 = st.columns(2)
            from datetime import date as _date, time as _time, datetime as _dt
            existing_date = None
            existing_time = None
            if p.get("kickoff_at"):
                try:
                    dt = _dt.fromisoformat(p["kickoff_at"])
                    existing_date = dt.date()
                    existing_time = dt.time()
                except (ValueError, TypeError):
                    pass
            kickoff_date = c1.date_input("Kickoff date *", value=existing_date, key="ko_date")
            kickoff_time = c2.time_input("Kickoff time *", value=existing_time, key="ko_time")
            kickoff_notes = st.text_area(
                "Kickoff notes",
                value=p.get("kickoff_notes", ""),
                placeholder="Agenda, meeting link, attendees..."
            )

        # ---- submit bar (outside the tabs, always visible at the bottom) ----
        st.markdown("---")
        st.caption("Items marked * are mandatory and must be answered Yes before submission.")

        c1, c2, _ = st.columns([1, 1, 2])
        save_clicked = c1.form_submit_button("💾 Save draft", use_container_width=True)
        submit_clicked = c2.form_submit_button("✅ Submit for PMO review",
                                               type="primary", use_container_width=True)

        if save_clicked or submit_clicked:
            kickoff_iso = ""
            if kickoff_date and kickoff_time:
                kickoff_iso = _dt.combine(kickoff_date, kickoff_time).isoformat(timespec="minutes")
            elif kickoff_date:
                kickoff_iso = kickoff_date.isoformat()

            if submit_clicked:
                missing = []
                for item in get_all_items():
                    if item["mandatory"] and responses[item["id"]]["response"] != "yes":
                        missing.append(item["text"])
                if not kickoff_iso:
                    missing.append("Kickoff date/time must be scheduled")

                if missing:
                    store.save_checklist(pid, responses, kickoff_iso, kickoff_notes.strip(),
                                         actor=u["username"], submit=False)
                    msg = "Cannot submit — these mandatory items are incomplete: "
                    msg += "; ".join(missing[:5])
                    if len(missing) > 5:
                        msg += f" ... (+{len(missing) - 5} more)"
                    flash("error", msg)
                    st.rerun()
                else:
                    store.save_checklist(pid, responses, kickoff_iso, kickoff_notes.strip(),
                                         actor=u["username"], submit=True)
                    flash("success", "Checklist submitted to PMO for review.")
                    go("detail", pid=pid)
            else:
                store.save_checklist(pid, responses, kickoff_iso, kickoff_notes.strip(),
                                     actor=u["username"], submit=False)
                flash("success", "Checklist progress saved.")
                st.rerun()


# ---------------------------------------------------------------------------
# Step 3 & 4 - PMO review
# ---------------------------------------------------------------------------
def page_review():
    pid = st.session_state.current_pid
    p = store.get_project(pid) if pid else None
    u = st.session_state.user

    if not p:
        st.error("Project not found.")
        return
    if u["role"] != "pmo":
        st.error("Only PMO members can review projects.")
        if st.button("← Back"):
            go("detail", pid=pid)
        return
    if p["status"] != store.STATUS_PENDING_REVIEW:
        st.info("This project is not pending PMO review.")
        if st.button("← Back to project"):
            go("detail", pid=pid)
        return

    head_l, head_r = st.columns([4, 1])
    head_l.markdown("# PMO Review")
    head_l.caption(
        f"{p['name']} · **{p['code']}** · Submitted by {store.user_name(p['manager'])} · Round {p['review_round']}"
    )
    if head_r.button("← Back to project"):
        go("detail", pid=pid)

    with st.container(border=True):
        st.markdown("**How to review:**")
        st.markdown(
            "1. Walk through each checklist item in the kickoff meeting.  \n"
            "2. Where you identify a gap, type a comment in the box below that item.  \n"
            "3. Click **Return with gaps** — the PM will close the gaps and resubmit.  \n"
            "4. Once everything is satisfactory, click **Approve project** to make it Active."
        )

    c1, c2 = st.columns(2)
    c1.markdown(f"**Sponsor**  \n{p['sponsor']}")
    c2.markdown(f"**Business unit**  \n{p['business_unit'] or '—'}")
    c1.markdown(f"**Kickoff scheduled**  \n{p['kickoff_at'] or '—'}")
    c2.markdown(f"**Kickoff notes**  \n{p['kickoff_notes'] or '—'}")
    st.markdown("---")

    with st.form("review_form"):
        gap_inputs = {}

        def short_label_r(section):
            num = section["section"].split(".")[0].strip()
            name = section["section"].split(".", 1)[1].strip() if "." in section["section"] else section["section"]
            short = " ".join(name.split()[:2])
            return f"{num}. {short}"

        review_tabs = st.tabs([short_label_r(s) for s in CHECKLIST] + ["✔ Decision"])

        for tab, section in zip(review_tabs[:-1], CHECKLIST):
            with tab:
                st.markdown(f"##### {section['section']}")
                for item in section["items"]:
                    resp = p["checklist"].get(item["id"], {"response": "", "note": ""})
                    resp_label = {"yes": "✅ Yes", "no": "❌ No", "na": "➖ N/A", "": "⏳ Pending"}.get(resp["response"], "⏳")

                    with st.container(border=True):
                        line = f"**{item['text']}**"
                        if item["mandatory"]:
                            line += " <span style='color:#B7791F;font-weight:700;'>*</span>"
                        st.markdown(f"{line}  &nbsp;&nbsp; {resp_label}", unsafe_allow_html=True)
                        if resp["note"]:
                            st.caption(f"PM note: {resp['note']}")

                        gap_inputs[item["id"]] = st.text_area(
                            "Raise gap / comment (leave empty if none)",
                            key=f"gap_{item['id']}",
                            placeholder="Describe the gap or what needs to be corrected...",
                            height=68,
                        )

                        for g in p.get("gaps", []):
                            if g["item_id"] == item["id"]:
                                tag = " · resolved by PM" if g.get("resolved") else ""
                                st.markdown(
                                    f"<div class='sr-gap-box'><b>Previous gap · "
                                    f"{store.user_name(g['raised_by'])} · {g['raised_at']}{tag}</b>"
                                    f"<br>{g['comment']}</div>",
                                    unsafe_allow_html=True,
                                )

        with review_tabs[-1]:
            st.markdown("##### Decision")
            remarks = st.text_area("Approval / return remarks (optional)", height=68,
                                   placeholder="Overall comments...")

        c1, c2 = st.columns(2)
        return_clicked = c1.form_submit_button("↩️ Return with gaps", use_container_width=True)
        approve_clicked = c2.form_submit_button("✅ Approve project", type="primary",
                                                use_container_width=True)

        if return_clicked:
            gaps = [{"item_id": iid, "comment": txt.strip()}
                    for iid, txt in gap_inputs.items() if txt.strip()]
            if not gaps:
                flash("error", "Add at least one gap comment, or use Approve if no gaps exist.")
                st.rerun()
            else:
                store.submit_review(pid, gaps=gaps, actor=u["username"], approve=False)
                flash("success", f"{len(gaps)} gap(s) raised. Project returned to PM.")
                go("detail", pid=pid)

        if approve_clicked:
            store.submit_review(pid, gaps=[], actor=u["username"],
                                approve=True, remarks=remarks.strip())
            flash("success", "Project approved. Status is now Active.")
            go("detail", pid=pid)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
def main():
    if st.session_state.user is None:
        render_flash()
        page_login()
        return

    render_sidebar()
    render_flash()

    page = st.session_state.page
    if page == "dashboard":
        page_dashboard()
    elif page == "create":
        page_create_project()
    elif page == "detail":
        page_project_detail()
    elif page == "checklist":
        page_checklist()
    elif page == "review":
        page_review()
    else:
        page_dashboard()


main()
