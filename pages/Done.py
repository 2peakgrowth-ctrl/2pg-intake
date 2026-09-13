"""
pages/Done.py — Completion confirmation page
"""
import streamlit as st

st.set_page_config(
    page_title="2Peak Growth — All Done!",
    page_icon="✅", layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 4rem; max-width: 600px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:40px 20px">
  <div style="font-size:56px;margin-bottom:16px">✅</div>
  <div style="font-size:26px;font-weight:800;color:#1A1A1A;
              font-family:-apple-system,sans-serif;margin-bottom:12px">
    You're all set!
  </div>
  <div style="font-size:15px;color:#6B7280;line-height:1.6;max-width:440px;
              margin:0 auto 32px">
    We've received your intake form and will start building your website.
    We'll be in touch within 2 business days with a preview link.
  </div>
  <div style="background:#F8F8F8;border-radius:8px;padding:20px;
              font-size:14px;color:#374151;text-align:left;max-width:400px;
              margin:0 auto">
    <div style="font-weight:600;margin-bottom:8px">What happens next:</div>
    <div style="margin-bottom:6px">1. We review your intake details</div>
    <div style="margin-bottom:6px">2. We build your site draft</div>
    <div style="margin-bottom:6px">3. You get a preview link to review</div>
    <div>4. Final adjustments → your site goes live</div>
  </div>
  <div style="margin-top:32px;font-size:13px;color:#9CA3AF">
    Questions? Email us at
    <a href="mailto:2peakgrowth@gmail.com"
       style="color:#1A1A1A;font-weight:600">2peakgrowth@gmail.com</a>
  </div>
  <div style="margin-top:48px;font-size:22px;font-weight:800;color:#1A1A1A">
    2Peak Growth
  </div>
</div>
""", unsafe_allow_html=True)
