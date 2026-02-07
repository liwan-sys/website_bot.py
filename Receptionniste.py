# ==============================================================================
# SARAH — SVB CHATBOT — VERSION FINALE (CORRIGÉE & FONCTIONNELLE)
# ==============================================================================

import os
import re
import random
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import streamlit as st

# ------------------------------------------------------------------------------
# 0) LOGGING
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ------------------------------------------------------------------------------
# 1) GEMINI (OPTIONNEL)
# ------------------------------------------------------------------------------
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ------------------------------------------------------------------------------
# 2) PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# ------------------------------------------------------------------------------
# 3) CSS (IDENTITÉ)
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
# 4) HEADER
# ------------------------------------------------------------------------------
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

# ==============================================================================
# 5) DONNÉES (SOURCE DE VÉRITÉ)
# ==============================================================================

CONTACT = {
    "whatsapp_url": "https://wa.me/33744919155",
    "whatsapp_label": "📞 Contacter l'équipe (WhatsApp)",
}

STUDIOS = {
    "docks": {"label": "Parc des Docks", "address": "6 Mail André Breton, St-Ouen"},
    "lavandieres": {"label": "Cours Lavandières", "address": "40 Cours des Lavandières, St-Ouen"},
}

UNIT_PRICE = {"training": 30.00, "machine": 50.00}
TRIAL = {"price": 30.00, "refund_if_signup": 15.00}
STARTER = {"price": 99.90, "sessions": 5, "duration": "1 mois"}
BOOST = {"price": 9.90}
FEES = {"registration": 49.00}
KIDS_EXTRA = 18.30

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

add_pass(PassConfig("crossformer", "Pass Crossformer", 50, {2: PassPrice(2, 78.30), 4: PassPrice(4, 152.30), 6: PassPrice(6, 222.30), 8: PassPrice(8, 288.30), 10: PassPrice(10, 350.30), 12: PassPrice(12, 408.30)}, "lavandieres"))
add_pass(PassConfig("reformer", "Pass Reformer", 50, {2: PassPrice(2, 70.30), 4: PassPrice(4, 136.30), 6: PassPrice(6, 198.30), 8: PassPrice(8, 256.30), 10: PassPrice(10, 310.30), 12: PassPrice(12, 360.30)}, "lavandieres"))
add_pass(PassConfig("full_former", "Pass Full Former", 50, {2: PassPrice(2, 74.30), 4: PassPrice(4, 144.30), 6: PassPrice(6, 210.30), 8: PassPrice(8, 272.30), 10: PassPrice(10, 330.30), 12: PassPrice(12, 384.30)}, "lavandieres"))
add_pass(PassConfig("cross", "Pass Cross", 55, {2: PassPrice(2, 30.30), 4: PassPrice(4, 60.30), 6: PassPrice(6, 90.30), 8: PassPrice(8, 116.30), 10: PassPrice(10, 145.30), 12: PassPrice(12, 168.30)}, "docks"))
add_pass(PassConfig("focus", "Pass Focus", 55, {2: PassPrice(2, 36.30), 4: PassPrice(4, 72.30), 6: PassPrice(6, 105.30), 8: PassPrice(8, 136.30), 10: PassPrice(10, 165.30), 12: PassPrice(12, 192.30)}, "mixte"))
add_pass(PassConfig("full", "Pass Full", 55, {2: PassPrice(2, 40.30), 4: PassPrice(4, 80.30), 6: PassPrice(6, 115.30), 8: PassPrice(8, 150.30), 10: PassPrice(10, 180.30), 12: PassPrice(12, 210.30)}, "mixte"))
add_pass(PassConfig("kids", "Pass Kids", 55, {2: PassPrice(2, 35.30), 4: PassPrice(4, 65.30)}, "docks"))

# --- PLANNING RÉEL ---
PLANNING_DATA = {
    "docks": {
        "lundi": [("12h", "Cross Training", "cross"), ("13h", "Cross Core", "cross"), ("19h", "Cross Training", "cross"), ("20h", "Cross Body", "cross")],
        "mardi": [("12h", "Cross Rox", "cross"), ("19h", "Cross Body", "cross"), ("20h", "Cross Training", "cross")],
        "mercredi": [("12h", "Cross Training", "cross"), ("16h", "Yoga Kids", "kids"), ("19h", "Cross Training", "cross"), ("20h", "Boxe", "focus")],
        "jeudi": [("08h", "Cross Core", "cross"), ("12h", "Cross Body", "cross"), ("13h", "Boxe", "focus"), ("18h", "Cross Training", "cross"), ("19h", "Afrodance", "focus")],
        "vendredi": [("18h", "Cross Rox", "cross"), ("19h", "Cross Training", "cross")],
        "samedi": [("09h30", "Training Kids", "kids"), ("10h30", "Cross Body", "cross"), ("11h30", "Cross Training", "cross")],
        "dimanche": [("10h30", "Cross Training", "cross"), ("11h30", "Cross Yoga", "cross")]
    },
    "lavandieres": {
        "lundi": [("12h", "Crossformer", "crossformer"), ("12h15", "Reformer", "reformer"), ("12h30", "Yoga Vinyasa", "focus"), ("18h45", "Crossformer", "crossformer"), ("19h", "Yoga Vinyasa", "focus"), ("19h15", "Reformer", "reformer")],
        "mardi": [("07h30", "Hatha Flow", "focus"), ("11h45", "Crossformer", "crossformer"), ("12h", "Power Pilates", "focus"), ("13h15", "Reformer", "reformer"), ("18h45", "Crossformer", "crossformer"), ("19h15", "Reformer", "reformer"), ("20h", "Power Pilates", "focus")],
        "mercredi": [("10h15", "Crossformer", "crossformer"), ("12h", "Reformer", "reformer"), ("12h15", "Crossformer", "crossformer"), ("19h", "Reformer", "reformer"), ("19h15", "Crossformer", "crossformer"), ("20h", "Reformer", "reformer")],
        "jeudi": [("07h", "Classic Pilates", "focus"), ("12h", "Yoga Vinyasa", "focus"), ("12h15", "Crossformer", "crossformer"), ("12h30", "Reformer", "reformer"), ("18h", "Crossformer", "crossformer"), ("18h45", "Reformer", "reformer"), ("19h15", "Power Pilates", "focus"), ("20h15", "Cross Yoga", "cross"), ("20h30", "Cross Forme", "crossformer")],
        "vendredi": [("09h45", "Crossformer", "crossformer"), ("10h45", "Crossformer", "crossformer"), ("12h", "Reformer", "reformer"), ("13h", "Reformer", "reformer"), ("18h", "Classic Pilates", "focus"), ("18h30", "Reformer", "reformer"), ("19h15", "Crossformer", "crossformer")],
        "samedi": [("09h", "Reformer", "reformer"), ("09h30", "Crossformer", "crossformer"), ("10h", "Reformer", "reformer"), ("10h15", "Classic Pilates", "focus"), ("10h30", "Crossformer", "crossformer"), ("11h15", "Core & Stretch", "focus")],
        "dimanche": [("10h", "Crossformer", "crossformer"), ("10h15", "Reformer", "reformer"), ("11h", "Crossformer", "crossformer"), ("11h15", "Reformer", "reformer"), ("11h30", "Yoga Vinyasa", "focus")]
    }
}
DAY_ORDER = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# ==============================================================================
# 6) UTILS
# ==============================================================================

def eur(val: float) -> str:
    return f"{val:,.2f}€".replace(",", " ").replace(".", ",")

def norm(text: str) -> str:
    return (text or "").strip().lower()

def get_api_key() -> Optional[str]:
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except:
        return os.getenv("GOOGLE_API_KEY")

def extract_course_key(text: str) -> Optional[str]:
    t = norm(text)
    # Mapping simplifié pour la détection
    if "reformer" in t: return "reformer"
    if "crossformer" in t: return "crossformer"
    if "boxe" in t: return "boxe"
    if "training" in t: return "cross training"
    if "kids" in t: return "kids"
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

def find_pass_key(text: str) -> Optional[str]:
    t = norm(text)
    if "crossformer" in t: return "crossformer"
    if "reformer" in t: return "reformer"
    if "full" in t: return "full"
    if "focus" in t: return "focus"
    if "cross" in t: return "cross"
    if "kid" in t: return "kids"
    return None

def find_sessions(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm(text))
    return int(m.group(1)) if m else None

# ==============================================================================
# 7) INTENTS & RESPONSES
# ==============================================================================

def intent_human(text: str) -> bool:
    return any(w in norm(text) for w in ["humain", "equipe", "telephone", "contact", "parler"])

def intent_suspension(text: str) -> bool:
    return any(w in norm(text) for w in ["pause", "suspendre", "suspension", "arret", "vacance"])

def intent_signup(text: str) -> bool:
    # Mots clés stricts pour inscription
    return any(w in norm(text) for w in ["m'inscrire", "inscrire", "inscription", "creer un compte", "identifiant", "connexion"])

def get_suspension_response() -> str:
    return (
        "🛑 **Mettre en pause son abonnement** :\n\n"
        "1. **Avec l'Option Boost** : Suspension libre, sans préavis.\n"
        "2. **Sans Option Boost** : Suspension possible si absence > 10 jours et préavis d'1 mois.\n\n"
        "Contactez-nous sur WhatsApp pour l'activer."
    )

def get_signup_response() -> str:
    return (
        "📝 **Inscription** : Souscrivez en ligne, recevez vos identifiants par mail, puis réservez sur l'appli SVB. "
        "Si vous ne recevez pas le mail, vérifiez vos spams ou écrivez-nous."
    )

def get_planning_response(text: str) -> str:
    studio = detect_studio(text)
    day = detect_day(text)
    course = extract_course_key(text)
    
    if not studio and course:
        if course in ["reformer", "crossformer"]: studio = "lavandieres"
        if course in ["boxe", "kids", "training"]: studio = "docks"
        
    if not studio:
        return "Tu veux le planning de quel studio : **Docks** ou **Lavandières** ?"
        
    res = []
    days_show = [day] if day else DAY_ORDER
    for d in days_show:
        slots = PLANNING_DATA.get(studio, {}).get(d, [])
        if course: slots = [s for s in slots if course in norm(s[1])]
        
        if slots:
            lines = [f"{h} : {c}" for h, c, tag in slots]
            res.append(f"**{d.capitalize()}** : {', '.join(lines)}")
            
    return "\n\n".join(res) if res else "Aucun cours trouvé pour cette recherche."

def get_price_response(text: str) -> str:
    if "starter" in norm(text): return f"⭐ **Starter** : {eur(STARTER['price'])} (5 sessions, 1 mois)."
    if "essai" in norm(text): return f"Essai : **{eur(TRIAL['price'])}** (remboursé si inscription)."
    if "unite" in norm(text) or "sans abo" in norm(text): return f"Unité : Training {eur(UNIT_PRICE['training'])}, Machine {eur(UNIT_PRICE['machine'])}."
    
    pk = find_pass_key(text)
    n = find_sessions(text)
    
    if pk and n:
        if "supp" in norm(text):
             # Calcul séance supp au prorata
             p = PASS[pk]
             return f"Séance supp ({p.label} {n}) : **{eur(p.prices[n].total/n)}**."
        else:
             # Prix du pass
             return f"📌 **{PASS[pk].label} {n} sessions** : **{eur(PASS[pk].prices[n].total)}** / mois."
             
    return "Je n'ai pas compris quel tarif tu cherches. Précise le pass et le nombre de séances."

# ==============================================================================
# 8) ROUTER & IA
# ==============================================================================

def deterministic_router(text: str) -> Tuple[Optional[str], bool]:
    t = norm(text)
    if intent_human(text): return "Je te mets avec l'équipe.", True
    if intent_suspension(text): return get_suspension_response(), False
    if intent_signup(text): return get_signup_response(), False
    if "planning" in t or "horaire" in t or "quand" in t: return get_planning_response(text), False
    if "prix" in t or "tarif" in t or "cout" in t or "supp" in t: return get_price_response(text), False
    return None, False

def call_gemini(user_text: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    api_key = get_api_key()
    if not GEMINI_AVAILABLE or not api_key:
        return "Je ne peux pas répondre sans ma clé API. Contacte l'équipe.", True

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    sys_prompt = "Tu es Sarah, assistante SVB. Sois courte, naturelle et utile. N'invente pas de prix."
    
    msgs = [{"role": "user", "parts": [sys_prompt]}]
    for m in history[-5:]:
        msgs.append({"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [user_text]})
    
    try:
        resp = model.generate_content(msgs)
        return resp.text.strip(), False
    except:
        return "Oups, erreur de connexion.", True

# ==============================================================================
# 9) APP MAIN
# ==============================================================================

def first_message():
    return random.choice([
        "Bonjour ! Je suis Sarah, l'assistante du studio SVB. Comment puis-je t'aider ?",
        "Hello ! Bienvenue chez SVB. Une question sur le planning ou les tarifs ?",
        "Salut 🙂 Je suis là pour te renseigner. Dis-moi ce que tu cherches !"
    ])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": first_message()}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    resp, show_wa = deterministic_router(prompt)
    if not resp:
        resp, show_wa = call_gemini(prompt, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": resp})
    with st.chat_message("assistant"):
        st.markdown(resp)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])