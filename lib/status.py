"""
lib/status.py — Single source of truth for status vocabulary.

Shared by the CRM and the client portal. Both apps import from here, so a
label can never mean one thing internally and another to the client.

Why this file exists: a status list was duplicated across five places, one
fell behind, and a page crashed with ValueError when the database returned
a value it had never heard of.
"""
import math

# ── Lead pipeline (web_leads.status) ─────────────────────────────────────────
LEAD_STATUSES = ["new", "contacted", "pending", "converted", "dead"]

LEAD_LABEL = {
    "new":       "Untouched",
    "contacted": "Contacted",
    "pending":   "Waiting on them",
    "converted": "Signed up",
    "dead":      "Not interested",
}

LEAD_COLOR = {
    "new":       "#3B82F6",
    "contacted": "#6B7280",
    "pending":   "#F59E0B",
    "converted": "#22C55E",
    "dead":      "#374151",
}

# 'converted' is set by the system when a lead becomes a business record,
# never chosen from a menu.
LEAD_EDITABLE = ["new", "contacted", "pending", "dead"]


# ── Website build stages (website_projects.status) ───────────────────────────
SITE_STATUSES = [
    "not_started", "gathering_info", "building",
    "client_review", "live", "on_hold", "cancelled",
]

# Internal labels, for the CRM.
SITE_LABEL = {
    "not_started":    "Not started",
    "gathering_info": "Gathering info",
    "building":       "Building",
    "client_review":  "With client",
    "live":           "Live",
    "on_hold":        "On hold",
    "cancelled":      "Cancelled",
}

# Client-facing labels, for the portal. Deliberately different from the
# internal set: a stage where the client has to do something says so in the
# label itself rather than making them infer it. "With client" is accurate
# from your desk and useless from theirs.
SITE_CLIENT_LABEL = {
    "not_started":    "Not started yet",
    "gathering_info": "We need your info",
    "building":       "We're building it",
    "client_review":  "Your review needed",
    "live":           "Live",
    "on_hold":        "On hold",
    "cancelled":      "Cancelled",
}

# Stages where the project cannot move without the client. The portal uses
# this to decide whether to show the action banner, so adding a blocking
# stage later takes one edit here and nowhere else.
SITE_NEEDS_CLIENT = {"gathering_info", "client_review"}

# What the client should actually do, per blocking stage.
SITE_CLIENT_ACTION = {
    "gathering_info": (
        "Fill out your intake form",
        "We can't start building until we know about your business. It saves "
        "as you go, so you don't have to finish in one sitting."),
    "client_review": (
        "Look over your preview and tell us what to change",
        "Your site is built and waiting. Open the preview, then send any "
        "changes below. Two rounds of changes are included."),
}

SITE_COLOR = {
    "not_started":    "#6B7280",
    "gathering_info": "#F59E0B",
    "building":       "#3B82F6",
    "client_review":  "#F59E0B",
    "live":           "#22C55E",
    "on_hold":        "#78716C",
    "cancelled":      "#374151",
}

# Progress rail order. on_hold and cancelled are off-ramps, not steps.
SITE_SEQUENCE = [
    "not_started", "gathering_info", "building", "client_review", "live",
]


# ── Tiers ────────────────────────────────────────────────────────────────────
TIERS = ["basic", "pro", "custom"]

TIER_LABEL  = {"basic": "Basic", "pro": "Pro", "custom": "Custom"}
TIER_DETAIL = {
    "basic":  "Up to 2 pages · $300",
    "pro":    "Up to 4 pages · $500",
    "custom": "Quoted per project",
}
TIER_PAGES  = {"basic": 2, "pro": 4, "custom": None}


# ── Change requests (change_requests.status) ─────────────────────────────────
CR_STATUSES = ["new", "in_progress", "done", "declined"]

CR_LABEL = {
    "new":         "Received",
    "in_progress": "In progress",
    "done":        "Done",
    "declined":    "Not doing",
}

CR_COLOR = {
    "new":         "#3B82F6",
    "in_progress": "#F59E0B",
    "done":        "#22C55E",
    "declined":    "#6B7280",
}


# ── Maintenance plans ────────────────────────────────────────────────────────
PLANS = ["none", "basic", "unlimited"]

PLAN_LABEL = {
    "none":      "No plan",
    "basic":     "Basic · $10/mo",
    "unlimited": "Unlimited · $25/mo",
}

# Changes included per month. None means unlimited.
PLAN_QUOTA = {"none": 0, "basic": 2, "unlimited": None}

# Charged per change once the monthly allowance is used, or with no plan.
PER_CHANGE_PRICE = 15


# ── Payments (website_projects.payment_status) ───────────────────────────────
PAY_STATUSES = ["unpaid", "deposit_paid", "paid", "refunded"]

PAY_LABEL = {
    "unpaid":       "Not paid",
    "deposit_paid": "Deposit paid",
    "paid":         "Paid in full",
    "refunded":     "Refunded",
}

PAY_COLOR = {
    "unpaid":       "#6B7280",
    "deposit_paid": "#F59E0B",
    "paid":         "#22C55E",
    "refunded":     "#374151",
}


# ── Safe lookups ─────────────────────────────────────────────────────────────
# Never call list.index() on a value from the database. It raises ValueError
# on anything unexpected and takes the page down with it.

def safe_index(options: list, value, default: int = 0) -> int:
    try:
        return options.index(value)
    except (ValueError, AttributeError):
        return default


def lead_label(s):        return LEAD_LABEL.get(str(s), str(s or "Unknown"))
def lead_color(s):        return LEAD_COLOR.get(str(s), "#6B7280")
def site_label(s):        return SITE_LABEL.get(str(s), str(s or "Unknown"))
def site_client_label(s): return SITE_CLIENT_LABEL.get(str(s), str(s or "Unknown"))
def site_color(s):        return SITE_COLOR.get(str(s), "#6B7280")
def tier_label(s):        return TIER_LABEL.get(str(s), str(s or "Unknown"))
def cr_label(s):          return CR_LABEL.get(str(s), str(s or "Unknown"))
def cr_color(s):          return CR_COLOR.get(str(s), "#6B7280")
def plan_label(s):        return PLAN_LABEL.get(str(s), str(s or "No plan"))
def pay_label(s):         return PAY_LABEL.get(str(s), str(s or "Unknown"))
def pay_color(s):         return PAY_COLOR.get(str(s), "#6B7280")


def needs_client(status) -> bool:
    """True when the project cannot move without the client."""
    return str(status) in SITE_NEEDS_CLIENT


def client_action(status):
    """(headline, explanation) for a blocking stage, or None."""
    return SITE_CLIENT_ACTION.get(str(status))


def quota_for(plan):
    """Changes included per month. None means unlimited."""
    return PLAN_QUOTA.get(str(plan), 0)


# ── NaN-safe value cleaning ──────────────────────────────────────────────────
# pandas turns SQL NULL into float('nan'), and a non-zero float is truthy, so
# `nan or ""` evaluates to nan and renders as the text "nan". Falsiness cannot
# catch NaN. It has to be tested for directly.

def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() in ("", "nan", "None", "NaT")


def clean(value, default: str = "") -> str:
    return default if is_blank(value) else str(value).strip()


def clean_int(value, default=None):
    """Nullable INTEGER columns come back as floats: 31 renders as 31.0."""
    if is_blank(value):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def clean_money(value, default=0.0) -> float:
    if is_blank(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
