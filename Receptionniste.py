# ==============================================================================
# SARAH — SVB CHATBOT — VERSION INTELLIGENTE & ROBUSTE (CORRIGÉE)
# ==============================================================================

import os
import re
import random
import logging
import datetime
import locale
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import streamlit as st

# ------------------------------------------------------------------------------
# 0) CONFIGURATION
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    pass

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# ------------------------------------------------------------------------------
# 1) ESTHÉTIQUE
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');
.stApp { background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%); font-family:'Lato',sans-serif; color:#000000 !important; }
h1 { font-family:'Dancing Script',cursive; color:#8FB592; text-align:center; font-size:3.4rem !important; margin-bottom:0px !important; text-shadow:2px 2px 4px rgba(0,0,0,0.10); }
.subtitle { text-align:center; color:#EBC6A6; font-size:1.0rem; font-weight:700; margin-bottom:18px; text-transform:uppercase; letter-spacing:2px; }
.stChatMessage { background-color: #ffffff !important; border: 1px solid #EBC6A6; border-radius: 15px; padding: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div, .stChatMessage h1, .stChatMessage h2, .stChatMessage h3, .stChatMessage strong { color: #000000 !important; line-height: 1.6; }
.stButton button { background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); color:white !important; border:none; border-radius:25px; padding:12px 25px; font-weight:800; width:100%; text-transform:uppercase; }
.stButton button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB • SANTEZ-VOUS BIEN</div>", unsafe_allow_html=True)

# ==============================================================================
# 2) BASE DE DONNÉES (VÉRITÉ)
# ==============================================================================

CONTACT = {"whatsapp": "https://wa.me/33744919155", "email": "hello@studiosvb.fr", "phone": "07 44 91 91 55"}

PRICING_DB = {
    "unit_training": 30.00, "unit_machine": 50.00, "trial": 30.00, "starter": 99.90, "boost": 9.90, "kids_extra": 18.30,
    "passes": {
        "cross": {4: 60.30, 8: 116.30, 12: 168.30},
        "focus": {4: 72.30, 8: 136.30, 12: 192.30},
        "full": {4: 80.30, 8: 150.30, 12: 210.30},
        "reformer": {4: 136.30, 8: 256.30, 12: 360.30},
        "crossformer": {4: 152.30, 8: 288.30, 12: 408.30},
        "full_former": {4: 144.30, 8: 272.30, 12: 384.30},
        "kids": {2: 35.30, 4: 65.30}
    }
}

PLANNING_DB = {
    "docks": {
        "lundi": ["12h Cross Training", "13h Cross Core", "19h Cross Training", "20h Cross Body"],
        "mardi": ["12h Cross Rox", "19h Cross Body", "20h Cross Training"],
        "mercredi": ["12h Cross Training", "16h Yoga Kids", "19h Cross Training", "20h Boxe"],
        "jeudi": ["08h Cross Core", "12h Cross Body", "13h Boxe", "18h Cross Training", "19h Afrodance"],
        "vendredi": ["18h Cross Rox", "19h Cross Training"],
        "samedi": ["09h30 Training Kids", "10h30 Cross Body", "11h30 Cross Training"],
        "dimanche": ["10h30 Cross Training", "11h30 Cross Yoga"]
    },
    "lavandieres": {
        "lundi": ["12h Crossformer", "12h15 Reformer", "12h30 Yoga Vinyasa", "18h45 Crossformer", "19h Yoga Vinyasa", "19h15 Reformer"],
        "mardi": ["07h30 Hatha Flow", "11h45 Crossformer", "12h Power Pilates", "13h15 Reformer", "18h45 Crossformer", "19h15 Reformer", "20h Power Pilates"],
        "mercredi": ["10h15 Crossformer", "12h Reformer", "12h15 Crossformer", "19h Reformer", "19h15 Crossformer", "20h Reformer"],
        "jeudi": ["07h Classic Pilates", "12h Yoga Vinyasa", "12h15 Crossformer", "12h30 Reformer", "18h Crossformer", "18h45 Reformer", "19h15 Power Pilates", "20h15 Cross Yoga", "20h30 Cross Forme"],
        "vendredi": ["09h45 Crossformer", "10h45 Crossformer", "12h Reformer", "13h Reformer", "18h Classic Pilates", "18h30 Reformer", "19h15 Crossformer"],
        "samedi": ["09h Reformer", "09h30 Crossformer", "10h Reformer", "10h15 Classic Pilates", "10h30 Crossformer", "11h15 Core & Stretch"],
        "dimanche": ["10h Crossformer", "10h15 Reformer", "11h Crossformer", "11h15 Reformer", "11h30 Yoga Vinyasa"]
    }
}

FAQ_DB = {
    "parking": "🚗 **Stationnement** :\n- **Docks** : Le parking des Docks est souvent complet. Privilégie les rues adjacentes ou le parking souterrain de la Mairie.\n- **Lavandières** : Il y a un parking public juste en face du studio.",
    "douche": "🚿 **Douches & Vestiaires** :\nOui, nos deux studios sont équipés de douches individuelles, de casiers sécurisés et de sèche-cheveux. Tout le confort est là !",
    "tenue": "👟 **Tenue** :\n- **Training (Docks)** : Baskets propres obligatoires.\n- **Machines (Lavandières)** : Chaussettes antidérapantes **OBLIGATOIRES** (en vente sur place 10€ si oubli).",
    "retard": "⏱️ **Politique de Retard** :\nPour la sécurité, **nous n'acceptons aucun retard** au-delà de 5 minutes. La porte sera fermée.",
    "contact_humain": "📞 **Besoin d'un humain ?**\nLe plus simple est d'écrire à l'équipe sur WhatsApp : " + CONTACT['whatsapp']
}

RULES = {
    "suspension_policy": "🛑 **Mettre en pause l'abonnement** :\n1. Avec l'Option Boost : Suspension libre, sans préavis et sans justificatif.\n2. Sans Option Boost : Suspension possible uniquement si absence > 10 jours et préavis d'1 mois."
}

# ==============================================================================
# 3) MOTEUR INTELLIGENT
# ==============================================================================

def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("é", "e").replace("è", "e").replace("à", "a").replace("ê", "e").replace("ù", "u")
    return text

def eur(val: float) -> str:
    return f"{val:,.2f}€".replace(",", " ").replace(".", ",")

def get_current_day() -> str:
    days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    return days[datetime.datetime.now().weekday()]

def detect_pass_info(text: str) -> Tuple[Optional[str], Optional[int]]:
    t = normalize(text)
    pass_key = None
    
    # 1. DÉTECTION PASS (ORDRE D'IMPORTANCE)
    
    # Si on parle explicitement de SOL / MAT -> C'est le PASS FOCUS
    if "sol" in t or "mat" in t: 
        pass_key = "focus"
        
    # Sinon, on vérifie les machines
    elif "crossformer" in t: 
        pass_key = "crossformer"
    elif "reformer" in t: 
        pass_key = "reformer"
        
    # Sinon, on vérifie le mot "pilate" générique
    # Si "pilate" est seul (sans "sol"), on assume souvent Reformer, 
    # MAIS on peut aussi renvoyer vers Focus si le contexte est "yoga/pilates".
    # Ici, on garde la priorité Reformer SAUF si "sol" a été détecté plus haut.
    elif "pilate" in t or "pialte" in t:
        pass_key = "reformer" if not pass_key else pass_key

    # Autres pass
    elif "full" in t: 
        pass_key = "full" if "former" not in t else "full_former"
    elif "focus" in t: 
        pass_key = "focus"
    elif "cross" in t: 
        pass_key = "cross"
    elif "kid" in t or "enfant" in t: 
        pass_key = "kids"
    
    # 2. DÉTECTION NOMBRE SÉANCES
    sessions = None
    match = re.search(r"\b(2|4|6|8|10|12)\b", t)
    if match: sessions = int(match.group(1))
    
    return pass_key, sessions

def get_pricing_response(text: str) -> str:
    t = normalize(text)
    
    if "boxe" in t:
        return (f"🥊 **Tarif Boxe** :\n"
                f"- À l'unité : **{eur(PRICING_DB['unit_training'])}**\n"
                f"- En abonnement : Inclus dans les Pass Cross et Full. Le prix revient au prorata (ex: Pass Cross 4 = 15€/séance).")
    
    if "starter" in t: return f"⭐ **Offre Starter** : {eur(PRICING_DB['starter'])} pour 5 sessions (valable 1 mois)."
    if "essai" in t: return f"🎟️ **Séance d'essai** : {eur(PRICING_DB['trial'])} (15€ remboursés si inscription !)."
    
    pass_key, sessions = detect_pass_info(text)
    
    if pass_key:
        if pass_key == "kids": return f"👶 **Pass Kids** : 2 séances = {eur(PRICING_DB['passes']['kids'][2])} | 4 séances = {eur(PRICING_DB['passes']['kids'][4])}."
        
        # Si nombre détecté
        if sessions and sessions in PRICING_DB['passes'].get(pass_key, {}):
            total = PRICING_DB['passes'][pass_key][sessions]
            unit = total / sessions
            return f"🏷️ **Pass {pass_key.capitalize()} {sessions} sessions** : **{eur(total)}** / mois (soit {eur(unit)}/séance)."
        
        # Si PAS de nombre détecté -> On affiche TOUT
        prices = PRICING_DB['passes'].get(pass_key)
        if prices:
            lines = [f"📋 **Tarifs Pass {pass_key.capitalize()}** :"]
            for k, v in prices.items():
                lines.append(f"- {k} sessions : **{eur(v)}**")
            return "\n".join(lines)

    return "🤔 Je vois que tu parles de prix, mais pour quel cours ou quel abonnement ? (Ex: 'Prix Reformer 4' ou 'Prix Boxe')"

def get_planning_response(text: str) -> str:
    t = normalize(text)
    day = None
    days_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    for d in days_fr:
        if d in t: day = d
    if "aujourd'hui" in t: day = get_current_day()

    studio = None
    if "dock" in t or "boxe" in t or "training" in t or "afro" in t: studio = "docks"
    if "lavandi" in t or "reformer" in t or "pilate" in t or "vinyasa" in t: studio = "lavandieres"

    if not studio: return "📅 Tu cherches le planning de quel côté ? **Docks** ou **Lavandières** ?"

    res = []
    days_to_show = [day] if day else days_fr
    for d in days_to_show:
        slots = PLANNING_DB[studio].get(d, [])
        if slots:
            res.append(f"🗓️ **{d.capitalize()} aux {studio.capitalize()}** :")
            for s in slots: res.append(f"- {s}")
            
    return "\n".join(res) if res else f"Aucun cours trouvé le {day}."

# ==============================================================================
# 4) ROUTEUR PRINCIPAL
# ==============================================================================

def main_router(text: str) -> Tuple[str, bool]:
    t = normalize(text)
    
    if any(w in t for w in ["humain", "parler", "telephone", "probleme", "urgent"]):
        return FAQ_DB["contact_humain"], True
    
    if any(w in t for w in ["garer", "parking"]): return FAQ_DB["parking"], False
    if any(w in t for w in ["douche", "laver"]): return FAQ_DB["douche"], False
    if any(w in t for w in ["tenue", "basket", "chaussure"]): return FAQ_DB["tenue"], False
    if any(w in t for w in ["retard"]): return FAQ_DB["retard"], False
    
    if any(w in t for w in ["pause", "suspendre", "arret"]): return RULES["suspension_policy"], True
    
    # DÉTECTION PRIX AMÉLIORÉE (Si pass + nombre détectés, on force le prix même sans mot clé "prix")
    pass_key, sessions = detect_pass_info(text)
    if any(w in t for w in ["prix", "tarif", "cout", "combien", "coute"]) or (pass_key and sessions) or (pass_key and "prix" in t):
        return get_pricing_response(text), False
        
    if any(w in t for w in ["quand", "heure", "planning", "cours", "jour"]) or detect_pass_info(text)[0]:
        # Si on parle d'un cours mais pas de prix, c'est le planning
        return get_planning_response(text), False

    return "GEMINI_FALLBACK", False

# ==============================================================================
# 5) IA GENERATIVE
# ==============================================================================

def call_gemini_smart(user_text: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
    if not GEMINI_AVAILABLE or not api_key:
        return "Oups, je suis un peu perdue. Contacte l'équipe sur WhatsApp !", True

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    sys_prompt = """
    Tu es Sarah, la coach du studio SVB. Ton rôle : Comprendre l'état d'esprit du client et l'orienter.
    Si le client veut se défouler -> Boxe/Cross Training.
    Si le client veut du calme/dos -> Reformer/Yoga.
    NE JAMAIS INVENTER DE PRIX. Si tu ne sais pas, dis de regarder le site.
    """
    
    msgs = [{"role": "user", "parts": [sys_prompt]}]
    for m in history[-4:]:
        msgs.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [user_text]})

    try:
        resp = model.generate_content(msgs)
        return resp.text.strip(), False
    except:
        return "J'ai un petit souci de connexion. Peux-tu répéter ?", True

# ==============================================================================
# 6) INTERFACE
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello ! Je suis Sarah. Prête à t'aider pour tes séances chez SVB ! 💪"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response, show_wa = main_router(prompt)
    if response == "GEMINI_FALLBACK":
        response, show_wa = call_gemini_smart(prompt, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"] if "whatsapp_label" in CONTACT else "📞 WhatsApp", CONTACT["whatsapp"])