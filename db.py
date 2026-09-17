"""
lib/db.py — Supabase layer for the 2Peak Growth client portal.

Two rules run through this whole file.

1. Every project lookup is keyed on the verified session email, never on
   anything from a URL. If a client id can come from a query parameter,
   editing the URL is the entire attack.

2. The app authenticates as service_role, which bypasses RLS. That key is
   server-side only and never reaches a browser. It also means scoping is
   this file's job, not Postgres's.
"""
from datetime import datetime

import streamlit as st
from supabase import create_client, Client

from lib import status as S


# ── Client ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client() -> Client:
    cfg = st.secrets.get("supabase", {})
    url = cfg.get("url", "")
    key = cfg.get("service_key", "")

    if not url:
        st.error("Supabase URL missing. Add it to Streamlit secrets.")
        st.stop()

    if not key:
        # A clear message beats a permission error you have to decode.
        if cfg.get("key"):
            st.error(
                "This app now needs the service_role key. Your secrets still "
                "have the old anon key under `key`. Add `service_key` under "
                "[supabase] in Streamlit Cloud settings."
            )
        else:
            st.error("Supabase not configured.")
        st.stop()

    return create_client(url, key)


def _sb() -> Client:
    return get_client()


# ── Authentication ───────────────────────────────────────────────────────────
def project_exists_for_email(email: str) -> bool:
    """
    True if any project is registered to this address.

    The caller must not reveal the answer to the user. Telling someone
    whether an address is on file lets them enumerate your client list.
    """
    if not email:
        return False
    try:
        resp = (_sb().table("website_projects").select("id")
                .eq("portal_email", email.lower().strip())
                .limit(1).execute())
        return bool(resp.data)
    except Exception:
        return False


def send_login_code(email: str) -> bool:
    """
    Ask Supabase Auth to email a six digit code.

    should_create_user is False so this can never mint an account for an
    address that is not already a client.
    """
    try:
        _sb().auth.sign_in_with_otp({
            "email": email.lower().strip(),
            "options": {"should_create_user": False},
        })
        return True
    except Exception:
        return False


def verify_login_code(email: str, code: str) -> bool:
    """Verify the emailed code. Returns True only on a real session."""
    if not code or len(code) < 6:
        return False
    try:
        res = _sb().auth.verify_otp({
            "email": email.lower().strip(),
            "token": code,
            "type": "email",
        })
        return bool(getattr(res, "session", None))
    except Exception:
        return False


# ── Project, scoped to the session ───────────────────────────────────────────
def get_project_for(email: str) -> dict:
    """
    The project belonging to this verified address.

    Every read in the portal starts here. Nothing downstream accepts a
    project id from the page.
    """
    if not email:
        return {}
    try:
        resp = (_sb().table("website_projects").select("*")
                .eq("portal_email", email.lower().strip())
                .order("created_at", desc=True)
                .limit(1).execute())
        return (resp.data or [{}])[0]
    except Exception:
        return {}


def get_business(rc_id: str) -> dict:
    if not rc_id:
        return {}
    try:
        # The column is `name`. `business_name` is web_leads' column,
        # not this table's.
        resp = (_sb().table("businesses")
                .select("rc_id,name,city,phone")
                .eq("rc_id", rc_id).limit(1).execute())
        return (resp.data or [{}])[0]
    except Exception:
        return {}


# ── Intake ───────────────────────────────────────────────────────────────────
def get_intake_for_project(rc_id: str) -> dict:
    if not rc_id:
        return {}
    try:
        resp = (_sb().table("site_intake").select("*")
                .eq("pg_id", rc_id).limit(1).execute())
        return (resp.data or [{}])[0]
    except Exception:
        return {}


def get_intake_by_token(token: str) -> dict:
    """Retained so existing intake links keep working during the switch."""
    if not token:
        return {}
    try:
        resp = (_sb().table("site_intake").select("*")
                .eq("token", token).limit(1).execute())
        return (resp.data or [{}])[0]
    except Exception:
        return {}


def upsert_intake(token: str, updates: dict):
    updates["last_saved"] = datetime.utcnow().isoformat()
    updates["token"] = token

    fields = ["business_name", "phone", "tagline", "color_primary",
              "services", "hours", "logo_url", "domain_preference"]
    filled = sum(1 for f in fields if updates.get(f) or updates.get(f) == [])
    updates["completion_pct"] = int((filled / len(fields)) * 100)

    _sb().table("site_intake").upsert(updates, on_conflict="token").execute()


def mark_intake_complete(token: str):
    (_sb().table("site_intake")
     .update({"status": "complete", "completion_pct": 100,
              "last_saved": datetime.utcnow().isoformat()})
     .eq("token", token).execute())


# ── Change requests ──────────────────────────────────────────────────────────
def get_change_requests(project_id: int) -> list:
    if not project_id:
        return []
    try:
        resp = (_sb().table("change_requests").select("*")
                .eq("project_id", project_id)
                .order("submitted_at", desc=True).execute())
        return resp.data or []
    except Exception:
        return []


def changes_used_this_month(project_id: int) -> int:
    """
    Counted in Postgres rather than by pulling every row and counting in
    Python, which stops working as the history grows.
    """
    if not project_id:
        return 0
    try:
        resp = _sb().rpc("changes_used_this_month",
                         {"p_project_id": project_id}).execute()
        return int(resp.data or 0)
    except Exception:
        return 0


def submit_change_request(project_id: int, rc_id: str, request: str,
                          billable: bool = False, price: float = 0) -> bool:
    """
    billable is decided by the caller from the plan allowance, and stored
    on the row so it does not have to be recomputed later against a plan
    that may since have changed.
    """
    text = (request or "").strip()
    if not text:
        return False
    try:
        _sb().table("change_requests").insert({
            "project_id": project_id,
            "rc_id":      rc_id or None,
            "request":    text[:4000],
            "status":     "new",
            "billable":   bool(billable),
            "price":      float(price or 0),
        }).execute()
        return True
    except Exception:
        return False


def quota_state(project: dict) -> dict:
    """
    Everything the portal needs to show plan usage, in one place, so the
    portal and the CRM cannot disagree about whether a change is billable.
    """
    plan = S.clean(project.get("maintenance_plan"), "none")
    pid = S.clean_int(project.get("id"), 0)
    used = changes_used_this_month(pid)
    quota = S.quota_for(plan)

    return {
        "plan":      plan,
        "used":      used,
        "quota":     quota,                       # None means unlimited
        "remaining": None if quota is None else max(0, quota - used),
        "billable":  False if quota is None else used >= quota,
        "price":     S.PER_CHANGE_PRICE,
    }
