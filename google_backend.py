import os
import json
import requests
import streamlit as st
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def process_audio_speech_to_text(audio_bytes: bytes) -> str:
    return "[Audio-Aufnahme empfangen und verarbeitet]"

def analyze_makler_input(transcript: str, image_bytes: Optional[bytes], plan: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        
    if not api_key:
        return {"kunde_name": "Hinweis", "din_checks": [{"kategorie": "API-Key", "status": "ROT", "meldung": "GEMINI_API_KEY fehlt!"}], "zusammenfassung": "Bitte API Key hinterlegen."}

    prompt_text = f"""
    Du bist eine Makler-KI für den deutschen Versicherungsmarkt.
    Analysiere das Gespräch streng nach DIN 77230. Tarif: {plan}. Transkript: {transcript}
    Antworte AUSSCHLIESSLICH als gültiges JSON:
    {{
        "kunde_name": "Max Mustermann",
        "din_checks": [
            {{"kategorie": "Berufsunfähigkeit", "status": "ROT", "meldung": "Soll-Bedarf laut DIN: 1.920 € Rente fehlt."}},
            {{"kategorie": "Privathaftpflicht", "status": "GRUEN", "meldung": "Ausreichende Deckung vorhanden."}}
        ],
        "zusammenfassung": "Zusammenfassung für das Maklerportal."
    }}
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    try:
        res = requests.post(url, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": prompt_text}]}], "generationConfig": {"response_mime_type": "application/json"}}, timeout=30)
        if res.status_code == 200:
            return json.loads(res.json()["candidates"][0]["content"]["parts"][0]["text"])
        return {"kunde_name": "Unbekannt", "din_checks": [{"kategorie": "API", "status": "ROT", "meldung": f"HTTP {res.status_code}"}], "zusammenfassung": "API Fehler"}
    except Exception as e:
        return {"kunde_name": "Unbekannt", "din_checks": [{"kategorie": "System", "status": "ROT", "meldung": str(e)}], "zusammenfassung": "Netzwerkunterbrechung"}