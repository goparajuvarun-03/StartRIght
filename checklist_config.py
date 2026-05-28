"""
StartRight - Predefined Checklist Configuration
================================================
Project initiation checklist used in Step 2 of the StartRight workflow.

Source: SR template.docx (CDO StartRight)
Last updated: 28 May 2026

Structure
---------
CHECKLIST is a list of sections. Each section has:
    section : str   - section heading shown to the user
    items   : list  - one entry per checklist item, each with:
        id        : str  - short unique code. NEVER reuse an old id.
        text      : str  - item text shown to the user
        mandatory : bool - must be answered 'Yes' before submission if True

To edit later
-------------
- Rename an item's text: keep the same id, change `text`. Existing projects
  keep their saved Yes/No answer.
- Add an item: append it with a fresh id (e.g., cs_07).
- Remove an item: delete the entry. Old projects' saved answers for that id
  sit unused in the JSON; the UI just stops showing it.
- Change mandatory: flip True/False. Affects projects still in Draft or
  Gaps Identified; already-Active projects are not re-evaluated.

Mandatory defaults
------------------
The template did not specify which items are mandatory, so the defaults below
reflect a reasonable starting set (commercial signoff, scope, SLAs, escalation,
security, PO funding, change control). Adjust as the PMO directs by flipping
`mandatory` to True/False for any item.
"""

CHECKLIST = [
    {
        "section": "1. Commercial and Scope Readiness",
        "items": [
            {"id": "cs_01", "text": "Signed MSA/SoW reviewed and filed",                              "mandatory": True},
            {"id": "cs_02", "text": "Service scope defined (roles, skills, exclusions)",              "mandatory": True},
            {"id": "cs_03", "text": "Engagement model confirmed (Capacity-based / T&M / Retainer)",   "mandatory": True},
            {"id": "cs_04", "text": "Rate cards and billing terms validated",                         "mandatory": True},
            {"id": "cs_05", "text": "Ramp-up / ramp-down terms agreed",                               "mandatory": True},
            {"id": "cs_06", "text": "Success metrics defined",                                        "mandatory": True},
        ],
    },
    {
        "section": "2. Resource and Delivery Readiness",
        "items": [
            {"id": "rd_01", "text": "Skill profiles (JDs) validated",                                 "mandatory": True},
            {"id": "rd_02", "text": "Fulfillment SLA confirmed",                                      "mandatory": True},
            {"id": "rd_03", "text": "Onboarding process agreed",                                      "mandatory": True},
            {"id": "rd_04", "text": "Offboarding and replacement SLAs defined",                       "mandatory": True},
            {"id": "rd_05", "text": "Escalation matrix finalized",                                    "mandatory": True},
        ],
    },
    {
        "section": "3. Governance and Operational Model",
        "items": [
            {"id": "go_01", "text": "Governance cadence defined",                                     "mandatory": True},
            {"id": "go_02", "text": "KPIs / SLAs baselined",                                          "mandatory": True},
            {"id": "go_03", "text": "Communication channels defined",                                 "mandatory": True},
            {"id": "go_04", "text": "Risk and dependency log created",                                "mandatory": True},
            {"id": "go_05", "text": "Performance cycles established",                                 "mandatory": True},
        ],
    },
    {
        "section": "4. Customer Environment Readiness",
        "items": [
            {"id": "ce_01", "text": "Access provisioning validated",                                  "mandatory": True},
            {"id": "ce_02", "text": "Customer Manager(s) identified",                                 "mandatory": True},
            {"id": "ce_03", "text": "Location model confirmed",                                       "mandatory": True},
            {"id": "ce_04", "text": "Security / compliance reviewed",                                 "mandatory": True},
            {"id": "ce_05", "text": "KT (knowledge transfer) expectations captured",                  "mandatory": True},
        ],
    },
    {
        "section": "5. Financial and Commercial Governance",
        "items": [
            {"id": "fg_01", "text": "PO / funding confirmation received",                             "mandatory": True},
            {"id": "fg_02", "text": "Billing cadence and workflow agreed",                            "mandatory": True},
            {"id": "fg_03", "text": "Timesheet workflow defined",                                     "mandatory": True},
            {"id": "fg_04", "text": "Financial tracking established",                                 "mandatory": True},
            {"id": "fg_05", "text": "Change control documented",                                      "mandatory": True},
        ],
    },
]


def get_all_items():
    """Flatten checklist into a list of items for validation / iteration."""
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
    """Return a fresh response dict with all items unanswered."""
    return {
        item["id"]: {"response": "", "note": ""}
        for item in get_all_items()
    }
