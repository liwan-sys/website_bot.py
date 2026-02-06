# ==============================================================================
# SARAH — SVB CHATBOT (Streamlit + Gemini) — VERSION CORRIGÉE
# ==============================================================================

import os
import re
import random
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Set

import streamlit as st

# ------------------------------------------------------------------------------
# 0) LOGGING & SETUP
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# Try importing Gemini, handle failure gracefully
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ------------------------------------------------------------------------------
# 1) PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# ------------------------------------------------------------------------------
# 2) CSS (STYLE)
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

.stApp{
  background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
  font-family:'Lato',sans-serif;
  color:#4A4A4A;
}
#MainMenu, footer, header {visibility:hidden;}

h1{
  font-family:'Dancing Script',cursive;
  color:#8FB592;
  text-align:center;
  font-size:3.4rem !important;
  margin-bottom:0px !important;
  text-shadow:2px 2px 4px rgba(0,0,0,0.10);
}
.subtitle{
  text-align:center;
  color:#EBC6A6;
  font-size:1.0rem;
  font-weight:700;
  margin-bottom:18px;
  text-transform:uppercase;
  letter-spacing:2px;
}
.stChatMessage{
  background-color: rgba(255,255,255,0.95) !important;
  border: 1px solid #EBC6A6;
  border-radius: 15px;
  padding: 14px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  color: #1f1f1f !important;
}
.stButton button{
  background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
  color:white !important;
  border:none;
  border-radius:25px;
  padding:12px 25px;
  font-weight:800;
  width:100%;
  text-transform:uppercase;
}
.stButton button:hover{ transform: scale(1.02); }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# 3) HEADER
# ------------------------------------------------------------------------------
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

# ==============================================================================
# 4) DONNÉES & CONFIGURATION (SOURCE DE VÉRITÉ)
# ==============================================================================

CONTACT = {
    "whatsapp_url": "https://wa.me/33744919155",
    "whatsapp_label": "📞 Contacter l'équipe (WhatsApp)",
    "email": "hello@studiosvb.fr",
    "instagram": "@svb.officiel",
}

STUDIOS = {
    "docks": {
        "label": "Parc des Docks",
        "address": "6 Mail André Breton, 93400 Saint-Ouen",
    },
    "lavandieres": {
        "label": "Cours Lavandières",
        "address": "40 Cours des Lavandières, 93400 Saint-Ouen",
    },
}

UNIT_PRICE = {
    "training": 30.00,
    "machine": 50.00,
}

TRIAL = {
    "price": 30.00,
    "refund_if_signup": 15.00,
}

STARTER = {
    "price": 99.90,
    "sessions": 5,
    "duration": "1 mois",
    "rule": "1 séance par discipline max.",
}

BOOST = {
    "price": 9.90,
    "includes": [
        "Frais d’inscription offerts",
        "1 essai gratuit / mois pour un proche",
        "Suspension abonnement sans préavis",
    ],
}

FEES = {
    "registration": 49.00,
    "kids_registration": 29.00,
}

KIDS_EXTRA = 18.30

# --- STRUCTURE DES PASS ---
@dataclass(frozen=True)
class PassPrice:
    sessions: int
    total: float

@dataclass(frozen=True)
class PassConfig:
    key: str
    label: str
    duration_min: int
    prices: Dict[int, PassPrice]
    where: str

PASS: Dict[str, PassConfig] = {}

def add_pass(p: PassConfig):
    PASS[p.key] = p

# Définition des Pass
add_pass(PassConfig("crossformer", "Pass Crossformer", 50, {
    2: PassPrice(2, 78.30), 4: PassPrice(4, 152.30), 6: PassPrice(6, 222.30),
    8: PassPrice(8, 288.30), 10: PassPrice(10, 350.30), 12: PassPrice(12, 408.30)
}, "lavandieres"))

add_pass(PassConfig("reformer", "Pass Reformer", 50, {
    2: PassPrice(2, 70.30), 4: PassPrice(4, 136.30), 6: PassPrice(6, 198.30),
    8: PassPrice(8, 256.30), 10: PassPrice(10, 310.30), 12: PassPrice(12, 360.30)
}, "lavandieres"))

add_pass(PassConfig("full_former", "Pass Full Former", 50, {
    2: PassPrice(2, 74.30), 4: PassPrice(4, 144.30), 6: PassPrice(6, 210.30),
    8: PassPrice(8, 272.30), 10: PassPrice(10, 330.30), 12: PassPrice(12, 384.30)
}, "lavandieres"))

add_pass(PassConfig("cross", "Pass Cross", 55, {
    2: PassPrice(2, 30.30), 4: PassPrice(4, 60.30), 6: PassPrice(6, 90.30),
    8: PassPrice(8, 116.30), 10: PassPrice(10, 145.30), 12: PassPrice(12, 168.30)
}, "docks"))

add_pass(PassConfig("focus", "Pass Focus", 55, {
    2: PassPrice(2, 36.30), 4: PassPrice(4, 72.30), 6: PassPrice(6, 105.30),
    8: PassPrice(8, 136.30), 10: PassPrice(10, 165.30), 12: PassPrice(12, 192.30)
}, "mixte"))

add_pass(PassConfig("full", "Pass Full", 55, {
    2: PassPrice(2, 40.30), 4: PassPrice(4, 80.30), 6: PassPrice(6, 115.30),
    8: PassPrice(8, 150.30), 10: PassPrice(10, 180.30), 12: PassPrice(12, 210.30)
}, "mixte"))

add_pass(PassConfig("kids", "Pass Kids", 55, {
    2: PassPrice(2, 35.30), 4: PassPrice(4, 65.30)
}, "docks"))

# --- PLANNING (PLACEHOLDER) ---
# Format: "studio": {"jour": [("heure", "cours", "tag")]}
PLANNING_DATA = {
    "docks": {
        "lundi": [("07:00", "Cross Training", "cross"), ("18:30", "Boxe", "focus")],
        "mardi": [("07:00", "Cross Training", "cross"), ("19:00", "Danse", "focus")],
        # ... Remplir avec le vrai planning ...
    },
    "lavandieres": {
        "lundi": [("08:00", "Reformer", "reformer"), ("19:00", "Yoga", "focus")],
        "mardi": [("12:30", "Crossformer", "crossformer")],
        # ... Remplir avec le vrai planning ...
    }
}
DAY_ORDER = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# ==============================================================================
# 5) FONCTIONS UTILITAIRES
# ==============================================================================

def eur(val: float) -> str:
    return f"{val:,.2f}€".replace(",", " ").replace(".", ",")

def norm(text: str) -> str:
    return (text or "").strip().lower()

def find_sessions(text: str) -> Optional[int]:
    import re
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm(text))
    return int(m.group(1)) if m else None

def find_pass_key(text: str) -> Optional[str]:
    t = norm(text)
    mapping = [
        ("full former", "full_former"), ("fullformer", "full_former"),
        ("crossformer", "crossformer"), ("reformer", "reformer"),
        ("cross", "cross"), ("focus", "focus"), ("full", "full"),
        ("kids", "kids"), ("enfant", "kids")
    ]
    for k_txt, k_key in mapping:
        if k_txt in t:
            return k_key
    return None

def detect_studio(text: str) -> Optional[str]:
    t = norm(text)
    if "dock" in t: return "docks"
    if "lavandi" in t: return "lavandieres"
    return None

def detect_day(text: str) -> Optional[str]:
    t = norm(text)
    for d in DAY_ORDER:
        if d in t: return d
    return None

def get_api_key() -> Optional[str]:
    # Check streamlit secrets first
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.getenv("GOOGLE_API_KEY")

# ==============================================================================
# 6) RÉPONSES DÉTERMINISTES
# ==============================================================================

def get_planning_response(text: str) -> str:
    studio = detect_studio(text)
    day = detect_day(text)

    if not studio:
        return "Tu veux le planning de quel studio : **Docks** ou **Lavandières** ?"
    
    if not day:
        # Afficher tout le planning du studio si pas de jour précis
        res = [f"📅 **Planning {STUDIOS[studio]['label']}** :"]
        for d in DAY_ORDER:
            slots = PLANNING_DATA.get(studio, {}).get(d, [])
            if slots:
                lines = [f"{h} : {c}" for h, c, tag in slots]
                res.append(f"**{d.capitalize()}** : " + ", ".join(lines))
        return "\n\n".join(res)

    # Jour spécifique
    slots = PLANNING_DATA.get(studio, {}).get(day, [])
    if not slots:
        return f"Aucun cours trouvé le **{day}** aux {STUDIOS[studio]['label']}."
    
    lines = [f"{h} : {c}" for h, c, tag in slots]
    return f"**{STUDIOS[studio]['label']} — {day.capitalize()}** :\n" + "\n".join(lines)

def get_price_response(text: str) -> Optional[str]:
    # 1. Séance supp
    if "supp" in norm(text) or "ajout" in norm(text):
        pk = find_pass_key(text)
        n = find_sessions(text)
        if pk == "kids": return f"Séance supp Kids : **{eur(KIDS_EXTRA)}**."
        if pk and n:
            p_conf = PASS[pk]
            total = p_conf.prices[n].total
            unit = total / n
            return f"Séance supp ({p_conf.label} {n}) : **{eur(unit)}** (prorata)."
        return "Pour la séance supp, dis-moi ton pass et le nombre de sessions (ex: 'supp cross 4')."

    # 2. Starter / Essai / Boost
    if "starter" in norm(text):
        return f"⭐ **Starter** : {eur(STARTER['price'])} ({STARTER['sessions']} sessions, 1 mois)."
    if "essai" in norm(text):
        return f"Essai : **{eur(TRIAL['price'])}** (remboursé si inscription)."
    if "boost" in norm(text):
        return f"⚡ **Option Boost** : {eur(BOOST['price'])}/mois (frais offerts, suspension libre)."

    # 3. Prix Pass
    pk = find_pass_key(text)
    n = find_sessions(text)
    if pk and n:
        p_conf = PASS[pk]
        if n in p_conf.prices:
            return f"📌 **{p_conf.label} {n} sessions** : **{eur(p_conf.prices[n].total)}** / mois."
    
    # 4. Unité
    if "unit" in norm(text) or "sans abo" in norm(text):
        return f"Unité : Training **{eur(UNIT_PRICE['training'])}**, Machine **{eur(UNIT_PRICE['machine'])}**."

    return None

def get_rules_response(text: str) -> Optional[str]:
    t = norm(text)
    if "chaussette" in t:
        return "🧦 Chaussettes antidérapantes **obligatoires** aux Lavandières (vente 10€, prêt 3€)."
    if "retard" in t:
        return "⏱️ **5 min de tolérance** max, ensuite porte fermée."
    if "annul" in t:
        return "Annulation : **1h** avant (collectif) ou **24h** (privé) sinon perdu."
    return None

# ==============================================================================
# 7) INTELLIGENCE ARTIFICIELLE (GEMINI)
# ==============================================================================

def call_gemini(user_text: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    api_key = get_api_key()
    if not GEMINI_AVAILABLE or not api_key:
        return "Je ne peux pas répondre intelligemment sans ma clé API 🧠. Contacte l'équipe !", True

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash") # Ou gemini-pro

    # Contexte système strict
    system_prompt = """
    Tu es Sarah, assistante du studio SVB. Ton ton est naturel, court et chaleureux.
    INTERDICTIONS FORMELLES :
    1. NE JAMAIS inventer de prix.
    2. NE JAMAIS inventer d'horaires.
    3. Si on te demande un prix ou un horaire que tu ne connais pas, dis "Je regarde..." et laisse le code gérer, ou renvoie vers WhatsApp.
    
    Ton rôle est d'orienter (Machine vs Training), de rassurer (débutants), et de qualifier le besoin.
    Si la demande semble complexe, propose de contacter l'équipe.
    """
    
    # Construction historique (limité)
    msgs = [{"role": "user", "parts": [system_prompt]}]
    for m in history[-5:]:
        role = "user" if m["role"] == "user" else "model"
        msgs.append({"role": role, "parts": [m["content"]]})
    
    msgs.append({"role": "user", "parts": [user_text]})

    try:
        resp = model.generate_content(msgs)
        txt = resp.text.strip()
        
        # Détection basique de demande humaine
        needs_wa = "whatsapp" in txt.lower() or "équipe" in txt.lower()
        return txt, needs_wa
    except Exception as e:
        log.error(f"Gemini error: {e}")
        return "Oups, petit souci de connexion. Passe par WhatsApp !", True

# ==============================================================================
# 8) MAIN APP LOOP
# ==============================================================================

# Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Message d'accueil
    intro = "Salut ! 🙂 Je suis Sarah. Tu cherches plutôt du Training (Cross/Boxe) ou des Machines (Pilates) ?"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Affichage historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input utilisateur
if prompt := st.chat_input("Pose ta question..."):
    # 1. User msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Logique de réponse
    response_text = None
    show_wa = False

    # A. Déterministe (Prioritaire)
    # Planning ?
    if "planning" in norm(prompt) or "horaire" in norm(prompt) or "quand" in norm(prompt):
        response_text = get_planning_response(prompt)
    
    # Prix / Tarif ?
    elif any(k in norm(prompt) for k in ["prix", "tarif", "cout", "combien", "starter", "essai", "supp", "ajout"]):
        response_text = get_price_response(prompt)
    
    # Règles ?
    elif any(k in norm(prompt) for k in ["chaussette", "retard", "annul"]):
        response_text = get_rules_response(prompt)
    
    # B. Génératif (Si pas de réponse déterministe)
    if not response_text:
        response_text, show_wa = call_gemini(prompt, st.session_state.messages)

    # C. Fallback
    if not response_text:
        response_text = "Je n'ai pas compris. Tu peux préciser ou contacter l'équipe ?"
        show_wa = True

    # 3. Assistant msg
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])