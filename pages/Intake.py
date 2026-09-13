"""
pages/Intake.py — Client site intake form with auto-save progress
"""
import streamlit as st
import json
from lib import db

st.set_page_config(
    page_title="2Peak Growth — Your Website Intake",
    page_icon="🌐", layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stSidebarNav"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 1.5rem; max-width: 720px; }
  .section-header {
    font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #6B7280;
    border-bottom: 1px solid #E5E7EB;
    padding-bottom: 8px; margin: 32px 0 20px;
  }
  .progress-bar-outer {
    background: #F3F4F6; border-radius: 99px;
    height: 6px; margin-bottom: 8px;
  }
  .progress-bar-inner {
    background: #1A1A1A; border-radius: 99px; height: 6px;
  }
  .save-note { font-size: 12px; color: #9CA3AF; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Load via token ────────────────────────────────────────────────────────────
token  = st.query_params.get("token","")
if not token:
    st.error("No intake link. Please use the link provided by 2Peak Growth.")
    st.stop()

intake = db.get_intake_by_token(token)
if not intake:
    st.error("Invalid or expired link.")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:8px 0 24px">
  <div style="font-size:22px;font-weight:800;color:#1A1A1A">2Peak Growth</div>
  <div style="font-size:15px;color:#6B7280;margin-top:4px">
    Tell us about your business
  </div>
</div>
""", unsafe_allow_html=True)

# Progress bar
pct = int(intake.get("completion_pct", 0))
st.markdown(
    f'<div class="progress-bar-outer">'
    f'<div class="progress-bar-inner" style="width:{pct}%"></div></div>'
    f'<div class="save-note">Progress: {pct}% complete · '
    f'Your answers save automatically</div>',
    unsafe_allow_html=True,
)

# ── Helper — auto-save on change ─────────────────────────────────────────────
def _save(key: str, value):
    """Save a single field to Supabase."""
    if value != intake.get(key):
        db.upsert_intake(token, {key: value})
        intake[key] = value   # update local state to avoid redundant saves

# ── Section 1: Business Basics ───────────────────────────────────────────────
st.markdown('<div class="section-header">1 — Business Basics</div>',
            unsafe_allow_html=True)

biz_name = st.text_input(
    "Business name *",
    value=intake.get("business_name",""),
    placeholder="Maria's Nail Studio",
)
if biz_name != intake.get("business_name",""):
    _save("business_name", biz_name)

tagline = st.text_input(
    "Tagline or slogan (optional)",
    value=intake.get("tagline",""),
    placeholder="Professional nails, relaxing experience",
)
if tagline != intake.get("tagline",""):
    _save("tagline", tagline)

c1, c2 = st.columns(2)
with c1:
    phone = st.text_input("Phone number *",
        value=intake.get("phone",""), placeholder="(253) 555-0100")
    if phone != intake.get("phone",""):
        _save("phone", phone)
with c2:
    email = st.text_input("Email address",
        value=intake.get("email",""), placeholder="hello@yourbusiness.com")
    if email != intake.get("email",""):
        _save("email", email)

address = st.text_input("Business address *",
    value=intake.get("address",""),
    placeholder="123 Main St, Renton, WA 98055")
if address != intake.get("address",""):
    _save("address", address)

about = st.text_area("About your business",
    value=intake.get("about_text",""),
    placeholder="Tell customers who you are, how long you've been open, "
                "what makes you different...",
    height=100)
if about != intake.get("about_text",""):
    _save("about_text", about)

# ── Section 2: Services ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">2 — Services</div>',
            unsafe_allow_html=True)

st.caption("List your main services, one per line.")
existing_services = intake.get("services", [])
if isinstance(existing_services, str):
    try: existing_services = json.loads(existing_services)
    except: existing_services = []
services_text = st.text_area(
    "Services (one per line) *",
    value="\n".join(existing_services) if existing_services else "",
    placeholder="Gel nails\nAcrylic nails\nPedicure\nNail art",
    height=120, label_visibility="collapsed",
)
services_list = [s.strip() for s in services_text.split("\n")
                 if s.strip()]
if services_list != existing_services:
    _save("services", services_list)

hours = st.text_input("Business hours",
    value=intake.get("hours",""),
    placeholder="Mon–Sat 9am–7pm, Sun 10am–5pm")
if hours != intake.get("hours",""):
    _save("hours", hours)

# ── Section 3: Brand ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">3 — Brand & Colors</div>',
            unsafe_allow_html=True)

st.caption(
    "Don't worry if you don't have colors picked out — we can help you choose. "
    "If you have brand colors, enter them as hex codes (e.g. #2563EB) "
    "or describe them (e.g. 'navy blue and gold')."
)
b1, b2, b3 = st.columns(3)
with b1:
    c_primary = st.text_input("Primary color",
        value=intake.get("color_primary",""), placeholder="#1A1A1A or 'dark navy'")
    if c_primary != intake.get("color_primary",""):
        _save("color_primary", c_primary)
with b2:
    c_secondary = st.text_input("Secondary color",
        value=intake.get("color_secondary",""), placeholder="#F8F8F8 or 'light gray'")
    if c_secondary != intake.get("color_secondary",""):
        _save("color_secondary", c_secondary)
with b3:
    c_accent = st.text_input("Accent color",
        value=intake.get("color_accent",""), placeholder="#2563EB or 'sky blue'")
    if c_accent != intake.get("color_accent",""):
        _save("color_accent", c_accent)

font_pref = st.text_input("Font or style preference (optional)",
    value=intake.get("font_preference",""),
    placeholder="Modern and clean / Elegant and traditional / Bold and energetic")
if font_pref != intake.get("font_preference",""):
    _save("font_preference", font_pref)

# ── Section 4: Logo & Photos ──────────────────────────────────────────────────
st.markdown('<div class="section-header">4 — Logo & Photos</div>',
            unsafe_allow_html=True)

st.info(
    "📎 **To upload your logo and photos:** Send them to "
    "**hello@2peakgrowth.com** with your business name in the subject line. "
    "We'll add them to your site."
)

logo_url = st.text_input(
    "Logo URL (if you have one hosted online)",
    value=intake.get("logo_url",""),
    placeholder="https://... (optional — you can email it instead)")
if logo_url != intake.get("logo_url",""):
    _save("logo_url", logo_url)

# ── Section 5: Social & Online ────────────────────────────────────────────────
st.markdown('<div class="section-header">5 — Social & Online Presence</div>',
            unsafe_allow_html=True)

s1, s2 = st.columns(2)
with s1:
    instagram = st.text_input("Instagram handle",
        value=intake.get("instagram",""), placeholder="@yourbusiness")
    if instagram != intake.get("instagram",""):
        _save("instagram", instagram.lstrip("@"))

    facebook = st.text_input("Facebook page",
        value=intake.get("facebook",""), placeholder="facebook.com/yourbusiness")
    if facebook != intake.get("facebook",""):
        _save("facebook", facebook)
with s2:
    tiktok = st.text_input("TikTok",
        value=intake.get("tiktok",""), placeholder="@yourbusiness")
    if tiktok != intake.get("tiktok",""):
        _save("tiktok", tiktok.lstrip("@"))

    yelp = st.text_input("Yelp page URL",
        value=intake.get("yelp",""), placeholder="yelp.com/biz/...")
    if yelp != intake.get("yelp",""):
        _save("yelp", yelp)

gmaps = st.text_input("Google Maps link (your business listing)",
    value=intake.get("google_maps_url",""),
    placeholder="maps.google.com/...")
if gmaps != intake.get("google_maps_url",""):
    _save("google_maps_url", gmaps)

# ── Section 6: Domain ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">6 — Domain Name</div>',
            unsafe_allow_html=True)

domain = st.text_input(
    "Domain preference *",
    value=intake.get("domain_preference",""),
    placeholder="mariasnailstudio.com or 'I need help choosing'",
)
if domain != intake.get("domain_preference",""):
    _save("domain_preference", domain)

domain_owned = st.checkbox(
    "I already own this domain",
    value=bool(intake.get("domain_owned", False)),
)
if domain_owned != bool(intake.get("domain_owned", False)):
    _save("domain_owned", domain_owned)

# ── Section 7: Notes ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">7 — Anything else?</div>',
            unsafe_allow_html=True)

notes = st.text_area(
    "Additional notes",
    value=intake.get("client_notes",""),
    placeholder="Websites you like, things you definitely don't want, "
                "specific features, anything else...",
    height=100, label_visibility="collapsed",
)
if notes != intake.get("client_notes",""):
    _save("client_notes", notes)

# ── Submit ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#6B7280;font-size:13px;'
    'margin-bottom:16px">Your progress is saved automatically. '
    "Submit when you're done — we'll start building right away.</div>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("✅  Submit & Finish",
                 type="primary", use_container_width=True):
        db.mark_complete(token)
        st.switch_page("pages/Done.py")

st.markdown(
    '<div style="text-align:center;font-size:12px;color:#9CA3AF;'
    'padding:24px 0">2Peak Growth · Kent / Renton / Tacoma, WA · '
    '2peakgrowth@gmail.com</div>',
    unsafe_allow_html=True,
)


