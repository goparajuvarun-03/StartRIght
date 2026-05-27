# StartRight — Streamlit edition

A lightweight Streamlit web app that digitises the CDO's **StartRight** project
initiation process. Replaces the current scatter of emails (checklist updates,
reviews, gap identification, approvals) with a single tool.

## Why this exists

Today, project initiation flows through mailboxes. That causes:

- scattered communication
- no real-time visibility into where a project stands
- difficult progress tracking
- version-control issues on the checklist itself

StartRight puts the whole flow in one place with an audit trail.

## The 4-step flow

| Step | Actor | Activity | Status after |
|------|-------|----------|--------------|
| 1 | Project Manager | Create project + assign stakeholders | **Draft** |
| 2 | Project Manager | Complete checklist + schedule kickoff | **Pending PMO Review** |
| 3 | PMO | Review, raise gap comments → PM closes → resubmits | **Gaps Identified** → back to Pending |
| 4 | PMO | Approve project | **Active** |

Every state change is captured in a per-project activity log.

## Project layout

```
.
├── streamlit_app.py        # Main Streamlit app (all pages in one file)
├── store.py                # JSON file storage (replace with DB for production)
├── checklist_config.py     # PLACEHOLDER checklist — replace with real one
├── requirements.txt
├── .gitignore
└── README.md
```

## Run locally

```bash
git clone https://github.com/<your-org>/startright.git
cd startright
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app opens at http://localhost:8501

## Deploy to Streamlit Community Cloud (free)

1. Push this repo to **GitHub** (public or private — both work).
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Click **New app** → pick your repo → set **Main file path** to
   `streamlit_app.py` → click **Deploy**.
4. The first build takes ~1 minute. You'll get a public URL like
   `https://<your-app>.streamlit.app`.

That's it. Pushes to your `main` branch auto-redeploy.

### Important deployment note

Streamlit Community Cloud has an **ephemeral filesystem** — the `data/` folder
will reset whenever the app sleeps, restarts, or you push a new commit. That is
fine for a demo or pilot. For real usage, swap `store.py` for a database
(see "Going to production" below).

## Demo accounts

| Username | Password | Role |
|----------|----------|------|
| `priya` | `pm123` | Project Manager |
| `rahul` | `pm123` | Project Manager |
| `anita` | `pmo123` | PMO Reviewer |
| `vikram` | `pmo123` | PMO Reviewer |

## End-to-end walkthrough

1. Sign in as **priya** → click **➕ New project** in the sidebar → fill in
   details, pick stakeholders (include a PMO user). The project is saved in
   **Draft**.
2. Open the project → click **Open checklist** → answer each item, attach
   notes/links, schedule the kickoff date+time, then **Submit for PMO review**.
   Status moves to **Pending PMO Review**.
3. Log out and sign in as **anita** (PMO). The project shows up under the
   "Pending Review" tab. Click **Open review** → for any item with a gap,
   type a comment → click **Return with gaps**. Status moves to **Gaps
   Identified**.
4. Sign back in as **priya** → open the project, the PMO gaps are shown at the
   top → click **Address gaps** → update items and resubmit. Status returns to
   **Pending PMO Review**.
5. Sign in as **anita** → review again → click **Approve project**. Status
   becomes **Active** and the approval is recorded.

## Customising the checklist

The placeholder checklist lives in `checklist_config.py`. Replace section
titles and item text with the actual StartRight checklist. Keep the structure
(`section → items` with `id`, `text`, `mandatory`) — no code changes needed.
Mandatory items must be answered **Yes** before submission.

## Going to production

This codebase is a clickable functional prototype. **Do not deploy it as your
production system without addressing each of the following.**

| Area | Demo (current) | Production |
|------|----------------|-----------|
| Auth | Plaintext passwords in JSON, no SSO | SSO (Azure AD / Okta) or hashed (bcrypt/argon2) |
| Storage | JSON files, ephemeral on Streamlit Cloud | PostgreSQL via SQLAlchemy (swap inside `store.py`) |
| Hosting | Streamlit Community Cloud | Self-hosted Streamlit + reverse proxy with HTTPS, or your internal PaaS |
| Notifications | None | Email / Teams / Slack on every status change |
| Audit & compliance | Per-project activity log | Centralised logging to SIEM, CSRF, rate limits, backups, env separation |

The data layer is isolated in `store.py` specifically so swapping JSON for a
real DB is a one-file change.

## Notes

- `data/` is auto-generated on first run; it's ignored by Git.
- The seed user file is healed on every startup, so corrupted local data
  cannot lock you out of the demo accounts.
