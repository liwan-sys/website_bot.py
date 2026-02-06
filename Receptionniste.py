# ==============================================================================
# SARAH — SVB CHATBOT (Streamlit + Gemini) — VERSION PROPRE "ANTI-ERREURS" + PLANNING (MODE A)
# ==============================================================================
#
# ✅ VERSION COMPLÈTE (pas de patch partiel)
#
# CE QUE CE CODE GARANTIT
# 1) Tarifs / règles / inscription / unité / séance supp / planning = DÉTERMINISTE (Python)
#    => zéro hallucination.
# 2) Gemini = uniquement orientation / ton / qualification. Et on BLOQUE toute sortie
#    Gemini contenant un prix (anti-hallucination).
# 3) Sarah "humaine" : pas de présentation répétée, réponses naturelles.
#
# IMPORTANT — PLANNING MODE A
# - Le planning est dans la variable PLANNING ci-dessous.
# - ⚠️ Pour l’instant, je l’ai mis en "EXEMPLE" (placeholder).
#   Tu dois remplacer les exemples par TON planning réel (texte / jours / heures).
# - Une fois rempli, Sarah répondra avec les horaires exacts.
#
# RÈGLES OFFICIELLES (TES RÉPONSES)
# - Séance supplémentaire abonné : AU PRORATA DU PASS (prix / nb sessions).
# - À l’unité (non abonné) : Training = 30€ ; Machine = 50€.
# - Essai : 30€ remboursé si inscription.
# - Starter : 99,90€ (5 sessions / 1 mois) MAIS 1 séance par discipline.
# - Human alert : si client demande un humain OU si question trop complexe / info incertaine.
# ==============================================================================

import os
import re
import random
import logging
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple, Any

import streamlit as st

# ------------------------------------------------------------------------------
# 0) Logging
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ------------------------------------------------------------------------------
# 1) Dépendance Gemini
# ------------------------------------------------------------------------------
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR : module 'google.generativeai' manquant. Installe: pip install google-generativeai")
    st.stop()

# ------------------------------------------------------------------------------
# 2) Page config
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# ------------------------------------------------------------------------------
# 3) CSS (identité)
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

.stApp {
  background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
  font-family: 'Lato', sans-serif;
  color: #4A4A4A;
}

#MainMenu, footer, header {visibility: hidden;}

h1 {
  font-family: 'Dancing Script', cursive;
  color: #8FB592;
  text-align: center;
  font-size: 3.5rem !important;
  margin-bottom: 0px !important;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.subtitle {
  text-align: center;
  color: #EBC6A6;
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 25px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.stChatMessage {
  background-color: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid #EBC6A6;
  border-radius: 15px;
  padding: 15px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  color: #1f1f1f !important;
}

.stChatMessage p, .stChatMessage li {
  color: #1f1f1f !important;
  line-height: 1.6;
}

.stButton button {
  background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
  color: white !important;
  border: none;
  border-radius: 25px;
  padding: 12px 25px;
  font-weight: bold;
  width: 100%;
  text-transform: uppercase;
}

.stButton button:hover { transform: scale(1.02); }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# 4) Header
# ------------------------------------------------------------------------------
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

# ==============================================================================
# 5) CONFIG — SOURCE DE VERITÉ (Tarifs + Règles)
# ==============================================================================

WHATSAPP_URL = "https://wa.me/33744919155"
WHATSAPP_LABEL = "📞 Contacter l'équipe (WhatsApp)"

# ---- Prix à l’unité (non abonné) — OFFICIEL ----
UNIT_PRICE = {
    "training": 30.0,
    "machine": 50.0,
}

# ---- Essai — OFFICIEL ----
TRIAL = {
    "price": 30.0,
    "refunded_if_signup": True,
}

# ---- Starter — OFFICIEL ----
STARTER = {
    "price": 99.90,
    "sessions": 5,
    "duration_days": 30,
    "discipline_rule": "1 séance par discipline (pas 5 fois la même discipline).",
}

# ---- Séance supplémentaire abonné — OFFICIEL : prorata du pass ----
EXTRA_SESSION_POLICY = {
    "mode": "pro_rata_of_member_pass",
}

# ---- Studios ----
STUDIOS = {
    "lavandieres": {
        "label": "Lavandières",
        "address": "40 Cours des Lavandières",
        "focus": "Machines (Reformer/Crossformer) + Yoga/Tapis",
    },
    "docks": {
        "label": "Docks",
        "address": "6 Mail André Breton",
        "focus": "Training (Cross/Boxe/Danse) + Kids",
    },
}

# ==============================================================================
# 6) PLANNING (MODE A) — À REMPLACER PAR TON PLANNING RÉEL
# ==============================================================================
#
# Format :
# PLANNING = {
#   "docks": {
#       "lundi": [("07:00", "Cross Training"), ("18:00", "Boxe")],
#       "mardi": [...],
#   },
#   "lavandieres": {
#       "lundi": [("08:00", "Reformer"), ("19:00", "Yoga")],
#   }
# }
#
# ⚠️ Remplace les EXEMPLES ci-dessous par ton planning officiel exact.
# ==============================================================================

PLANNING: Dict[str, Dict[str, List[Tuple[str, str]]]] = {
    "docks": {
        "lundi": [
            ("07:00", "Cross Training"),
            ("12:30", "Cross Core"),
            ("18:30", "Boxe"),
        ],
        "mardi": [
            ("07:00", "Cross Training"),
            ("12:30", "Hyrox"),
            ("19:00", "Danse"),
        ],
        "mercredi": [
            ("07:00", "Cross Training"),
            ("12:30", "Cross Body"),
            ("18:30", "Boxe"),
        ],
        "jeudi": [
            ("07:00", "Cross Training"),
            ("12:30", "Cross Core"),
            ("19:00", "Yoga"),
        ],
        "vendredi": [
            ("07:00", "Cross Training"),
            ("12:30", "Hyrox"),
            ("18:00", "Cross Body"),
        ],
        "samedi": [
            ("10:00", "Cross Training"),
            ("11:00", "Boxe"),
        ],
        "dimanche": [],
    },
    "lavandieres": {
        "lundi": [
            ("08:00", "Reformer"),
            ("12:30", "Crossformer"),
            ("19:00", "Yoga"),
        ],
        "mardi": [
            ("08:00", "Reformer"),
            ("12:30", "Crossformer"),
            ("20:00", "Pilates Tapis"),
        ],
        "mercredi": [
            ("08:00", "Reformer"),
            ("12:30", "Crossformer"),
            ("19:00", "Reformer"),
        ],
        "jeudi": [
            ("08:00", "Reformer"),
            ("12:30", "Crossformer"),
            ("19:00", "Yoga"),
        ],
        "vendredi": [
            ("08:00", "Reformer"),
            ("12:30", "Crossformer"),
            ("18:30", "Reformer"),
        ],
        "samedi": [
            ("10:00", "Reformer"),
            ("11:00", "Crossformer"),
        ],
        "dimanche": [],
    },
}

# ==============================================================================
# 7) Discipline / catégories (routing prix)
# ==============================================================================

DISCIPLINE_TO_CATEGORY = {
    # Machines
    "reformer": "machine",
    "crossformer": "machine",
    "full former": "machine",
    "fullformer": "machine",
    # Training
    "cross": "training",
    "cross training": "training",
    "boxe": "training",
    "danse": "training",
    "yoga": "training",
    "pilates tapis": "training",
    "tapis": "training",
    "focus": "training",
    "full": "training",
    "hyrox": "training",
    "core": "training",
    "body": "training",
    # Kids
    "kids": "kids",
    "enfant": "kids",
    "enfants": "kids",
}

# ==============================================================================
# 8) Pass mensuels
# ==============================================================================
@dataclass(frozen=True)
class PassPrice:
    sessions: int
    price: float

@dataclass(frozen=True)
class PassConfig:
    key: str
    label: str
    category: str
    studio_hint: str
    includes: str
    duration_min: int
    prices: Dict[int, PassPrice]

PASS_CONFIGS: Dict[str, PassConfig] = {}

def add_pass(pass_cfg: PassConfig) -> None:
    PASS_CONFIGS[pass_cfg.key] = pass_cfg

# Machines
add_pass(PassConfig(
    key="reformer",
    label="Pass Reformer",
    category="machine",
    studio_hint="Lavandières",
    includes="Pilates Reformer",
    duration_min=50,
    prices={
        2: PassPrice(2, 70.30),
        4: PassPrice(4, 136.30),
        6: PassPrice(6, 198.30),
        8: PassPrice(8, 256.30),
        10: PassPrice(10, 310.30),
        12: PassPrice(12, 360.30),
    }
))

add_pass(PassConfig(
    key="crossformer",
    label="Pass Crossformer",
    category="machine",
    studio_hint="Lavandières",
    includes="Pilates Crossformer",
    duration_min=50,
    prices={
        2: PassPrice(2, 78.30),
        4: PassPrice(4, 152.30),
        6: PassPrice(6, 222.30),
        8: PassPrice(8, 288.30),
        10: PassPrice(10, 350.30),
        12: PassPrice(12, 408.30),
    }
))

add_pass(PassConfig(
    key="full_former",
    label="Pass Full Former",
    category="machine",
    studio_hint="Lavandières",
    includes="Reformer + Crossformer",
    duration_min=50,
    prices={
        2: PassPrice(2, 74.30),
        4: PassPrice(4, 144.30),
        6: PassPrice(6, 210.30),
        8: PassPrice(8, 272.30),
        10: PassPrice(10, 330.30),
        12: PassPrice(12, 384.30),
    }
))

# Training
add_pass(PassConfig(
    key="cross",
    label="Pass Cross",
    category="training",
    studio_hint="Docks",
    includes="Cross Training • Core • Body • Hyrox • Yoga",
    duration_min=55,
    prices={
        2: PassPrice(2, 30.30),
        4: PassPrice(4, 60.30),
        6: PassPrice(6, 90.30),
        8: PassPrice(8, 116.30),
        10: PassPrice(10, 145.30),
        12: PassPrice(12, 168.30),
    }
))

add_pass(PassConfig(
    key="focus",
    label="Pass Focus",
    category="training",
    studio_hint="Mixte",
    includes="Boxe • Danse • Yoga • Pilates Tapis",
    duration_min=55,
    prices={
        2: PassPrice(2, 36.30),
        4: PassPrice(4, 72.30),
        6: PassPrice(6, 105.30),
        8: PassPrice(8, 136.30),
        10: PassPrice(10, 165.30),
        12: PassPrice(12, 192.30),
    }
))

add_pass(PassConfig(
    key="full",
    label="Pass Full (Cross + Focus)",
    category="training",
    studio_hint="Mixte",
    includes="Tous les cours Cross + Focus",
    duration_min=55,
    prices={
        2: PassPrice(2, 40.30),
        4: PassPrice(4, 80.30),
        6: PassPrice(6, 115.30),
        8: PassPrice(8, 150.30),
        10: PassPrice(10, 180.30),
        12: PassPrice(12, 210.30),
    }
))

# Kids
add_pass(PassConfig(
    key="kids",
    label="Pass Kids",
    category="kids",
    studio_hint="Docks",
    includes="Kids (selon planning)",
    duration_min=55,
    prices={
        2: PassPrice(2, 35.30),
        4: PassPrice(4, 65.30),
    }
))

# ==============================================================================
# 9) Helpers
# ==============================================================================
def eur(value: float) -> str:
    return f"{value:,.2f}€".replace(",", " ").replace(".", ",")

def normalize(text: str) -> str:
    return (text or "").strip().lower()

def find_sessions_count(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", normalize(text))
    return int(m.group(1)) if m else None

def find_pass_key(text: str) -> Optional[str]:
    t = normalize(text)
    patterns = [
        ("full former", "full_former"),
        ("fullformer", "full_former"),
        ("reformer", "reformer"),
        ("crossformer", "crossformer"),
        ("pass cross", "cross"),
        ("pass focus", "focus"),
        ("pass full", "full"),
        ("kids", "kids"),
        ("enfant", "kids"),
        ("enfants", "kids"),
        # fallback words
        ("focus", "focus"),
        ("cross", "cross"),
        ("full", "full"),
    ]
    for needle, key in patterns:
        if needle in t:
            return key
    return None

def unit_price_from_pass(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS_CONFIGS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    return round(p.prices[sessions].price / sessions, 2)

def detect_day(text: str) -> Optional[str]:
    t = normalize(text)
    days = {
        "lundi": ["lundi"],
        "mardi": ["mardi"],
        "mercredi": ["mercredi"],
        "jeudi": ["jeudi"],
        "vendredi": ["vendredi"],
        "samedi": ["samedi"],
        "dimanche": ["dimanche"],
        "aujourd'hui": ["aujourd", "aujourd’hui", "aujourdhui"],
        "demain": ["demain"],
    }
    # on ne fait pas de calcul de date ici, juste mots simples
    for d, keys in days.items():
        if any(k in t for k in keys):
            return d
    return None

def detect_studio(text: str) -> Optional[str]:
    t = normalize(text)
    if "dock" in t or "docks" in t or "parc des docks" in t:
        return "docks"
    if "lavand" in t or "lavandi" in t:
        return "lavandieres"
    return None

def detect_discipline(text: str) -> Optional[str]:
    t = normalize(text)
    # simple match : retourne la discipline clé la plus probable
    keys = [
        "reformer", "crossformer", "cross training", "cross", "boxe", "danse",
        "yoga", "pilates tapis", "tapis", "hyrox", "core", "body", "kids"
    ]
    for k in keys:
        if k in t:
            return k
    return None

# ==============================================================================
# 10) Intents
# ==============================================================================
def is_human_request(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "humain", "quelqu'un", "conseiller", "équipe", "equipe",
        "whatsapp", "appeler", "téléphone", "telephone",
        "contact", "joindre", "parler à", "parler a"
    ])

def is_signup_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "m'inscrire", "inscription", "inscrire", "s’inscrire", "s'inscrire",
        "abonner", "abonnement",
        "identifiant", "identifiants", "mot de passe",
        "connexion", "se connecter", "connecter",
        "je n'ai pas reçu", "j'ai pas reçu", "pas recu", "pas reçu", "mail", "email"
    ])

def is_trial_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["essai", "séance d'essai", "seance d'essai", "découverte", "decouverte", "tester"])

def is_starter_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["starter", "pass starter", "offre starter", "99,90", "99.90"])

def is_unit_price_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "à l'unité", "a l'unite", "unité", "unite",
        "sans abonnement", "sans abo", "sans être abonné", "sans etre abonne",
        "prix d'une séance", "prix d’une séance", "prix séance", "prix seance"
    ])

def is_extra_session_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "séance supp", "seance supp", "séance supplémentaire", "seance supplementaire",
        "ajouter une séance", "ajouter une seance", "rajouter une séance", "rajouter une seance",
        "séance en plus", "seance en plus"
    ])

def is_pass_price_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["tarif", "prix", "coût", "cout", "combien", "abonnement", "pass", "forfait"])

def is_studio_access_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in ["autre studio", "deux studios", "lavandi", "docks", "je peux réserver", "acces", "accès"])

def is_planning_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "planning", "horaire", "horaires", "cours", "séance", "seance",
        "quand", "disponible", "creneau", "créneau", "créneaux", "creneaux"
    ])

def is_support_app_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "bug", "marche pas", "ne marche pas", "impossible", "erreur",
        "connexion", "mot de passe", "identifiant", "application", "appli",
        "paiement", "prélèvement", "prelevement"
    ])

# ==============================================================================
# 11) Réponses déterministes
# ==============================================================================
HUMAN_ACKS = ["OK 🙂", "Parfait.", "Je vois.", "Bien sûr.", "Top.", "D’accord.", "Yes.", "Très bien."]

def ack() -> str:
    return random.choice(HUMAN_ACKS)

def signup_answer() -> str:
    return (
        "Pour vous inscrire :\n\n"
        "1) Vous souscrivez votre abonnement en ligne.\n"
        "2) Après le paiement, vous recevez automatiquement un e-mail avec vos identifiants.\n"
        "3) Vous téléchargez l’application (SVB / Sportigo).\n"
        "4) Vous rentrez les identifiants reçus par e-mail dans l’application.\n"
        "5) Ensuite, vous réservez vos séances sur le planning ✅\n\n"
        "Si vous ne recevez pas l’e-mail (spam / délai), écrivez-nous sur WhatsApp."
    )

def trial_answer() -> str:
    base = f"La séance d’essai est à **{eur(TRIAL['price'])}**."
    if TRIAL.get("refunded_if_signup", False):
        base += " **Elle est remboursée si vous vous inscrivez** ✅"
    return base

def starter_answer() -> str:
    return (
        f"⭐ Offre Starter : **{eur(STARTER['price'])}** — **{STARTER['sessions']} sessions** sur **1 mois**.\n"
        f"📌 Règle : **{STARTER['discipline_rule']}**"
    )

def unit_price_answer(text: str) -> str:
    t = normalize(text)
    cat = None
    for k, v in DISCIPLINE_TO_CATEGORY.items():
        if k in t:
            cat = v
            break

    if cat is None or cat not in ("training", "machine"):
        return (
            "À l’unité (sans abonnement) :\n"
            f"- Training : **{eur(UNIT_PRICE['training'])}**\n"
            f"- Machines : **{eur(UNIT_PRICE['machine'])}**\n\n"
            "Tu cherches plutôt un cours Training (Cross/Boxe/Yoga…) ou une Machine (Reformer/Crossformer) ?"
        )
    if cat == "training":
        return f"À l’unité (sans abonnement), un cours Training est à **{eur(UNIT_PRICE['training'])}**."
    if cat == "machine":
        return f"À l’unité (sans abonnement), une séance Machine est à **{eur(UNIT_PRICE['machine'])}**."
    return (
        "À l’unité (sans abonnement) :\n"
        f"- Training : **{eur(UNIT_PRICE['training'])}**\n"
        f"- Machines : **{eur(UNIT_PRICE['machine'])}**"
    )

def pass_price_answer(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS_CONFIGS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    total = p.prices[sessions].price
    unit = unit_price_from_pass(pass_key, sessions)
    return (
        f"📌 {p.label} — {sessions} sessions/mois\n"
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance (calcul) : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
        f"- Studio : {p.studio_hint}\n"
        f"- Inclus : {p.includes}"
    )

def extra_session_answer(text: str) -> str:
    pass_key = find_pass_key(text)
    sessions = find_sessions_count(text)

    if not pass_key or not sessions:
        return (
            "Pour que je calcule au prorata, il me faut :\n"
            "1) ton pass (Cross / Focus / Full / Reformer / Crossformer / Full Former / Kids)\n"
            "2) le nombre de sessions (2/4/6/8/10/12)\n\n"
            "Exemple : *Pass Cross 4* → prix séance = (prix du pass / 4)."
        )

    u = unit_price_from_pass(pass_key, sessions)
    if u is None:
        return (
            "Je peux le calculer, mais je n’ai pas reconnu la formule exacte.\n"
            "Dis-moi : Cross / Focus / Full / Reformer / Crossformer / Full Former + 2/4/6/8/10/12."
        )

    p = PASS_CONFIGS[pass_key]
    total = p.prices[sessions].price
    return (
        "Séance supplémentaire (au prorata de ton abonnement) :\n"
        f"- Formule : **{p.label} {sessions}**\n"
        f"- Calcul : {eur(total)} / {sessions} = **{eur(u)}**\n\n"
        "Tu veux l’ajouter sur quel cours (et quel studio) ?"
    )

def studio_access_answer(text: str) -> str:
    return (
        "Ça dépend de ta formule.\n"
        "Dis-moi : tu as quel abonnement (Cross / Focus / Full / Reformer / Crossformer / Full Former) "
        "et tu veux réserver dans quel studio (Docks ou Lavandières) ?"
    )

def planning_answer(text: str) -> str:
    studio = detect_studio(text)
    day = detect_day(text)
    discipline = detect_discipline(text)

    # si pas de studio, demander
    if not studio:
        return "Tu veux le planning de quel studio : **Docks** ou **Lavandières** ?"

    # si pas de jour, proposer
    if not day or day in ("aujourd'hui", "demain"):
        # on ne calcule pas les dates ici pour éviter les erreurs, on demande le jour
        return "Tu veux quel jour ? (lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche)"

    day_key = day
    if studio not in PLANNING or day_key not in PLANNING[studio]:
        return "Je n’ai pas ce jour-là sous la main. Dis-moi le studio + le jour et je te le liste."

    slots = PLANNING[studio][day_key]
    if not slots:
        return f"{STUDIOS[studio]['label']} — {day_key.capitalize()} : pas de cours affiché ce jour-là."

    # filtrer par discipline si demandée
    if discipline:
        filtered = [(h, c) for (h, c) in slots if discipline.lower() in c.lower()]
        if filtered:
            slots_to_show = filtered
        else:
            slots_to_show = slots
    else:
        slots_to_show = slots

    lines = [f"**{STUDIOS[studio]['label']} — {day_key.capitalize()}**"]
    for h, c in slots_to_show:
        lines.append(f"- {h} — {c}")
    return "\n".join(lines)

def human_alert_answer(reason: str = "") -> str:
    if reason:
        return f"{reason}\n\n[HUMAN_ALERT]"
    return "Je préfère te mettre avec l’équipe pour être sûr à 100%.\n\n[HUMAN_ALERT]"

# ==============================================================================
# 12) Router déterministe
# ==============================================================================
def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
    # 0) support/app/paiement -> humain (évite erreurs)
    if is_support_app_question(user_text) and ("prix" not in normalize(user_text)) and ("tarif" not in normalize(user_text)):
        ans = human_alert_answer("Je préfère te mettre avec l’équipe pour régler ça rapidement 🙂")
        return ans.replace("[HUMAN_ALERT]", ""), True

    # 1) demande humain
    if is_human_request(user_text):
        ans = human_alert_answer("OK, je te mets avec l’équipe 🙂")
        return ans.replace("[HUMAN_ALERT]", ""), True

    # 2) planning
    if is_planning_question(user_text):
        return planning_answer(user_text), False

    # 3) inscription
    if is_signup_question(user_text):
        return signup_answer(), False

    # 4) essai
    if is_trial_question(user_text):
        return trial_answer(), False

    # 5) starter
    if is_starter_question(user_text):
        return starter_answer(), False

    # 6) séance supp
    if is_extra_session_question(user_text):
        return extra_session_answer(user_text), False

    # 7) unité
    if is_unit_price_question(user_text):
        return unit_price_answer(user_text), False

    # 8) accès autre studio
    if is_studio_access_question(user_text):
        return studio_access_answer(user_text), False

    # 9) prix pass (pass + sessions)
    if is_pass_price_question(user_text):
        pk = find_pass_key(user_text)
        s = find_sessions_count(user_text)
        if pk and s:
            pp = pass_price_answer(pk, s)
            if pp:
                return pp, False

    return None, False

# ==============================================================================
# 13) Gemini (orientation) + anti-hallucination prix
# ==============================================================================
def get_api_key() -> Optional[str]:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY")

@st.cache_resource
def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = f"""
Tu es Sarah (SVB). Tu réponds comme une vraie personne (naturel, simple, pas robot).
Tu NE dis JAMAIS que tu es un bot/IA.

RÈGLE ABSOLUE ANTI-ERREUR :
- Tu n’inventes jamais un prix, un montant, une règle, un délai, une pénalité, un horaire.
- Si la question implique un chiffre/règle/horaire que tu n’as pas dans FACTS, tu réponds :
  "Je préfère confirmer avec l’équipe" + [HUMAN_ALERT].

STYLE :
- Pas de présentation répétée.
- Court, clair.
- 0 à 2 questions de qualification max.
- Pas de "Bienvenue chez SVB" à chaque message.

FACTS AUTORISÉS :
- Prix à l’unité : Training {eur(UNIT_PRICE['training'])} ; Machine {eur(UNIT_PRICE['machine'])}
- Essai : {eur(TRIAL['price'])} (remboursé si inscription)
- Starter : {eur(STARTER['price'])} / {STARTER['sessions']} sessions / 1 mois ; règle = {STARTER['discipline_rule']}
- Séance supp abonné : au prorata du pass (prix du pass / nombre de sessions)
- Inscription : paiement en ligne -> mail auto identifiants -> app (SVB/Sportigo) -> entrer identifiants -> réserver
- Studios : Docks / Lavandières

Si besoin humain => [HUMAN_ALERT]
"""

def build_gemini_contents(history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    trimmed = history[-16:]
    contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for msg in trimmed:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents

def response_contains_price_or_schedule(text: str) -> bool:
    t = text or ""
    # prix: € ou "euros" ou nombre + € ou "30 e"
    if re.search(r"(\€|\beuro\b|\beuros\b)", t, flags=re.IGNORECASE):
        return True
    if re.search(r"\b\d{1,3}\s?€\b", t):
        return True
    # horaires: 07:00 / 7h / 19h30 / 19 h 30
    if re.search(r"\b\d{1,2}:\d{2}\b", t):
        return True
    if re.search(r"\b\d{1,2}\s?h(\s?\d{2})?\b", t, flags=re.IGNORECASE):
        return True
    return False

def gemini_answer(api_key: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    model = get_model(api_key)
    contents = build_gemini_contents(history)

    resp = model.generate_content(
        contents,
        generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 420},
    )
    text = (resp.text or "").strip()
    needs_whatsapp = False

    if "[HUMAN_ALERT]" in text:
        needs_whatsapp = True
        text = text.replace("[HUMAN_ALERT]", "").strip()

    # Anti-hallucination chiffres/horaire
    if response_contains_price_or_schedule(text):
        safe = human_alert_answer("Je préfère confirmer ça avec l’équipe pour éviter une erreur 🙂")
        return safe.replace("[HUMAN_ALERT]", ""), True

    if not text:
        text = "Tu cherches plutôt une séance Machine (Reformer/Crossformer) ou un cours Training (Cross/Boxe/Yoga) ?"

    return text, needs_whatsapp

# ==============================================================================
# 14) "Humain" : accueil 1 seule fois
# ==============================================================================
def first_message() -> str:
    variants = [
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif et je te guide (tonus, perte de poids, mobilité…).",
        "OK 🙂 Tu veux des infos sur les tarifs, le planning, ou l’inscription ?",
    ]
    return random.choice(variants)

def ensure_session_state():
    if "did_greet" not in st.session_state:
        st.session_state["did_greet"] = False
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if not st.session_state["did_greet"] and len(st.session_state["messages"]) == 0:
        st.session_state["messages"].append({"role": "assistant", "content": first_message()})
        st.session_state["did_greet"] = True

ensure_session_state()

# ==============================================================================
# 15) UI — Affichage historique
# ==============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================================================================
# 16) Chat loop
# ==============================================================================
api_key = get_api_key()
prompt = st.chat_input("Posez votre question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    det_answer, needs_whatsapp = deterministic_router(prompt)

    if det_answer is not None:
        with st.chat_message("assistant"):
            st.markdown(det_answer)
            st.session_state.messages.append({"role": "assistant", "content": det_answer})

            if needs_whatsapp:
                st.markdown("---")
                st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)
    else:
        # Pas de déterministe => Gemini
        if not api_key:
            fallback = human_alert_answer("Je préfère te mettre avec l’équipe pour te répondre vite 🙂")
            with st.chat_message("assistant"):
                st.markdown(fallback.replace("[HUMAN_ALERT]", ""))
                st.session_state.messages.append({"role": "assistant", "content": fallback.replace("[HUMAN_ALERT]", "")})
                st.markdown("---")
                st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        text, needs_whatsapp = gemini_answer(api_key, st.session_state.messages)

                    st.markdown(text)
                    st.session_state.messages.append({"role": "assistant", "content": text})

                    if needs_whatsapp:
                        st.markdown("---")
                        st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)

            except Exception:
                log.exception("Erreur Gemini")
                fallback = human_alert_answer("Petit souci technique. Le plus simple : on te répond sur WhatsApp.")
                with st.chat_message("assistant"):
                    st.markdown(fallback.replace("[HUMAN_ALERT]", ""))
                    st.session_state.messages.append({"role": "assistant", "content": fallback.replace("[HUMAN_ALERT]", "")})
                    st.markdown("---")
                    st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)

# ==============================================================================
# FIN
# ==============================================================================

# NOTE IMPORTANT POUR TOI :
# - Remplace les horaires EXEMPLE dans PLANNING par ton planning exact.
# - Une fois fait, Sarah donnera les horaires sans se tromper.
