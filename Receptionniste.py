# ==============================================================================
# SARAH — SVB CHATBOT — VERSION ULTIME (FIX PRIX & MAT/SOL)
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
# 2) BASE DE DONNÉES
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
    
    # 1. DÉTECTION SPÉCIALE SOL/MAT (Priorité absolue pour le Pass Focus)
    if "sol" in t or "mat" in t: 
        pass_key = "focus"
    
    # 2. Autres détections
    elif "crossformer" in t: pass_key = "crossformer"
    elif "reformer" in t: pass_key = "reformer"
    # Si "Pilate" est dit SANS "sol" ni "mat", on propose Reformer par défaut, sinon Focus
    elif "pilate" in t or "pialte" in t: 
        pass_key = "reformer" if not pass_key else pass_key
        
    elif "full" in t: pass_key = "full" if "former" not in t else "full_former"
    elif "focus" in t: pass_key = "focus"
    elif "cross" in t: pass_key = "cross"
    elif "kid" in t or "enfant" in t: pass_key = "kids"
    
    sessions = None
    match = re.search(r"\b(2|4|6|8|10|12)\b", t)
    if match: sessions = int(match.group(1))
    
    return pass_key, sessions

def extract_course_key(text: str) -> Optional[str]:
    t = normalize(text)
    aliases = {
        "pilate reformer": "reformer", "reformer": "reformer",
        "pilate crossformer": "crossformer", "crossformer": "crossformer",
        "boxe": "boxe", "cross training": "cross training", "cross core": "cross core",
        "yoga vinyasa": "yoga vinyasa", "hatha": "hatha flow", "classic pilates": "classic pilates",
        "power pilates": "power pilates", "yoga kids": "yoga kids", "afrodance": "afrodance",
        "pilate mat": "power pilates", "pilate au sol": "power pilates" # Ajout pour planning
    }
    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t: return aliases[k]
    # Fallback générique
    if "pilate" in t and ("sol" in t or "mat" in t): return "power pilates"
    return None

def detect_studio(text: str) -> Optional[str]:
    t = normalize(text)
    if "dock" in t: return "docks"
    if "lavandi" in t: return "lavandieres"
    return None

def detect_day(text: str) -> Optional[str]:
    t = normalize(text)
    days_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    for d in days_fr:
        if d in t: return d
    return None

def get_api_key() -> Optional[str]:
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.getenv("GOOGLE_API_KEY")

# ==============================================================================
# 4) RÉPONSES
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
        if course_key in ["reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates"]:
            studio = "lavandieres"
        elif course_key in ["boxe", "afrodance", "cross training", "cross core", "cross body"]:
            studio = "docks"

    if not studio: 
        return "Tu veux le planning de quel studio : **Docks** (Cross/Boxe) ou **Lavandières** (Reformer/Yoga) ?"
    
    res = []
    days_to_show = [day] if day else ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    
    studio_slots = PLANNING_DB.get(studio, {})
    
    found_any = False
    for d in days_to_show:
        slots = studio_slots.get(d, [])
        if course_key:
            # Recherche partielle plus souple
            slots = [s for s in slots if course_key in normalize(s)]
            
        if slots:
            found_any = True
            # Nettoyage affichage
            clean_slots = [s.replace(course_key.capitalize(), f"**{course_key.capitalize()}**") for s in slots]
            res.append(f"🗓️ **{d.capitalize()}** : {', '.join(clean_slots)}")
        elif day: 
            res.append(f"Aucun cours trouvé le **{d}** aux {studio.capitalize()}.")
            
    if not found_any and not day:
        return f"Je n'ai pas trouvé de cours correspondant à ta demande aux {studio.capitalize()}."

    return "\n\n".join(res)

def answer_boxe_price() -> str:
    return (
        f"Un cours de **Boxe** :\n"
        f"- Sans abonnement : **{eur(PRICING_DB['unit_training'])}**\n"
        f"- Si tu es abonné(e) : ça dépend de ton pass (au **prorata** : prix du pass / nb sessions). "
        f"Dis-moi juste ton pass et ton nombre de sessions (ex: *Pass Focus 4*) et je te calcule."
    )

def get_price_response(text: str) -> str:
    t = normalize(text)
    
    if "boxe" in t: return answer_boxe_price()
    if "starter" in t: return f"⭐ **Starter** : {eur(PRICING_DB['starter'])} ({PRICING_DB['starter']} sessions, 1 mois)."
    if "essai" in t: return f"Essai : **{eur(PRICING_DB['trial'])}** (remboursé si inscription)."
    if "boost" in t: return f"⚡ **Option Boost** : {eur(PRICING_DB['boost'])}/mois."
    if "unit" in t or "sans abo" in t: return f"Unité : Training **{eur(PRICING_DB['unit_training'])}**, Machine **{eur(PRICING_DB['unit_machine'])}**."

    # Pass prices
    pass_key, sessions = detect_pass_info(text)
    
    # CAS 1 : PASS + NOMBRE
    if pass_key and sessions:
        if sessions in PRICING_DB['passes'].get(pass_key, {}):
            total = PRICING_DB['passes'][pass_key][sessions]
            unit = total / sessions
            return (f"📌 **Pass {pass_key.capitalize()} {sessions} sessions** : **{eur(total)}** / mois.\n"
                    f"_(Soit environ **{eur(unit)}** la séance)_")
    
    # CAS 2 : PASS SANS NOMBRE -> On affiche TOUT
    elif pass_key:
        prices = PRICING_DB['passes'].get(pass_key)
        lines = [f"📋 **Tarifs Pass {pass_key.capitalize()}** :"]
        for sess, val in prices.items():
            lines.append(f"- {sess} sessions : **{eur(val)}**")
        return "\n".join(lines)
            
    return "Je n'ai pas compris quel tarif tu cherches. Peux-tu préciser (ex: 'Pass Cross 4 sessions') ?"

def get_rules_response(text: str) -> str:
    t = normalize(text)
    if "chaussette" in t: return "🧦 Chaussettes antidérapantes **obligatoires** aux Lavandières (vente 10€, prêt 3€)."
    if "retard" in t: return FAQ_DB["retard"]
    if "annul" in t: return "Annulation : **1h** avant (collectif) ou **24h** (privé) sinon perdu."
    return "Peux-tu préciser ta question sur le règlement ?"

def get_definition_response(text: str) -> Optional[str]:
    t = normalize(text)
    if "difference" in t:
        if "reformer" in t and "crossformer" in t:
            return "Différence **Reformer vs Crossformer** :\n- **Reformer** : Pilates machine contrôlé, top pour la posture/gainage.\n- **Crossformer** : Pilates machine **cardio/intense**, ça transpire plus !"
    return None

# ==============================================================================
# 8) MAIN LOGIC (ROUTER)
# ==============================================================================

def deterministic_router(text: str) -> Tuple[Optional[str], bool]:
    t = normalize(text)
    
    if intent_human(text): return human_alert("Ça marche, je te mets en relation avec l'équipe.")
    if intent_suspension(text): return get_suspension_response(), False
    if intent_signup(text): return get_signup_response(), False
    
    # PRIX (CORRECTION : On inclut "pric" et la détection auto du pass)
    pass_key, _ = detect_pass_info(text)
    is_pricing = any(w in t for w in ["prix", "tarif", "cout", "combien", "coute", "pric"]) or pass_key
    
    # PLANNING (Si c'est un cours mais PAS une demande de prix explicite)
    is_planning = intent_planning(text) or (extract_course_key(text) and not is_pricing)

    # Priorité : Si mot clé "prix" présent -> Prix. Sinon -> Planning si cours détecté.
    if is_pricing and any(w in t for w in ["prix", "tarif", "cout", "combien", "coute", "pric"]):
        return get_price_response(text), False
    elif is_planning:
        return get_planning_response(text), False
    elif is_pricing: # Cas du "Focus 8" sans mot clé
        return get_price_response(text), False

    if intent_rules(text): return get_rules_response(text), False
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

    system_prompt = """
    Tu es Sarah, assistante du studio SVB. Ton ton est naturel, court et chaleureux.
    
    RÈGLES D'OR :
    1. NE JAMAIS inventer de prix ou d'horaires.
    2. Si on te demande "C'est quoi le Crossformer ?", explique brièvement.
    3. Oriente le client : Stressé -> Boxe/Cross. Mal de dos -> Reformer/Yoga.
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
# 9) APP LOOP
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Bonjour ! Je suis Sarah, l'assistante du studio SVB. Comment puis-je t'aider aujourd'hui ?"})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response_text, show_wa = deterministic_router(prompt)

    if not response_text:
        response_text, show_wa = call_gemini(prompt, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp"])