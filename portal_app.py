"""
app.py — 2Peak Growth client portal

Entry point and authentication gate. Replaces the old token-in-URL
routing.

Why an emailed code and not a clickable magic link
--------------------------------------------------
A magic link returns its tokens in the URL fragment (#access_token=...).
Fragments never reach the server, and Streamlit renders server-side, so
the app cannot read them. Supabase's email OTP sends a 6 digit code
instead, verified server-side. Same security property, and it works when
a client is on the phone with you and cannot find the email.

Why not a PG ID
---------------
PG-20260902-0187 is a date plus a counter. Anyone holding one could type
PG-20260902-0186 and land in someone else's portal. The PG ID is shown
inside the portal as a reference number, never used as a credential.
"""
import streamlit as st

from lib import db

st.set_page_config(
    page_title="2Peak Growth · Your Project",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Clients see the portal, not Streamlit.
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stSidebarNav"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 2rem; max-width: 760px; }
  [data-testid="stAppViewContainer"] { background: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:24px 0 8px">
  <div style="font-size:22px;font-weight:800;color:#1A1A1A;
              font-family:-apple-system,sans-serif;letter-spacing:-0.5px">
    2Peak Growth
  </div>
  <div style="font-size:13px;color:#6B7280;margin-top:4px">
    Your project
  </div>
</div>
""", unsafe_allow_html=True)


# ── Already signed in ────────────────────────────────────────────────────────
if st.session_state.get("portal_email"):
    st.switch_page("pages/Portal.py")


# ── Step 1: email ────────────────────────────────────────────────────────────
if not st.session_state.get("otp_sent"):
    st.markdown("""
    <div style="text-align:center;padding:24px 0 8px;color:#6B7280;font-size:15px">
      Enter the email address we have on file and we will send you a
      six digit code.
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("Email address", placeholder="you@example.com",
                          label_visibility="collapsed")

    if st.button("Send me a code", type="primary", use_container_width=True):
        addr = (email or "").strip().lower()
        if "@" not in addr or "." not in addr:
            st.error("That does not look like an email address.")
            st.stop()

        # Only send to an address that actually has a project. The message
        # below is deliberately the same either way: confirming which
        # addresses exist would let someone enumerate your client list.
        if db.project_exists_for_email(addr):
            ok = db.send_login_code(addr)
            if not ok:
                st.error("We could not send the code just now. "
                         "Please try again, or call us on (425) 494-1518.")
                st.stop()

        st.session_state["otp_sent"] = True
        st.session_state["otp_email"] = addr
        st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:28px 0 0;color:#9CA3AF;font-size:13px">
      Not sure which email we have? Call or text
      <strong>(425) 494-1518</strong>.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Step 2: code ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:20px 0 4px;color:#6B7280;font-size:15px">
  If <strong>{st.session_state['otp_email']}</strong> is on file, a six digit
  code is on its way. It expires in a few minutes.
</div>
""", unsafe_allow_html=True)

code = st.text_input("Code", placeholder="123456", max_chars=6,
                     label_visibility="collapsed")

c1, c2 = st.columns([2, 1])

with c1:
    if st.button("Sign in", type="primary", use_container_width=True):
        addr = st.session_state["otp_email"]
        if db.verify_login_code(addr, (code or "").strip()):
            st.session_state["portal_email"] = addr
            st.session_state.pop("otp_sent", None)
            st.session_state.pop("otp_email", None)
            st.rerun()
        else:
            st.error("That code did not work. Check it and try again, "
                     "or request a new one.")

with c2:
    if st.button("Start over", use_container_width=True):
        st.session_state.pop("otp_sent", None)
        st.session_state.pop("otp_email", None)
        st.rerun()
