# ==============================================================================
# SARAH — SVB CHATBOT — ARCHITECTURE INDUSTRIELLE (KNOWLEDGE BASE INTEGRÉE)
# ==============================================================================
#
# CE CODE EST CONÇU POUR ANTICIPER 99% DES QUESTIONS CLIENTS.
# IL UTILISE UNE "BASE DE CONNAISSANCES" STATIQUE POUR LA PRÉCISION
# ET L'IA GEMINI POUR LA CONVERSATION ET L'EMPATHIE.
#
# ==============================================================================

import os
import re
import random
import logging
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Union

import streamlit as st

# ------------------------------------------------------------------------------
# 0) CONFIGURATION SYSTEME
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# Configuration de la date en français (si possible, sinon anglais)
try:
    import locale
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
# 1) ESTHÉTIQUE & CSS (TEXTE NOIR FORCE)
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

.stApp { background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%); font-family:'Lato',sans-serif; color:#000000 !important; }
h1 { font-family:'Dancing Script',cursive; color:#8FB592; text-align:center; font-size:3.4rem !important; margin-bottom:0px !important; text-shadow:2px 2px 4px rgba(0,0,0,0.10); }
.subtitle { text-align:center; color:#EBC6A6; font-size:1.0rem; font-weight:700; margin-bottom:18px; text-transform:uppercase; letter-spacing:2px; }

/* Force chat bubbles text to black */
.stChatMessage { background-color: #ffffff !important; border: 1px solid #EBC6A6; border-radius: 15px; padding: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage li, .stChatMessage h1, .stChatMessage h2, .stChatMessage h3, .stChatMessage strong { color: #000000 !important; line-height: 1.6; }

/* Buttons */
.stButton button { background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); color:white !important; border:none; border-radius:25px; padding:12px 25px; font-weight:800; width:100%; text-transform:uppercase; }
.stButton button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB • SANTEZ-VOUS BIEN</div>", unsafe_allow_html=True)

# ==============================================================================
# 2) BASE DE CONNAISSANCES (KNOWLEDGE BASE)
# ==============================================================================

CONTACT = {
    "whatsapp": "https://wa.me/33744919155",
    "email": "hello@studiosvb.fr",
    "phone": "07 44 91 91 55"
}

# --- TARIFS (PRÉCIS) ---
PRICING_DB = {
    "unit_training": 30.00,
    "unit_machine": 50.00,
    "trial": 30.00,
    "starter": 99.90,
    "boost": 9.90,
    "kids_extra": 18.30,
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

# --- PLANNING (RÉEL) ---
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

# --- FAQ & SITUATIONS SPÉCIFIQUES (C'EST ICI QUE CA DEVIENT INTELLIGENT) ---
FAQ_DB = {
    "parking": "🚗 **Stationnement** : \n- **Docks** : Le parking des Docks est souvent complet. Privilégie les rues adjacentes ou le parking souterrain de la Mairie.\n- **Lavandières** : Il y a un parking public juste en face du studio.",
    "douche": "🚿 **Douches & Vestiaires** :\nOui, nos deux studios sont équipés de douches individuelles, de casiers sécurisés et de sèche-cheveux. Tout le confort est là !",
    "tenue": "u **Tenue** :\n- **Training (Docks)** : Baskets propres obligatoires + tenue de sport.\n- **Machines (Lavandières)** : Chaussettes antidérapantes **OBLIGATOIRES** (en vente sur place 10€ si oubli). Pas de chaussures sur les machines.",
    "retard": "⏱️ **Politique de Retard** :\nPour la sécurité et le respect du cours, **nous n'acceptons aucun retard** au-delà de 5 minutes. La porte sera fermée.",
    "enceinte": "🤰 **Femmes Enceintes** :\n- **Recommandé** : Pilates Reformer (avec accord médical) et Yoga Prénatal (si au planning).\n- **Déconseillé** : Cross Training, Boxe et Crossformer après le 1er trimestre.",
    "blessure": "🤕 **Blessures** :\nSignale-le **toujours** au coach en début de séance. \n- **Mal de dos ?** Privilégie le Reformer.\n- **Genoux fragiles ?** Evite les sauts du Cross Training.",
    "famille": "👨‍👩‍👧 **Venir accompagné** :\nL'accès aux studios est réservé aux membres inscrits. Pour des raisons d'assurance et de calme, les enfants/animaux ne peuvent pas attendre à l'accueil pendant le cours.",
    "paiement": "💳 **Moyens de paiement** :\nNous acceptons les cartes bancaires via l'application et sur place. Nous ne prenons pas les chèques vacances pour le moment.",
    "niveau": "🔰 **Niveau Débutant** :\nTous nos cours sont **accessibles aux débutants** ! Nos coachs adaptent les charges et les exercices. N'aie pas peur de la Boxe ou du Crossformer, on t'expliquera tout.",
    "annulation_cours": "❌ **Annulation de séance** :\nTu peux annuler sans frais jusqu'à **1h avant** le début du cours (24h pour le coaching privé). Sinon, la séance est décomptée.",
    "contact_humain": "📞 **Besoin d'un humain ?**\nLe plus simple est d'écrire à l'équipe sur WhatsApp : " + CONTACT['whatsapp']
}

# ==============================================================================
# 3) MOTEUR D'INTELLIGENCE (LOGIQUE PYTHON)
# ==============================================================================

def normalize(text: str) -> str:
    """Nettoie le texte pour l'analyse."""
    text = text.lower()
    text = text.replace("é", "e").replace("è", "e").replace("à", "a").replace("ê", "e").replace("ù", "u")
    return text

def eur(val: float) -> str:
    return f"{val:,.2f}€".replace(",", " ").replace(".", ",")

def get_current_day() -> str:
    """Renvoie le jour actuel en français."""
    days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    return days[datetime.datetime.now().weekday()]

# --- DÉTECTEURS SPÉCIFIQUES ---

def detect_faq(text: str) -> Optional[str]:
    t = normalize(text)
    if any(w in t for w in ["garer", "parking", "stationnement", "voiture"]): return FAQ_DB["parking"]
    if any(w in t for w in ["douche", "laver", "vestiaire", "casier", "seche cheveux"]): return FAQ_DB["douche"]
    if any(w in t for w in ["tenue", "habiller", "basket", "chaussure", "pied", "nu"]): return FAQ_DB["tenue"]
    if any(w in t for w in ["retard", "late", "bouchon", "arriver apres"]): return FAQ_DB["retard"]
    if any(w in t for w in ["enceinte", "grossesse", "bebe", "pregnant"]): return FAQ_DB["enceinte"]
    if any(w in t for w in ["mal", "douleur", "dos", "genou", "blessure", "hernie"]): return FAQ_DB["blessure"]
    if any(w in t for w in ["enfant", "ami", "chien", "accompagner", "regarder"]): return FAQ_DB["famille"]
    if any(w in t for w in ["cheque", "vacances", "espece", "cash", "payer"]): return FAQ_DB["paiement"]
    if any(w in t for w in ["debutant", "commencer", "jamais fait", "niveau", "dur", "difficile"]): return FAQ_DB["niveau"]
    if any(w in t for w in ["annuler", "annulation", "desister", "empechement"]): return FAQ_DB["annulation_cours"]
    return None

def detect_pass_info(text: str) -> Tuple[Optional[str], Optional[int]]:
    t = normalize(text)
    # Détection Pass
    pass_key = None
    if "crossformer" in t: pass_key = "crossformer"
    elif "reformer" in t or "pilate" in t: pass_key = "reformer" # Priorité reformer sur pilate
    elif "full" in t: pass_key = "full" if "former" not in t else "full_former"
    elif "focus" in t: pass_key = "focus"
    elif "cross" in t: pass_key = "cross"
    elif "kid" in t or "enfant" in t: pass_key = "kids"
    
    # Détection Nombre
    sessions = None
    match = re.search(r"\b(2|4|6|8|10|12)\b", t)
    if match: sessions = int(match.group(1))
    
    return pass_key, sessions

# --- ROUTEURS DE RÉPONSE ---

def get_pricing_response(text: str) -> str:
    t = normalize(text)
    
    # Cas spécifiques
    if "boxe" in t:
        return (f"🥊 **Tarif Boxe** :\n"
                f"- À l'unité : **{eur(PRICING_DB['unit_training'])}**\n"
                f"- En abonnement : Inclus dans les Pass Cross et Full. Le prix revient au prorata (ex: Pass Cross 4 = 15€/séance).")
    
    if "starter" in t: return f"⭐ **Offre Starter** : {eur(PRICING_DB['starter'])} pour 5 sessions (valable 1 mois)."
    if "essai" in t: return f"🎟️ **Séance d'essai** : {eur(PRICING_DB['trial'])} (15€ remboursés si tu t'abonnes derrière !)."
    if "boost" in t: return f"🚀 **Option Boost** : {eur(PRICING_DB['boost'])}/mois (Suspension libre + Frais offerts + Invité)."
    if "unite" in t or "session" in t: return f"💎 **Prix à l'unité** : Training {eur(PRICING_DB['unit_training'])} | Machine {eur(PRICING_DB['unit_machine'])}."

    # Cas Calcul Pass
    pass_key, sessions = detect_pass_info(text)
    
    if pass_key:
        if pass_key == "kids": return f"👶 **Pass Kids** (hors vacances) : 2 séances = {eur(PRICING_DB['passes']['kids'][2])} | 4 séances = {eur(PRICING_DB['passes']['kids'][4])}."
        
        # Si on a le nombre
        if sessions and sessions in PRICING_DB['passes'].get(pass_key, {}):
            total = PRICING_DB['passes'][pass_key][sessions]
            unit = total / sessions
            if "supp" in t or "ajout" in t:
                return f"➕ **Séance Supplémentaire** ({pass_key.capitalize()} {sessions}) : **{eur(unit)}** (calculé au prorata)."
            return f"🏷️ **Pass {pass_key.capitalize()} {sessions} sessions** : **{eur(total)}** / mois (soit {eur(unit)}/séance)."
        
        # Si on a que le nom
        prices = PRICING_DB['passes'].get(pass_key)
        if prices:
            lines = [f"📋 **Tarifs Pass {pass_key.capitalize()}** :"]
            for k, v in prices.items():
                lines.append(f"- {k} sessions : **{eur(v)}**")
            return "\n".join(lines)

    return "🤔 Je vois que tu parles de prix, mais pour quel cours ou quel abonnement ? (Ex: 'Prix Reformer 4' ou 'Prix Boxe')"

def get_planning_response(text: str) -> str:
    t = normalize(text)
    
    # Détection Jour
    day = None
    for d in DAY_ORDER:
        if d in t: day = d
    
    if "aujourd'hui" in t or "ce soir" in t: day = get_current_day()
    if "demain" in t: 
        curr_idx = datetime.datetime.now().weekday()
        day = DAY_ORDER[(curr_idx + 1) % 7]

    # Détection Studio/Activité
    studio = None
    if "dock" in t or "boxe" in t or "training" in t or "afro" in t: studio = "docks"
    if "lavandi" in t or "reformer" in t or "pilate" in t or "vinyasa" in t: studio = "lavandieres"

    # Logique de réponse
    if not studio:
        return "📅 Tu cherches le planning de quel côté ? **Docks** (Intensité/Boxe) ou **Lavandières** (Pilates/Yoga) ?"

    res = []
    days_to_show = [day] if day else DAY_ORDER # Si pas de jour précis, on montre tout ou on demande
    
    # Si pas de jour précisé, on affiche un résumé compact ou on demande précision
    if not day:
        return f"📅 **Planning {studio.capitalize()}** : Tu veux voir quel jour en particulier ? (Lundi, Mardi...)"

    # Affichage du jour demandé
    slots = PLANNING_DB[studio].get(day, [])
    if slots:
        res.append(f"🗓️ **{day.capitalize()} aux {studio.capitalize()}** :")
        for s in slots:
            res.append(f"- {s}")
    else:
        res.append(f"😴 Pas de cours prévu le **{day}** aux {studio.capitalize()}.")

    return "\n".join(res)

# ==============================================================================
# 4) INTELLIGENCE HYBRIDE (ROUTER)
# ==============================================================================

def main_router(text: str) -> Tuple[str, bool]:
    t = normalize(text)
    
    # 1. URGENCES & HUMAIN
    if any(w in t for w in ["humain", "parler", "telephone", "probleme", "bug", "urgent"]):
        return FAQ_DB["contact_humain"], True
    
    # 2. FAQ SPÉCIFIQUES (Priorité haute car questions précises)
    faq_answer = detect_faq(text)
    if faq_answer:
        return faq_answer, False
        
    # 3. SUSPENSION / RESILIATION
    if any(w in t for w in ["pause", "suspendre", "arret", "resilier"]):
        return RULES["suspension_policy"], True
        
    # 4. INSCRIPTION
    if any(w in t for w in ["inscrire", "inscription", "creer un compte"]):
        return "📝 **Inscription** : Tout se fait en ligne sur le site. Tu reçois tes codes par mail (vérifie tes spams !) puis tu réserves sur l'appli.", False
        
    # 5. TARIFS (Mot clé prix OU nom de pass + chiffre)
    pass_key, sessions = detect_pass_info(text)
    if any(w in t for w in ["prix", "tarif", "cout", "combien", "coute"]) or (pass_key and sessions):
        return get_pricing_response(text), False
        
    # 6. PLANNING
    if any(w in t for w in ["quand", "heure", "planning", "cours", "jour"]) or detect_day(text):
        return get_planning_response(text), False

    # 7. Si rien ne matche -> IA GEMINI
    return "GEMINI_FALLBACK", False

# ==============================================================================
# 5) IA GENERATIVE (LE FILET DE SECURITÉ EMPATHIQUE)
# ==============================================================================

def call_gemini_smart(user_text: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
    if not GEMINI_AVAILABLE or not api_key:
        return "Oups, je suis un peu perdue. Peux-tu reformuler ou contacter l'équipe sur WhatsApp ?", True

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Prompt Psychologique Avancé
    sys_prompt = """
    Tu es Sarah, la coach/assistante du studio SVB.
    Ton rôle : Comprendre l'état d'esprit du client et l'orienter avec bienveillance.
    
    SCÉNARIOS :
    - Client stressé/énergique -> Propose Boxe ou Cross Training (Docks).
    - Client fatigué/mal de dos/besoin de zen -> Propose Pilates Reformer ou Yoga (Lavandières).
    - Client qui veut du résultat physique -> Propose Crossformer ou Cross Body.
    
    RÈGLES :
    - Ne donne JAMAIS de prix inventé.
    - Ne donne JAMAIS d'horaire précis (dis "regarde le planning").
    - Sois courte, punchy et utilise des emojis.
    """
    
    msgs = [{"role": "user", "parts": [sys_prompt]}]
    for m in history[-4:]:
        msgs.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
    msgs.append({"role": "user", "parts": [user_text]})

    try:
        resp = model.generate_content(msgs)
        return resp.text.strip(), False
    except:
        return "J'ai un petit souci de connexion 🧠. Peux-tu répéter ?", True

# ==============================================================================
# 6) INTERFACE UTILISATEUR (STREAMLIT)
# ==============================================================================

def init_chat():
    if "messages" not in st.session_state:
        welcome = random.choice([
            "Hello ! Je suis Sarah. Prête à t'aider pour tes séances chez SVB ! 💪",
            "Bonjour ! Je connais tout sur le studio (Tarifs, Planning, Règles). Dis-moi ce que tu cherches !",
            "Salut 🙂 Besoin de te défouler ou de te détendre aujourd'hui ?"
        ])
        st.session_state.messages = [{"role": "assistant", "content": welcome}]

init_chat()

# Affichage Historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Gestion Entrée Utilisateur
if prompt := st.chat_input("Pose ta question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Essai Déterministe (Base de connaissance)
    response, show_wa = main_router(prompt)

    # 2. Si pas de réponse précise, on appelle l'IA
    if response == "GEMINI_FALLBACK":
        response, show_wa = call_gemini_smart(prompt, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp"])