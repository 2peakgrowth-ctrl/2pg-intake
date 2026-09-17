"""
pages/Done.py — Completion confirmation.

Now offers a way back into the portal rather than being a dead end, since
the client has somewhere to go: their project page, where they can track
the build and send change requests.
"""
import streamlit as st

st.set_page_config(
    page_title="2Peak Growth · All Done",
    page_icon="✅", layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stSidebarNav"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 3rem; max-width: 600px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:32px 20px 8px">
  <div style="font-size:56px;margin-bottom:16px">✅</div>
  <div style="font-size:26px;font-weight:800;color:#1A1A1A;
              font-family:-apple-system,sans-serif;margin-bottom:12px">
    You're all set
  </div>
  <div style="font-size:15px;color:#6B7280;line-height:1.6;max-width:440px;
              margin:0 auto 32px">
    We have your intake form and will start building. Expect to hear from
    us within 2 business days with a preview link.
  </div>
  <div style="background:#F8F8F8;border-radius:8px;padding:20px;
              font-size:14px;color:#374151;text-align:left;max-width:400px;
              margin:0 auto">
    <div style="font-weight:600;margin-bottom:8px">What happens next</div>
    <div style="margin-bottom:6px">1. We review your intake details</div>
    <div style="margin-bottom:6px">2. We build your site draft</div>
    <div style="margin-bottom:6px">3. You get a preview link to review</div>
    <div>4. Final adjustments, then your site goes live</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Only offer the portal route to someone who actually signed in. A client
# who arrived on an old intake link has no session to go back to.
if st.session_state.get("portal_email"):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Go to my project page", type="primary",
                     use_container_width=True):
            st.switch_page("pages/Portal.py")
    st.markdown(
        '<div style="text-align:center;font-size:13px;color:#9CA3AF;'
        'padding-top:10px">Track your build and send change requests '
        'from there any time.</div>',
        unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:32px 0 0">
  <div style="font-size:13px;color:#9CA3AF;line-height:1.7">
    Questions? Call or text <strong style="color:#374151">(425) 494-1518</strong><br>
    <a href="mailto:2peakgrowth@gmail.com"
       style="color:#1A1A1A;font-weight:600">2peakgrowth@gmail.com</a>
  </div>
  <div style="margin-top:44px;font-size:22px;font-weight:800;color:#1A1A1A">
    2Peak Growth
  </div>
</div>
""", unsafe_allow_html=True)
