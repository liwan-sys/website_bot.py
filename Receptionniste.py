# ==============================================================================
# SARAH — SVB CHATBOT — VERSION ULTIME (INTELLIGENTE & ROBUSTE)
# ==============================================================================

import os
import re
import random
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import streamlit as st

# ------------------------------------------------------------------------------
# 0) LOGGING & SETUP
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

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
# 2) CSS (DESIGN & VISIBILITÉ)
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

.stApp{
  background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
  font-family:'Lato',sans-serif;
  color:#000000 !important;
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
  background-color: #ffffff !important;
  border: 1px solid #EBC6A6;
  border-radius: 15px;
  padding: 14px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage li {
  color: #000000 !important;
  line-height: 1.6;
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
# 4) DATA (SOURCE DE VÉRITÉ)
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
# 5) UTILS
# ==============================================================================

def eur(val: float) -> str:
    return f"{val:,.2f}€".replace(",", " ").replace(".", ",")

def norm(text: str) -> str:
    return (text or "").strip().lower()

def find_sessions(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm(text))
    return int(m.group(1)) if m else None

def find_pass_key(text: str) -> Optional[str]:
    t = norm(text)
    mapping = [("full former", "full_former"), ("fullformer", "full_former"), ("crossformer", "crossformer"), ("reformer", "reformer"), ("cross", "cross"), ("focus", "focus"), ("full", "full"), ("kids", "kids"), ("enfant", "kids")]
    for k_txt, k_key in mapping:
        if k_txt in t: return k_key
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
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.getenv("GOOGLE_API_KEY")

def extract_course_key(text: str) -> Optional[str]:
    t = norm(text)
    aliases = {
        "pilate reformer": "reformer", "reformer": "reformer",
        "pilate crossformer": "crossformer", "crossformer": "crossformer", "cross-former": "crossformer",
        "boxe": "boxe", "cross training": "cross training", "cross core": "cross core", "cross body": "cross body",
        "cross rox": "cross rox", "cross yoga": "cross yoga", "yoga vinyasa": "yoga vinyasa", "hatha": "hatha flow",
        "classic pilates": "classic pilates", "power pilates": "power pilates", "core & stretch": "core & stretch",
        "yoga kids": "yoga kids", "training kids": "training kids", "afrodance": "afrodance"
    }
    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t: return aliases[k]
    return None

def tag_to_pass_hint(tag: str) -> str:
    mapping = {
        "cross": "Pass Cross (ou Pass Full)",
        "focus": "Pass Focus (ou Pass Full)",
        "kids": "Pass Kids",
        "reformer": "Pass Reformer",
        "crossformer": "Pass Crossformer",
    }
    return mapping.get(tag, "selon la formule")

# ==============================================================================
# 6) INTENT DETECTION (ROBUSTE)
# ==============================================================================

def intent_human(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in ["humain", "conseiller", "equipe", "équipe", "whatsapp", "telephone", "téléphone", "contact", "joindre", "parler a", "parler à"])

def intent_suspension(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in ["pause", "suspendre", "suspension", "arret", "arrêt", "vacance"])

def intent_signup(text: str) -> bool:
    t = norm(text)
    signup_keywords = ["m'inscrire", "inscrire", "inscription", "s'inscrire", "creer un compte", "créer un compte", "nouvel adherent", "nouveau membre"]
    app_keywords = ["identifiant", "mot de passe", "connexion", "connecter", "pas reçu mail", "pas recu mail"]
    return any(w in t for w in signup_keywords + app_keywords)

def intent_pricing(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in ["prix", "tarif", "cout", "combien", "starter", "essai", "supp", "ajout", "abonnement", "pass"])

def intent_planning(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in ["planning", "horaire", "quand", "heure", "jour", "cours"])

def intent_rules(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in ["chaussette", "retard", "annul", "regle"])

def intent_definition(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in ["c'est quoi", "c quoi", "ça veut dire", "definition", "définition", "explique", "expliquer", "difference", "différence"])

# ==============================================================================
# 7) DETERMINISTIC RESPONSES (REPONSES EXACTES)
# ==============================================================================

def human_alert(reason: str = "") -> Tuple[str, bool]:
    txt = reason.strip() if reason else "Je te mets directement avec l’équipe pour être sûr à 100% 🙂"
    return txt, True

def get_suspension_response() -> str:
    return (
        "🛑 **Mettre en pause son abonnement** :\n\n"
        "1. **Avec l'Option Boost** : La suspension est libre, sans préavis et sans justificatif.\n"
        "2. **Sans Option Boost (Standard)** : La suspension n'est possible que pour une absence **supérieure à 10 jours** et nécessite un **préavis d'1 mois**.\n\n"
        "Pour activer une suspension, contactez-nous directement via WhatsApp."
    )

def get_signup_response() -> str:
    return (
        "📝 **Procédure d'inscription** :\n\n"
        "1. Souscrivez votre abonnement en ligne sur notre site.\n"
        "2. Après paiement, vous recevez un e-mail automatique avec vos identifiants.\n"
        "3. Téléchargez l'application (SVB / Sportigo).\n"
        "4. Connectez-vous avec les identifiants reçus.\n"
        "5. Réservez vos séances sur le planning ! ✅\n\n"
        "⚠️ *Mail non reçu ? Vérifiez les spams ou contactez-nous.*"
    )

def get_planning_response(text: str) -> str:
    studio = detect_studio(text)
    day = detect_day(text)
    course_key = extract_course_key(text)
    
    if not studio and course_key:
        if course_key in ["reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch"]:
            studio = "lavandieres"
        elif course_key in ["boxe", "afrodance", "cross training", "cross core", "cross body", "cross rox", "training kids", "yoga kids"]:
            studio = "docks"

    if not studio: 
        return "Tu veux le planning de quel studio : **Docks** (Cross/Boxe) ou **Lavandières** (Reformer/Yoga) ?"
    
    res = []
    days_to_show = [day] if day else DAY_ORDER
    
    studio_slots = PLANNING_DATA.get(studio, {})
    
    found_any = False
    for d in days_to_show:
        slots = studio_slots.get(d, [])
        if course_key:
            slots = [s for s in slots if course_key in norm(s[1])]
            
        if slots:
            found_any = True
            lines = [f"{h} : {c}" for h, c, tag in slots]
            res.append(f"**{d.capitalize()}** : {', '.join(lines)}")
        elif day: 
            res.append(f"Aucun cours de {course_key.capitalize() if course_key else ''} trouvé le **{d}** aux {STUDIOS[studio]['label']}.")
            
    if not found_any and not day:
        return f"Je n'ai pas trouvé de cours correspondant à ta demande aux {STUDIOS[studio]['label']}."

    return "\n\n".join(res)

def answer_boxe_price() -> str:
    return (
        f"Un cours de **Boxe** :\n"
        f"- Sans abonnement : **{eur(UNIT_PRICE['training'])}**\n"
        f"- Si tu es abonné(e) : ça dépend de ton pass (au **prorata** : prix du pass / nb sessions). "
        f"Dis-moi juste ton pass et ton nombre de sessions (ex: *Pass Focus 4*) et je te calcule."
    )

def get_price_response(text: str) -> str:
    t = norm(text)
    if "supp" in t or "ajout" in t:
        pk = find_pass_key(text)
        n = find_sessions(text)
        if pk == "kids": return f"Séance supp Kids : **{eur(KIDS_EXTRA)}**."
        if pk and n:
            p = PASS[pk]
            return f"Séance supp ({p.label} {n}) : **{eur(p.prices[n].total/n)}** (prorata)."
        return "Pour la séance supp, dis-moi ton pass et le nombre de sessions (ex: 'supp cross 4')."
    
    if "starter" in t: return f"⭐ **Starter** : {eur(STARTER['price'])} ({STARTER['sessions']} sessions, 1 mois)."
    if "essai" in t: return f"Essai : **{eur(TRIAL['price'])}** (remboursé si inscription)."
    if "boost" in t: return f"⚡ **Option Boost** : {eur(BOOST['price'])}/mois."
    if "unit" in t or "sans abo" in t: return f"Unité : Training **{eur(UNIT_PRICE['training'])}**, Machine **{eur(UNIT_PRICE['machine'])}**."

    # Pass prices
    pk = find_pass_key(text)
    n = find_sessions(text)
    if pk and n:
        if n in PASS[pk].prices:
            return f"📌 **{PASS[pk].label} {n} sessions** : **{eur(PASS[pk].prices[n].total)}** / mois."
            
    return "Je n'ai pas compris quel tarif tu cherches. Peux-tu préciser (ex: 'Pass Cross 4 sessions') ?"

def get_rules_response(text: str) -> str:
    t = norm(text)
    if "chaussette" in t: return "🧦 Chaussettes antidérapantes **obligatoires** aux Lavandières (vente 10€, prêt 3€)."
    if "retard" in t: return "⏱️ **5 min de tolérance** max, ensuite porte fermée."
    if "annul" in t: return "Annulation : **1h** avant (collectif) ou **24h** (privé) sinon perdu."
    return "Peux-tu préciser ta question sur le règlement ?"

def get_definition_response(text: str) -> Optional[str]:
    t = norm(text)
    if "difference" in t or "différence" in t:
        if "reformer" in t and "crossformer" in t:
            return "Différence **Reformer vs Crossformer** :\n- **Reformer** : Pilates machine contrôlé, top pour la posture/gainage.\n- **Crossformer** : Pilates machine **cardio/intense**, ça transpire plus !"
    
    ck = extract_course_key(text)
    defs = {
        "reformer": "Le **Reformer** est une machine à ressorts pour travailler le Pilates en profondeur (gainage, posture).",
        "crossformer": "Le **Crossformer** est une version cardio et intense du Pilates sur machine.",
        "cross training": "Le **Cross Training** est un circuit haute intensité (cardio + renfo).",
        "boxe": "La **Boxe** chez SVB est cardio et technique, sur sacs (pas de coups reçus).",
        "yoga vinyasa": "Le **Vinyasa** est un yoga dynamique où on enchaîne les postures."
    }
    if ck in defs:
        return defs[ck]
    return None

# ==============================================================================
# 8) MAIN LOGIC (ROUTER)
# ==============================================================================

def deterministic_router(text: str) -> Tuple[Optional[str], bool]:
    t = norm(text)
    # 0. Humain
    if intent_human(text):
        return human_alert("Ça marche, je te mets en relation avec l'équipe.")
        
    # 1. Suspension
    if intent_suspension(text):
        return get_suspension_response(), False
    
    # 2. Inscription
    if intent_signup(text):
        return get_signup_response(), False
        
    # 3. Planning
    if intent_planning(text) or extract_course_key(text): 
        if not intent_pricing(text) and not intent_definition(text):
            return get_planning_response(text), False
        
    # 4. Prix (Priorité Boxe)
    if "boxe" in t and any(w in t for w in ["prix", "tarif", "cout", "combien"]):
        return answer_boxe_price(), False

    if intent_pricing(text):
        return get_price_response(text), False
        
    # 5. Règles
    if intent_rules(text):
        return get_rules_response(text), False
        
    # 6. Définitions
    if intent_definition(text):
        r = get_definition_response(text)
        if r: return r, False
        
    return None, False

def call_gemini(user_text: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    api_key = get_api_key()
    if not GEMINI_AVAILABLE or not api_key:
        return "Je ne peux pas répondre intelligemment sans ma clé API 🧠. Contacte l'équipe !", True

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # CERVEAU AMÉLIORÉ : INTELLIGENCE PSYCHOLOGIQUE
    system_prompt = """
    Tu es Sarah, l'assistante experte et empathique du studio SVB.
    Ton but n'est pas juste de donner des infos, mais de COMPRENDRE le besoin caché du client.

    🧠 TA MATRICE DE DÉDUCTION (Si le client dit ça -> Tu proposes ça) :
    1. BESOIN : "Se défouler", "Stressé", "Journée horrible", "Énergie", "Transpirer", "Gants"
       👉 SOLUTION : Propose les cours INTENSES aux DOCKS (Boxe, Cross Training).
       👉 ARGUMENT : "Rien de mieux pour lâcher prise et tout oublier !"

    2. BESOIN : "Mal au dos", "Reprise douce", "Enceinte", "Pas sportif", "Raide", "Souplesse"
       👉 SOLUTION : Propose les cours DOUX/TECHNIQUES aux LAVANDIÈRES (Pilates Reformer, Yoga).
       👉 ARGUMENT : "C'est idéal pour renforcer ton corps en profondeur sans chocs."

    3. BESOIN : "Sculpter", "Tonifier", "Brûler", "Intense mais sans sauter partout"
       👉 SOLUTION : Propose le CROSSFORMER (Lavandières) ou le CROSS BODY (Docks).

    ⚠️ RÈGLES DE SÉCURITÉ ABSOLUES :
    - Ne jamais inventer un prix (si tu ne l'as pas, dis "Je n'ai pas le tarif exact sous les yeux").
    - Ne jamais inventer un horaire précis (si le client ne donne pas de jour, demande-lui "Tu préfères venir quel jour ?").
    - Si la question est technique (appli qui bug, paiement), renvoie vers WhatsApp.

    TON TON :
    Chaleureux, pro, tutoiement respectueux (comme une coach).
    """
    
    msgs = [{"role": "user", "parts": [system_prompt]}]
    for m in history[-6:]:
        role = "user" if m["role"] == "user" else "model"
        msgs.append({"role": role, "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [user_text]})

    try:
        resp = model.generate_content(msgs)
        txt = resp.text.strip()
        needs_wa = "whatsapp" in txt.lower() or "équipe" in txt.lower()
        return txt, needs_wa
    except Exception as e:
        log.error(f"Gemini error: {e}")
        return "Oups, je réfléchis trop... Un petit souci de connexion. Réessaie !", True

# ==============================================================================
# 9) APP LOOP & UX
# ==============================================================================

def first_message() -> str:
    variants = [
        "Bonjour ! Je suis Sarah, l'assistante du studio SVB. Comment puis-je t'aider aujourd'hui ?",
        "Hello ! Bienvenue chez SVB. Tu as une question sur le planning, les tarifs ou nos cours ?",
        "Salut 🙂 Je suis là pour te renseigner sur le studio. Dis-moi ce que tu recherches !"
    ]
    return random.choice(variants)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": first_message()})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ROUTING
    response_text, show_wa = deterministic_router(prompt)

    # Fallback Gemini
    if not response_text:
        response_text, show_wa = call_gemini(prompt, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])