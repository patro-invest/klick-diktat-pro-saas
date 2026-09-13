import streamlit as st
import auth_db
from google_backend import process_audio_speech_to_text, analyze_makler_input
from pool_integration import upload_protocol_to_fonds_finanz
from pdf_generator import generate_din_pdf_report

st.set_page_config(page_title="Klick&Diktat Pro", layout="centered")

st.markdown("""
<style>
    .main { background-color: #0b132b; color: #ffffff; }
    h1, h2, h3, p { color: #ffffff !important; }
    .stButton>button { 
        font-size: 22px !important; 
        font-weight: bold !important; 
        height: 70px !important; 
        width: 100% !important; 
        background-color: #c5a880 !important; 
        color: #000000 !important; 
        border-radius: 15px !important; 
    }
    .ampel-rot { background-color: #ff1744; color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 18px; }
    .ampel-gruen { background-color: #00e676; color: black; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Klick&Diktat Login")
    with st.form("login"):
        email = st.text_input("E-Mail", value="vater@makler.de")
        pw = st.text_input("Passwort", type="password", value="makler123")
        if st.form_submit_button("Anmelden"):
            user = auth_db.authenticate_user(email, pw)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user_info"] = user
                st.rerun()
    st.stop()
    user_info = st.session_state["user_info"]
st.title("🎙️ Klick&Diktat Pro")

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.write(f"Tarif: {user_info['plan']}")
    ff_key = st.text_input("Fonds Finanz Key", value=user_info.get("ff_api_key", ""), type="password")
    if st.button("Key speichern"):
        auth_db.update_agency_api_key(user_info['agency_id'], ff_key)
        st.success("Gespeichert!")

st.write("📸 **1. Dokument fotografieren**")
foto = st.camera_input("Foto", label_visibility="collapsed")
foto_bytes = foto.getvalue() if foto else None

st.write("🎙️ **2. Gespräch diktieren**")
audio = st.audio_input("Aufnahme", label_visibility="collapsed")

if audio:
    with st.spinner("Analyse läuft..."):
        transcript = process_audio_speech_to_text(audio.getvalue())
        st.session_state["auswertung"] = analyze_makler_input(transcript, foto_bytes, user_info['plan'])

if "auswertung" in st.session_state:
    res = st.session_state["auswertung"]
    st.write(f"### ⚡ Ergebnisanalyse ({res.get('kunde_name', 'Kunde')}):")
    
    for check in res.get("din_checks", []):
        css_class = "ampel-rot" if check["status"] == "ROT" else "ampel-gruen"
        st.markdown(f'<div class="{css_class}">{check["kategorie"]}: {check["meldung"]}</div>', unsafe_allow_html=True)
        
    pdf_bytes = generate_din_pdf_report(res, user_info['agency_id'])
    st.download_button("📄 PDF-Protokoll herunterladen", data=pdf_bytes, file_name=f"DIN_Protokoll_{res.get('kunde_name', 'Kunde')}.pdf", mime="application/pdf")