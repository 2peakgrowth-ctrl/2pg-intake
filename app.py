"""
2Peak Growth — Client Site Intake
Entry point — routes to intake form via token URL parameter.
URL format: start.2peakgrowth.com/?token=abc123
"""
import streamlit as st
from lib import db

st.set_page_config(
    page_title="2Peak Growth — Site Intake",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome — clients see only the form
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stSidebarNav"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 2rem; max-width: 720px; }
  [data-testid="stAppViewContainer"] { background: #ffffff; }
</style>
""", unsafe_allow_html=True)

# ── Brand header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 32px">
  <div style="font-size:22px;font-weight:800;color:#1A1A1A;
              font-family:-apple-system,sans-serif;letter-spacing:-0.5px">
    2Peak Growth
  </div>
  <div style="font-size:13px;color:#6B7280;margin-top:4px">
    Website intake form
  </div>
</div>
""", unsafe_allow_html=True)

# ── Token from URL ────────────────────────────────────────────────────────────
params = st.query_params
token  = params.get("token", "")

if not token:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#6B7280">
      <div style="font-size:48px">🔗</div>
      <div style="font-size:18px;font-weight:600;color:#1A1A1A;margin:16px 0 8px">
        No intake link detected
      </div>
      <div style="font-size:14px">
        You should have received a personal link from 2Peak Growth.<br>
        Please check your messages or contact us at
        <a href="mailto:hello@2peakgrowth.com" style="color:#1A1A1A">
        hello@2peakgrowth.com</a>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load intake record ────────────────────────────────────────────────────────
intake = db.get_intake_by_token(token)
if not intake:
    st.error("This intake link is invalid or has expired. "
             "Please contact 2Peak Growth.")
    st.stop()

status = intake.get("status","in_progress")

if status == "complete":
    st.switch_page("pages/Done.py")
else:
    st.switch_page("pages/Intake.py")
