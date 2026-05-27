"""
StartRight - Predefined Checklist Configuration
================================================
This file contains the project initiation checklist used in Step 2.

NOTE FOR THE TEAM:
These are PLACEHOLDER items. Replace each item's `id`, `text`, and the section
titles with the actual StartRight checklist once it is finalized. The structure
(sections -> items) and the field names (id, text, mandatory) must stay the
same so the rest of the application keeps working without code changes.

Each item supports three response states: 'yes', 'no', 'na', plus a free-text
note. If `mandatory` is True the item must be answered 'yes' before the
checklist can be submitted for PMO review.
"""

CHECKLIST = [
    {
        "section": "1. Project Charter & Scope",
        "items": [
            {"id": "cs_01", "text": "Business case document prepared and signed off by sponsor", "mandatory": True},
            {"id": "cs_02", "text": "Project scope statement finalized (in-scope / out-of-scope clearly defined)", "mandatory": True},
            {"id": "cs_03", "text": "Success criteria and measurable KPIs defined", "mandatory": True},
            {"id": "cs_04", "text": "Project objectives aligned with organizational OKRs", "mandatory": False},
        ],
    },
    {
        "section": "2. Stakeholders & Governance",
        "items": [
            {"id": "sg_01", "text": "Stakeholder register prepared with roles and contact details", "mandatory": True},
            {"id": "sg_02", "text": "RACI matrix prepared and shared with all stakeholders", "mandatory": True},
            {"id": "sg_03", "text": "Steering committee identified and meeting cadence agreed", "mandatory": False},
            {"id": "sg_04", "text": "Escalation path documented", "mandatory": True},
        ],
    },
    {
        "section": "3. Resources, Budget & Procurement",
        "items": [
            {"id": "rb_01", "text": "Budget approved by finance and CDO office", "mandatory": True},
            {"id": "rb_02", "text": "Core project team identified and onboarded", "mandatory": True},
            {"id": "rb_03", "text": "Required tools, licenses, and infrastructure procured", "mandatory": False},
            {"id": "rb_04", "text": "Vendor / partner contracts signed (if applicable)", "mandatory": False},
        ],
    },
    {
        "section": "4. Risk, Compliance & Data",
        "items": [
            {"id": "rc_01", "text": "Initial risk register prepared with mitigation owners", "mandatory": True},
            {"id": "rc_02", "text": "Regulatory and compliance review completed", "mandatory": True},
            {"id": "rc_03", "text": "Data privacy / DPIA review completed", "mandatory": True},
            {"id": "rc_04", "text": "Information security review completed", "mandatory": True},
        ],
    },
    {
        "section": "5. Schedule, Plan & Communication",
        "items": [
            {"id": "sp_01", "text": "High-level project plan with milestones prepared", "mandatory": True},
            {"id": "sp_02", "text": "Kickoff meeting scheduled with PMO and all team members", "mandatory": True},
            {"id": "sp_03", "text": "Communication plan documented (cadence, channels, audience)", "mandatory": False},
            {"id": "sp_04", "text": "Reporting templates and dashboards identified", "mandatory": False},
        ],
    },
]


def get_all_items():
    items = []
    for section in CHECKLIST:
        for item in section["items"]:
            items.append({**item, "section": section["section"]})
    return items


def get_item_by_id(item_id):
    for item in get_all_items():
        if item["id"] == item_id:
            return item
    return None


def default_responses():
    return {
        item["id"]: {"response": "", "note": ""}
        for item in get_all_items()
    }
