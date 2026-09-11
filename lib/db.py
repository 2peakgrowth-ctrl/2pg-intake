"""
lib/db.py — Supabase client for 2pg-intake app.
Reads/writes site_intake table only.
"""
import streamlit as st
from supabase import create_client, Client
from datetime import datetime


@st.cache_resource
def get_client() -> Client:
    cfg = st.secrets.get("supabase", {})
    return create_client(cfg["url"], cfg["key"])


def _sb():
    return get_client()


def get_intake_by_token(token: str) -> dict:
    resp = (_sb().table("site_intake")
            .select("*").eq("token", token).single().execute())
    return resp.data or {}


def upsert_intake(token: str, updates: dict):
    updates["last_saved"] = datetime.utcnow().isoformat()
    updates["token"]      = token
    # Calculate completion %
    fields = [
        "business_name","phone","tagline","color_primary",
        "services","hours","logo_url","domain_preference",
    ]
    filled = sum(1 for f in fields
                 if updates.get(f) or (updates.get(f) == []))
    updates["completion_pct"] = int((filled / len(fields)) * 100)
    (_sb().table("site_intake")
     .upsert(updates, on_conflict="token").execute())


def create_intake(pg_id: str) -> str:
    """Create a new intake record and return its token."""
    resp = (_sb().table("site_intake")
            .insert({"pg_id": pg_id}).execute())
    return resp.data[0]["token"] if resp.data else ""


def mark_complete(token: str):
    (_sb().table("site_intake")
     .update({"status": "complete", "completion_pct": 100,
               "last_saved": datetime.utcnow().isoformat()})
     .eq("token", token).execute())
