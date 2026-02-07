# ==============================================================================
# SARAH — SVB CHATBOT — VERSION RÉFLEXION AVANCÉE (ANTI-ERREURS)
# ==============================================================================

import os, re, random
import streamlit as st
from typing import Dict, Optional

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(page_title="Sarah – SVB", page_icon="🧡", layout="centered")

CONTACT = {
    "whatsapp": "https://wa.me/33744919155",
    "label": "📞 Contacter l’équipe SVB"
}

# ==============================================================================
# BASE DE CONNAISSANCES (FACTS UNIQUES)
# ==============================================================================
PRICES = {
    "unit_training": 30.00,
    "unit_machine": 50.00,
    "passes": {
        "reformer": {4: 136.30, 8: 256.30, 12: 360.30},
        "crossformer": {4: 152.30, 8: 288.30, 12: 408.30},
        "focus": {4: 72.30, 8: 136.30, 12: 192.30},
        "cross": {4: 60.30, 8: 116.30, 12: 168.30},
        "full": {4: 80.30, 8: 150.30, 12: 210.30}
    }
}

DEFINITIONS = {
    "reformer": "Le Pilates Reformer est un Pilates sur machine à ressorts. Idéal pour le gainage, la posture et le dos. Accessible aux débutants.",
    "crossformer": "Le Crossformer est une machine plus cardio et intense, mélange de Pilates et de training.",
    "boxe": "La Boxe est un cours cardio sans combat, parfait pour se défouler et se tonifier.",
    "core & stretch": "Core & Stretch combine gainage et étirements, idéal pour le dos et la mobilité."
}

# ==============================================================================
# MÉMOIRE DE CONVERSATION (SLOTS)
# ==============================================================================
def ensure_memory():
    if "memory" not in st.session_state:
        st.session_state.memory = {
            "course": None,
            "pass": None,
            "sessions": None
        }

ensure_memory()

# ==============================================================================
# HELPERS
# ==============================================================================
def norm(t: str) -> str:
    return t.lower().replace("é","e").replace("è","e").replace("à","a")

def eur(x: float) -> str:
    return f"{x:,.2f}€".replace(",", " ").replace(".", ",")

def extract_sessions(t: str) -> Optional[int]:
    m = re.search(r"\b(4|8|12)\b", t)
    return int(m.group(1)) if m else None

def extract_course(t: str) -> Optional[str]:
    for c in DEFINITIONS:
        if c in t:
            return c
    if "reformer" in t or "pilate" in t:
        return "reformer"
    return None

# ==============================================================================
# LOGIQUE DE RÉFLEXION (LE CŒUR)
# ==============================================================================
def think(user_text: str) -> str:
    t = norm(user_text)
    mem = st.session_state.memory

    # --- 1. Définition ---
    if "c'est quoi" in t or "c quoi" in t:
        course = extract_course(t)
        if course:
            return DEFINITIONS[course]

    # --- 2. Prix ---
    if "combien" in t or "prix" in t or "tarif" in t:
        course = extract_course(t)
        if course:
            mem["course"] = course

        sessions = extract_sessions(t)
        if sessions:
            mem["sessions"] = sessions

        # ❌ manque info
        if not mem["sessions"]:
            return "Tu pensais à **combien de séances par mois** ? (4 / 8 / 12)"

        if not mem["course"]:
            return "Tu parles de **quel cours** exactement ? (Reformer, Crossformer, Boxe…)"

        # ✅ calcul
        prices = PRICES["passes"].get(mem["course"])
        if prices and mem["sessions"] in prices:
            total = prices[mem["sessions"]]
            unit = total / mem["sessions"]
            return (
                f"Pour **{mem['sessions']} séances de {mem['course'].capitalize()}** :\n"
                f"- Total : **{eur(total)}** / mois\n"
                f"- Soit **{eur(unit)} par séance**"
            )

    # --- 3. Inscription ---
    if "inscrire" in t or "inscription" in t:
        return (
            "Pour t’inscrire :\n"
            "1️⃣ Tu t’abonnes en ligne\n"
            "2️⃣ Tu reçois tes identifiants par mail\n"
            "3️⃣ Tu télécharges l’appli et tu réserves\n\n"
            "Besoin d’aide ?"
        )

    # --- 4. Fallback intelligent ---
    return (
        "Dis-moi ce que tu cherches exactement 🙂\n"
        "• un **prix**\n"
        "• un **cours**\n"
        "• le **planning**\n"
        "• ou une **recommandation**"
    )

# ==============================================================================
# UI
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Salut 🙂 Tu cherches plutôt un cours, un tarif ou un conseil ?"
    }]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Pose ta question…"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = think(prompt)

    st.session_state.messages.append({"role":"assistant","content":answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

        if "WhatsApp" in answer or "aide" in answer.lower():
            st.link_button(CONTACT["label"], CONTACT["whatsapp"])
