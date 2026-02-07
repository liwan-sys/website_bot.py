# ==============================================================================
# SARAH — SVB CHATBOT (Streamlit + Gemini) — VERSION CORRIGÉE & FLUIDE
# ==============================================================================
#
# OBJECTIF
# - ZÉRO erreur sur : tarifs, règles, inscription, planning, définitions, engagements.
# - 95% des réponses = Python (déterministe).
# - Gemini = uniquement orientation + reformulation + questions de qualification.
# - Suppression des guardrails excessifs qui bloquaient l'IA.
#
# ==============================================================================

import os
import re
import math
import random
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Set

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
except Exception:
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
.stChatMessage p,.stChatMessage li{
  color:#1f1f1f !important;
  line-height:1.6;
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
# 5) CONFIG — CONTACT / STUDIOS
# ==============================================================================

CONTACT = {
    "whatsapp_url": "https://wa.me/33744919155",
    "whatsapp_label": "📞 Contacter l'équipe (WhatsApp)",
    "email": "hello@studiosvb.fr",
    "instagram": "@svb.officiel",
    "phone": "07 44 91 91 55",
    "sites": ["https://www.studiosvb.com", "https://www.studiosvb.fr"],
}

STUDIOS = {
    "docks": {
        "label": "Parc des Docks",
        "address": "6 Mail André Breton, 93400 Saint-Ouen",
        "notes": "Réservations sur l’app pour les membres SVB.",
    },
    "lavandieres": {
        "label": "Cours Lavandières",
        "address": "40 Cours des Lavandières, 93400 Saint-Ouen",
        "notes": "Chaussettes antidérapantes obligatoires (voir règlement).",
    },
}

# ==============================================================================
# 6) CONFIG — TARIFS (BROCHURES)
# ==============================================================================

# Prix à l’unité (sans abonnement) — validé par toi
UNIT_PRICE = {
    "training": 30.00,  # boxe, cross, yoga, danse...
    "machine": 50.00,   # reformer, crossformer...
}

# Essai — brochure: 30€ et 15€ remboursés si inscription (pas 30)
TRIAL = {
    "price": 30.00,
    "refund_if_signup": 15.00,
}

# Starter — brochure
STARTER = {
    "price": 99.90,
    "sessions": 5,
    "duration": "1 mois",
    "no_engagement": True,
    "no_auto_renew": True,
    "rule": "1 séance par discipline (pas 5 fois la même discipline).",
}

# Option Boost — brochure
BOOST = {
    "price": 9.90,
    "includes": [
        "Frais d’inscription offerts",
        "1 essai gratuit / mois pour un proche (sous réserve de dispo)",
        "Suspension abonnement sans préavis",
    ],
    # La brochure mentionne aussi “engagement 2 mois (coachings) & 3 mois (small groups)”
    # mais elle mentionne en bas “engagement 6 mois pour les pass small groups”.
    # => On ne tranche pas si question trop précise : escalade WhatsApp.
    "engagement_note": "Des conditions d’engagement peuvent s’appliquer selon la formule.",
}

# Frais / engagements — brochure
FEES_AND_ENGAGEMENT = {
    "small_group_registration_fee": 49.00,
    "small_group_engagement_months": 6,   # brochure
    "kids_registration_fee": 29.00,
    "kids_engagement_months": 4,          # brochure
    "coaching_engagement_months": 3,       # brochure (Good Vibes / Duo)
}

# Coaching — brochure
COACHING = {
    "good_vibes": {
        "label": "Coaching Pass Good Vibes",
        "duration_min": 55,
        "prices": {4: 300.30, 8: 560.30},
        "engagement_months": 3,
    },
    "duo": {
        "label": "Coaching Pass Duo",
        "duration_min": 55,
        "prices": {4: 400.60, 8: 720.60},
        "per_person": {4: 200.30, 8: 360.30},
        "engagement_months": 3,
    }
}

# ==============================================================================
# 7) CONFIG — PASS SMALL GROUP (BROCHURE)
# ==============================================================================

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
    pass_family: str  # cross / focus / reformer / crossformer / full / full_former / kids
    where: str        # docks / lavandieres / mixte

PASS: Dict[str, PassConfig] = {}

def add_pass(p: PassConfig) -> None:
    PASS[p.key] = p

# Machines
add_pass(PassConfig(
    key="crossformer",
    label="Pass Crossformer",
    duration_min=50,
    pass_family="crossformer",
    where="lavandieres",
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
    key="reformer",
    label="Pass Reformer",
    duration_min=50,
    pass_family="reformer",
    where="lavandieres",
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
    key="full_former",
    label="Pass Full Former",
    duration_min=50,
    pass_family="full_former",
    where="lavandieres",
    prices={
        2: PassPrice(2, 74.30),
        4: PassPrice(4, 144.30),
        6: PassPrice(6, 210.30),
        8: PassPrice(8, 272.30),
        10: PassPrice(10, 330.30),
        12: PassPrice(12, 384.30),
    }
))

# Training (Docks / mixte)
add_pass(PassConfig(
    key="cross",
    label="Pass Cross",
    duration_min=55,
    pass_family="cross",
    where="docks",
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
    duration_min=55,
    pass_family="focus",
    where="mixte",
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
    duration_min=55,
    pass_family="full",
    where="mixte",
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
    label="Pass Kids (hors juillet/août)",
    duration_min=55,
    pass_family="kids",
    where="docks",
    prices={
        2: PassPrice(2, 35.30),
        4: PassPrice(4, 65.30),
    }
))

KIDS = {
    "extra_session": 18.30,
    "note": "1 activité au choix",
}

# ==============================================================================
# 8) RÈGLEMENT INTÉRIEUR (BROCHURE)
# ==============================================================================

RULES = {
    "booking_window": "En small group, vous pouvez booker vos sessions avec 1 mois d’avance.",
    "cancel_small_group": "Annulation d’un small group : jusqu’à 1h avant le début sans perdre de crédit.",
    "cancel_private": "Annulation d’un coaching privé : jusqu’à 24h avant le créneau sans perdre de crédit.",
    "no_carry_over": "Report de crédits : les sessions du mois en cours ne peuvent pas être reportées sur le mois suivant.",
    "suspension_absence": "Absences : en cas d’absence de plus de 10 jours, un préavis d’un mois est requis pour suspendre l’abonnement.",
    "resiliation": (
        "Résiliation & modification : résiliation par mail avec préavis d’1 mois (1 mensualité) dès la fin d’engagement. "
        "Pas de préavis pour un abonnement supérieur. 1 mois pour un abonnement inférieur."
    ),
    "socks_lavandieres": (
        "SVB Cours Lavandières : chaussettes antidérapantes obligatoires. "
        "En cas d’oubli : achat à 10€ ou prêt à 3€ (10€ supplémentaires facturés si pas rendu)."
    ),
    "late_policy": "+ de 5 minutes de retard = cours refusé.",
}

PARRAINAGE = (
    "Offre de parrainage : parrainez un ami et recevez un cadeau 🎁 "
    "Pour chaque nouveau membre qui s’inscrit grâce à vous, vous recevez un cadeau exclusif."
)

# ==============================================================================
# 9) PLANNING (BROCHURES — planners)
#    On encode chaque cours : studio, jour, heure, nom, catégorie (pour quel pass)
# ==============================================================================

DAY_ORDER = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

@dataclass(frozen=True)
class ClassSlot:
    studio: str             # "docks" / "lavandieres"
    day: str                # "lundi"...
    time: str               # "12h15"
    name: str               # "Reformer"
    tag: str                # "cross" / "focus" / "kids" / "reformer" / "crossformer"

def t(h: str) -> str:
    # normalise (ex: "12H" -> "12h", "9H30" -> "9h30")
    h = h.strip().lower().replace(" ", "")
    h = h.replace("h", "h")
    h = h.replace(":", "h")
    h = h.replace("hh", "h")
    return h

SLOTS: List[ClassSlot] = []

def add_slot(studio: str, day: str, time: str, name: str, tag: str) -> None:
    SLOTS.append(ClassSlot(studio=studio, day=day, time=t(time), name=name, tag=tag))

# ---- DOCKS (Planner Parc des Docks) ----
add_slot("docks", "lundi", "12h", "Cross Training", "cross")
add_slot("docks", "lundi", "13h", "Cross Core", "cross")
add_slot("docks", "lundi", "19h", "Cross Training", "cross")
add_slot("docks", "lundi", "20h", "Cross Body", "cross")

add_slot("docks", "mardi", "12h", "Cross Rox", "cross")
add_slot("docks", "mardi", "19h", "Cross Body", "cross")
add_slot("docks", "mardi", "20h", "Cross Training", "cross")

add_slot("docks", "mercredi", "12h", "Cross Training", "cross")
add_slot("docks", "mercredi", "16h", "Yoga Kids", "kids")
add_slot("docks", "mercredi", "19h", "Cross Training", "cross")
add_slot("docks", "mercredi", "20h", "Boxe", "focus")

add_slot("docks", "jeudi", "8h", "Cross Core", "cross")
add_slot("docks", "jeudi", "12h", "Cross Body", "cross")
add_slot("docks", "jeudi", "13h", "Boxe", "focus")
add_slot("docks", "jeudi", "18h", "Cross Training", "cross")
add_slot("docks", "jeudi", "19h", "Afrodance'All", "focus")

add_slot("docks", "vendredi", "18h", "Cross Rox", "cross")
add_slot("docks", "vendredi", "19h", "Cross Training", "cross")

add_slot("docks", "samedi", "9h30", "Training Kids", "kids")
add_slot("docks", "samedi", "10h30", "Cross Body", "cross")
add_slot("docks", "samedi", "11h30", "Cross Training", "cross")

add_slot("docks", "dimanche", "10h30", "Cross Training", "cross")
add_slot("docks", "dimanche", "11h30", "Cross Yoga", "cross")

# ---- LAVANDIÈRES (Planner Cours Lavandières) ----
add_slot("lavandieres", "lundi", "12h", "Cross-Former", "crossformer")
add_slot("lavandieres", "lundi", "12h15", "Reformer", "reformer")
add_slot("lavandieres", "lundi", "12h30", "Yoga Vinyasa", "focus")
add_slot("lavandieres", "lundi", "18h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "lundi", "19h", "Yoga Vinyasa", "focus")
add_slot("lavandieres", "lundi", "19h15", "Reformer", "reformer")

add_slot("lavandieres", "mardi", "7h30", "Hatha Flow", "focus")
add_slot("lavandieres", "mardi", "11h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "mardi", "12h", "Power Pilates", "focus")
add_slot("lavandieres", "mardi", "13h15", "Reformer", "reformer")
add_slot("lavandieres", "mardi", "18h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "mardi", "19h15", "Reformer", "reformer")
add_slot("lavandieres", "mardi", "20h", "Power Pilates", "focus")

add_slot("lavandieres", "mercredi", "10h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "mercredi", "12h", "Reformer", "reformer")
add_slot("lavandieres", "mercredi", "12h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "mercredi", "19h", "Reformer", "reformer")
add_slot("lavandieres", "mercredi", "19h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "mercredi", "20h", "Reformer", "reformer")

add_slot("lavandieres", "jeudi", "7h", "Classic Pilates", "focus")
add_slot("lavandieres", "jeudi", "12h", "Yoga Vinyasa", "focus")
add_slot("lavandieres", "jeudi", "12h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "jeudi", "12h30", "Reformer", "reformer")
add_slot("lavandieres", "jeudi", "18h", "Cross-Former", "crossformer")
add_slot("lavandieres", "jeudi", "18h45", "Reformer", "reformer")
add_slot("lavandieres", "jeudi", "19h15", "Power Pilates", "focus")
add_slot("lavandieres", "jeudi", "20h15", "Cross Yoga", "cross")
add_slot("lavandieres", "jeudi", "20h30", "Cross-Former", "crossformer")  # libellé "Cross Forme" sur flyer

add_slot("lavandieres", "vendredi", "9h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "vendredi", "10h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "vendredi", "12h", "Reformer", "reformer")
add_slot("lavandieres", "vendredi", "13h", "Reformer", "reformer")
add_slot("lavandieres", "vendredi", "18h", "Classic Pilates", "focus")
add_slot("lavandieres", "vendredi", "18h30", "Reformer", "reformer")
add_slot("lavandieres", "vendredi", "19h15", "Cross-Former", "crossformer")

add_slot("lavandieres", "samedi", "8h45", "Reformer", "reformer")
add_slot("lavandieres", "samedi", "9h", "Cross-Former", "crossformer")
add_slot("lavandieres", "samedi", "9h45", "Reformer", "reformer")
add_slot("lavandieres", "samedi", "10h15", "Classic Pilates", "focus")
add_slot("lavandieres", "samedi", "11h15", "Core & Stretch", "focus")
add_slot("lavandieres", "samedi", "11h30", "Cross-Former", "crossformer")

add_slot("lavandieres", "dimanche", "10h", "Cross-Former", "crossformer")
add_slot("lavandieres", "dimanche", "10h15", "Reformer", "reformer")
add_slot("lavandieres", "dimanche", "11h", "Cross-Former", "crossformer")
add_slot("lavandieres", "dimanche", "11h15", "Reformer", "reformer")
add_slot("lavandieres", "dimanche", "11h30", "Yoga Vinyasa", "focus")

# ==============================================================================
# 10) DÉFINITIONS / COURS (pour répondre “c’est quoi …” sans WhatsApp)
# ==============================================================================

DEFINITIONS: Dict[str, str] = {
    "pilates reformer": (
        "Le **Pilates Reformer** c’est du Pilates sur machine (ressorts). "
        "On travaille fort le gainage, la posture, la mobilité, les fessiers/jambes — et le coach adapte à ton niveau."
    ),
    "reformer": (
        "Le **Reformer** = Pilates sur machine à ressorts. "
        "Très efficace pour gainer, se tonifier et améliorer la posture (débutant OK)."
    ),
    "pilates crossformer": (
        "Le **Pilates Crossformer** c’est une machine Pilates version **plus cardio / intense** : "
        "rythme plus élevé, on transpire, tout en gardant la technique."
    ),
    "crossformer": (
        "Le **Crossformer** = machine Pilates plus **cardio / intense**. "
        "Top si tu veux te tonifier + transpirer + booster le cardio."
    ),
    "cross training": (
        "Le **Cross Training** c’est un entraînement complet : cardio + renfo (haut/bas du corps), "
        "avec des variations selon les séances."
    ),
    "cross core": "Le **Cross Core** cible surtout le gainage (abdos/dos) + stabilité + posture.",
    "cross body": "Le **Cross Body** travaille tout le corps (renfo + cardio) avec un focus tonus.",
    "cross rox": "Le **Cross Rox** = format plus intense/rythmé (cardio + renfo).",
    "cross yoga": "Le **Cross Yoga** mélange mobilité, gainage et flow pour être plus souple et plus solide.",
    "boxe": "La **Boxe** = cardio + technique + renfo (sans combat). Très efficace pour se défouler et se tonifier.",
    "afrodance": "L’**Afrodance'All** = danse cardio, fun, énergie, transpiration garantie.",
    "yoga vinyasa": "Le **Yoga Vinyasa** = enchaînements fluides, respiration, mobilité, renforcement léger.",
    "hatha flow": "Le **Hatha Flow** = yoga plus doux/contrôlé, idéal pour bien commencer.",
    "classic pilates": "Le **Classic Pilates** = travail postural + gainage + mobilité, sans machine.",
    "power pilates": "Le **Power Pilates** = Pilates plus dynamique/intense (gainage + tonus).",
    "core & stretch": "Le **Core & Stretch** = gainage + étirements (parfait pour le dos et la mobilité).",
    "yoga kids": "Le **Yoga Kids** = yoga adapté aux enfants (mobilité, coordination, fun).",
    "training kids": "Le **Training Kids** = sport adapté aux enfants (motricité, renfo, cardio).",
    "small group": "Small Group = petit groupe, coaching plus personnalisé, corrections et adaptations.",
    "coaching": "Coaching = séance personnalisée (individuel ou duo) selon ton objectif.",
}

# ==============================================================================
# 11) HELPERS — TEXTE / PARSING
# ==============================================================================

def eur(x: float) -> str:
    # ex: 60.3 -> "60,30€"
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}€"

def norm(s: str) -> str:
    return (s or "").strip().lower()

def strip_accents_cheap(s: str) -> str:
    # suffisant pour matching simple
    replacements = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a",
        "î": "i", "ï": "i",
        "ô": "o",
        "ù": "u", "û": "u",
        "ç": "c",
        "’": "'", "“": '"', "”": '"',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s

def norm2(s: str) -> str:
    return strip_accents_cheap(norm(s))

def find_sessions_count(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm2(text))
    return int(m.group(1)) if m else None

def find_pass_key(text: str) -> Optional[str]:
    t = norm2(text)
    # ordre important : full former avant full
    patterns = [
        ("full former", "full_former"),
        ("fullformer", "full_former"),
        ("crossformer", "crossformer"),
        ("reformer", "reformer"),
        ("pass cross", "cross"),
        ("pass focus", "focus"),
        ("pass full", "full"),
        ("kids", "kids"),
        ("enfant", "kids"),
        ("cross", "cross"),
        ("focus", "focus"),
        ("full", "full"),
    ]
    for needle, key in patterns:
        if needle in t:
            return key
    return None

def pass_unit_price(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS.get(pass_key)
    if not p:
        return None
    if sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    return round(total / sessions, 2)

def extract_day(text: str) -> Optional[str]:
    t = norm2(text)
    for d in DAY_ORDER:
        if d in t:
            return d
    # variantes
    if "aujourdhui" in t or "aujourd'hui" in t:
        return None
    return None

def extract_studio(text: str) -> Optional[str]:
    t = norm2(text)
    if "dock" in t or "parc des docks" in t:
        return "docks"
    if "lavandi" in t or "cours lavandieres" in t:
        return "lavandieres"
    return None

def extract_course_key(text: str) -> Optional[str]:
    """
    Retourne une clé canonique du type :
    'reformer', 'crossformer', 'boxe', 'cross training', 'yoga vinyasa', ...
    """
    t = norm2(text)

    # alias rapides
    aliases = {
        "pilate reformer": "reformer",
        "pilates reformer": "reformer",
        "reformer": "reformer",
        "pilate crossformer": "crossformer",
        "pilates crossformer": "crossformer",
        "crossformer": "crossformer",
        "cross-former": "crossformer",
        "cross former": "crossformer",

        "boxe": "boxe",
        "boxing": "boxe",

        "cross training": "cross training",
        "cross-training": "cross training",
        "cross core": "cross core",
        "cross-core": "cross core",
        "cross body": "cross body",
        "cross-body": "cross body",
        "cross rox": "cross rox",
        "cross-rox": "cross rox",
        "cross yoga": "cross yoga",
        "cross-yoga": "cross yoga",

        "yoga vinyasa": "yoga vinyasa",
        "vinyasa": "yoga vinyasa",
        "hatha": "hatha flow",
        "hatha flow": "hatha flow",

        "classic pilates": "classic pilates",
        "pilates classic": "classic pilates",
        "power pilates": "power pilates",
        "core & stretch": "core & stretch",
        "core and stretch": "core & stretch",
        "stretch": "core & stretch",

        "yoga kids": "yoga kids",
        "training kids": "training kids",
        "kids": "kids",

        "afrodance": "afrodance",
        "afrodance'all": "afrodance",
        "afrodance all": "afrodance",
    }

    # match plus long d’abord
    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t:
            return aliases[k]

    return None

def tag_to_pass_hint(tag: str) -> str:
    # Donne un indice “quel pass” pour un cours planning
    mapping = {
        "cross": "Pass Cross (ou Pass Full)",
        "focus": "Pass Focus (ou Pass Full)",
        "kids": "Pass Kids",
        "reformer": "Pass Reformer",
        "crossformer": "Pass Crossformer",
    }
    return mapping.get(tag, "selon la formule")

# ==============================================================================
# 12) INTENTS — DÉTECTION (TRÈS LARGE)
# ==============================================================================

def has_any(text: str, words: List[str]) -> bool:
    t = norm2(text)
    return any(w in t for w in words)

def intent_human(text: str) -> bool:
    return has_any(text, [
        "humain", "conseiller", "equipe", "équipe", "whatsapp",
        "appeler", "telephone", "téléphone", "contact", "joindre",
        "parler a", "parler à", "urgent", "stp appelle", "je veux parler"
    ])

def intent_signup(text: str) -> bool:
    # Must explicitely mention signup actions (removed "abonnement" alone)
    signup_keywords = ["m'inscrire", "inscrire", "inscription", "s'inscrire", "creer un compte", "créer un compte", "nouvel adherent", "nouveau membre"]
    app_keywords = ["identifiant", "mot de passe", "connexion", "connecter", "pas reçu mail", "pas recu mail"]
    return has_any(text, signup_keywords + app_keywords)

def intent_suspension(text: str) -> bool:
    return has_any(text, ["pause", "suspendre", "suspension", "arret", "arrêt", "vacance"])

def intent_trial(text: str) -> bool:
    return has_any(text, ["essai", "seance d'essai", "séance d'essai", "tester", "découverte", "decouverte"])

def intent_starter(text: str) -> bool:
    return has_any(text, ["starter", "new pass starter", "99,90", "99.90", "offre starter"])

def intent_boost(text: str) -> bool:
    return has_any(text, ["boost", "option boost", "svb boost"])

def intent_parrainage(text: str) -> bool:
    return has_any(text, ["parrainage", "parrainer", "parraine", "parrain"])

def intent_rules(text: str) -> bool:
    return has_any(text, [
        "annulation", "annuler", "report", "reporter", "cumul", "cumulable",
        "resiliation", "résiliation", "preavis", "préavis",
        "absence", "absent", "retard", "chaussette", "chaussettes",
        "reglement", "règlement", "interieur", "intérieur"
    ])

def intent_unit_price(text: str) -> bool:
    return has_any(text, [
        "a l'unite", "à l'unité", "unite", "unité", "sans abonnement", "sans abo",
        "prix d'une seance", "prix d’une seance", "prix seance", "combien coute une seance",
        "combien ca coute", "tarif a l'unite"
    ])

def intent_pass_price(text: str) -> bool:
    return has_any(text, ["pass", "forfait", "tarif", "prix", "combien", "abonnement"])

def intent_extra_session(text: str) -> bool:
    return has_any(text, [
        "seance supp", "séance supp", "seance supplementaire", "séance supplémentaire",
        "ajouter une seance", "ajouter une séance", "rajouter", "seance en plus", "séance en plus"
    ])

def intent_definition(text: str) -> bool:
    return has_any(text, [
        "c'est quoi", "c quoi", "ça veut dire", "definition", "définition",
        "explique", "expliquer", "difference", "différence"
    ])

def intent_planning(text: str) -> bool:
    return has_any(text, [
        "planning", "horaire", "horaires", "quel jour", "quels jours",
        "a quelle heure", "à quelle heure", "quand", "cours de", "seance de", "séance de"
    ])

def intent_coaching(text: str) -> bool:
    return has_any(text, ["coaching", "coach", "individuel", "duo", "good vibes"])

def intent_kids(text: str) -> bool:
    return has_any(text, ["kids", "enfant", "enfants", "ado", "training kids", "yoga kids"])

# ==============================================================================
# 13) RÉPONSES DÉTERMINISTES — (ZÉRO HALLUCINATION)
# ==============================================================================

ACKS = ["OK 🙂", "Parfait.", "Je vois.", "Bien sûr.", "Top.", "D’accord.", "Yes.", "Très bien."]

def ack() -> str:
    return random.choice(ACKS)

def human_alert(reason: str = "") -> Tuple[str, bool]:
    txt = reason.strip() if reason else "Je te mets directement avec l’équipe pour être sûr à 100% 🙂"
    return txt, True

def answer_suspension() -> str:
    return (
        "🛑 **Mettre en pause son abonnement** :\n\n"
        "1. **Avec l'Option Boost** : La suspension est libre, sans préavis et sans justificatif.\n"
        "2. **Sans Option Boost (Standard)** : La suspension n'est possible que pour une absence **supérieure à 10 jours** et nécessite un **préavis d'1 mois**.\n\n"
        "Pour activer une suspension, contactez-nous directement via WhatsApp."
    )

def answer_signup() -> str:
    # validé par toi
    return (
        "Pour t’inscrire :\n\n"
        "1) Tu souscris ton abonnement en ligne.\n"
        "2) Après le paiement, tu reçois automatiquement un e-mail avec tes identifiants.\n"
        "3) Tu télécharges l’application (SVB / Sportigo).\n"
        "4) Tu rentres les identifiants reçus par e-mail dans l’application.\n"
        "5) Ensuite tu réserves tes séances sur le planning ✅\n\n"
        "Si tu ne reçois pas l’e-mail (spam / délai), écris-nous sur WhatsApp."
    )

def answer_trial() -> str:
    return (
        f"La séance d’essai est à **{eur(TRIAL['price'])}**.\n"
        f"👉 **{eur(TRIAL['refund_if_signup'])} remboursés si inscription** ✅"
    )

def answer_starter() -> str:
    return (
        f"⭐ **New Pass Starter** : **{eur(STARTER['price'])}** — **{STARTER['sessions']} sessions** — valable **{STARTER['duration']}**.\n"
        f"✅ Pas d’engagement / pas de reconduction.\n"
        f"📌 Règle : **{STARTER['rule']}**"
    )

def answer_boost() -> str:
    bullets = "\n".join([f"- {x}" for x in BOOST["includes"]])
    return (
        f"⚡ **Option SVB Boost** : **{eur(BOOST['price'])}/mois** (en + d’un pass)\n"
        f"{bullets}\n\n"
        f"📌 {BOOST['engagement_note']}"
    )

def answer_parrainage() -> str:
    return PARRAINAGE

def answer_unit_price(text: str) -> str:
    # On répond utile même si la personne ne précise pas (abonné ou pas)
    course = extract_course_key(text)
    if course in ("reformer", "crossformer"):
        return f"Sans abonnement, une séance **Machine** est à **{eur(UNIT_PRICE['machine'])}**."
    if course in ("boxe", "cross training", "cross core", "cross body", "cross rox", "cross yoga", "afrodance", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch", "yoga kids", "training kids"):
        return f"Sans abonnement, une séance **Training / cours** est à **{eur(UNIT_PRICE['training'])}**."
    return (
        "Sans abonnement :\n"
        f"- Cours **Training** : **{eur(UNIT_PRICE['training'])}**\n"
        f"- Séance **Machine** : **{eur(UNIT_PRICE['machine'])}**\n\n"
        "Tu cherches plutôt un cours Training (Boxe/Cross/Yoga…) ou une Machine (Reformer/Crossformer) ?"
    )

def answer_boxe_price() -> str:
    # “combien coûte un cours de boxe” => on donne prix unité + option abonné prorata
    return (
        f"Un cours de **Boxe** :\n"
        f"- Sans abonnement : **{eur(UNIT_PRICE['training'])}**\n"
        f"- Si tu es abonné(e) : ça dépend de ton pass (au **prorata** : prix du pass / nb sessions). "
        f"Dis-moi juste ton pass et ton nombre de sessions (ex: *Pass Focus 4*) et je te calcule."
    )

def answer_pass_price(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS.get(pass_key)
    if not p:
        return None
    if sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    unit = pass_unit_price(pass_key, sessions)
    extra = ""

    # note kids
    if pass_key == "kids":
        extra = f"\n- Séance supplémentaire kids : **{eur(KIDS['extra_session'])}**"

    return (
        f"📌 **{p.label}** — {sessions} sessions / mois\n"
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance (calcul) : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
        f"- Studio : {STUDIOS[p.where]['label'] if p.where in STUDIOS else p.where}\n"
        f"{extra}"
    )

def answer_extra_session(text: str) -> str:
    # règle : prorata du pass (sauf kids = 18,30€)
    pk = find_pass_key(text)
    n = find_sessions_count(text)

    if pk == "kids":
        return f"Pour Kids, la séance supplémentaire est à **{eur(KIDS['extra_session'])}**."

    if not pk or not n:
        return (
            "Je peux te calculer la séance supplémentaire **au prorata** 👇\n\n"
            "Dis-moi :\n"
            "1) ton pass (Cross / Focus / Full / Reformer / Crossformer / Full Former)\n"
            "2) le nombre de sessions (2/4/6/8/10/12)\n\n"
            "Exemple : *Pass Cross 4* → prix séance = (prix du pass / 4)."
        )

    u = pass_unit_price(pk, n)
    if u is None:
        return (
            "Je peux te le calculer, mais je n’ai pas reconnu la formule exacte.\n"
            "Écris-moi : Cross/Focus/Full/Reformer/Crossformer/Full Former + 2/4/6/8/10/12."
        )

    p = PASS[pk]
    total = p.prices[n].total
    return (
        "✅ Séance supplémentaire (au prorata de ton abonnement) :\n"
        f"- Formule : **{p.label} {n}**\n"
        f"- Calcul : {eur(total)} / {n} = **{eur(u)}**"
    )

def answer_rules(text: str) -> str:
    t = norm2(text)

    # Réponses ciblées plutôt qu’un pavé
    if any(k in t for k in ["annuler", "annulation"]):
        return f"{RULES['cancel_small_group']}\n\n{RULES['cancel_private']}"

    if any(k in t for k in ["report", "reporter", "cumul", "cumulable"]):
        return RULES["no_carry_over"]

    if any(k in t for k in ["resiliation", "résiliation", "preavis", "préavis", "modifier", "modification"]):
        return RULES["resiliation"]

    if any(k in t for k in ["suspension", "absence", "absent"]):
        return RULES["suspension_absence"]

    if any(k in t for k in ["retard"]):
        return RULES["late_policy"]

    if any(k in t for k in ["chaussette", "chaussettes"]):
        return f"{RULES['socks_lavandieres']}\n{RULES['late_policy']}"

    if any(k in t for k in ["book", "booking", "reserver", "réserver"]):
        return RULES["booking_window"]

    # fallback
    return (
        "Règlement (résumé) :\n"
        f"- {RULES['booking_window']}\n"
        f"- {RULES['cancel_small_group']}\n"
        f"- {RULES['cancel_private']}\n"
        f"- {RULES['no_carry_over']}\n"
        f"- {RULES['suspension_absence']}\n"
        f"- {RULES['resiliation']}\n"
        f"- {RULES['socks_lavandieres']}\n"
        f"- {RULES['late_policy']}"
    )

def answer_definition(text: str) -> Optional[str]:
    """
    Gère :
    - "c’est quoi le reformer"
    - "c’est quoi le pilates crossformer"
    - "différence reformer crossformer"
    """
    t = norm2(text)
    course = extract_course_key(text)

    # différence
    if "difference" in t or "différence" in t:
        if ("reformer" in t and ("crossformer" in t or "cross-former" in t or "cross former" in t)):
            return (
                "Différence **Reformer vs Crossformer** :\n"
                "- **Reformer** : Pilates machine plus contrôlé, super pour posture/gainage/tonus.\n"
                "- **Crossformer** : machine plus **cardio / intense**, ça monte plus vite en rythme.\n"
                "Les deux sont adaptés débutants : le coach ajuste."
            )

    # définitions simples
    if course == "reformer":
        return DEFINITIONS.get("reformer")
    if course == "crossformer":
        return DEFINITIONS.get("crossformer")
    if course == "boxe":
        return DEFINITIONS.get("boxe")
    if course == "cross training":
        return DEFINITIONS.get("cross training")

    # match dictionnaire (si phrase complète)
    for k in sorted(DEFINITIONS.keys(), key=len, reverse=True):
        if k in t:
            return DEFINITIONS[k]

    return None

def answer_coaching(text: str) -> str:
    # si la personne demande “tarifs coaching”
    gv = COACHING["good_vibes"]
    duo = COACHING["duo"]
    return (
        f"Coaching (55 min) — engagement **{FEES_AND_ENGAGEMENT['coaching_engagement_months']} mois** :\n\n"
        f"✅ **{gv['label']}**\n"
        f"- 4 séances/mois : **{eur(gv['prices'][4])}**\n"
        f"- 8 séances/mois : **{eur(gv['prices'][8])}**\n\n"
        f"✅ **{duo['label']}**\n"
        f"- 4 séances/mois : **{eur(duo['prices'][4])}** (soit **{eur(duo['per_person'][4])}/pers**)\n"
        f"- 8 séances/mois : **{eur(duo['prices'][8])}** (soit **{eur(duo['per_person'][8])}/pers**)"
    )

def answer_kids(text: str) -> str:
    return (
        f"Kids (hors juillet/août) — engagement **{FEES_AND_ENGAGEMENT['kids_engagement_months']} mois** :\n"
        f"- 2 séances/mois : **{eur(PASS['kids'].prices[2].total)}**\n"
        f"- 4 séances/mois : **{eur(PASS['kids'].prices[4].total)}**\n"
        f"- Séance supplémentaire : **{eur(KIDS['extra_session'])}**\n"
        f"- Frais de dossier : **{eur(FEES_AND_ENGAGEMENT['kids_registration_fee'])}**\n"
        f"📌 {KIDS['note']}"
    )

# ==============================================================================
# 14) PLANNING — ANSWERS
# ==============================================================================

def slots_for(studio: Optional[str] = None, day: Optional[str] = None, course_key: Optional[str] = None) -> List[ClassSlot]:
    out = []
    for s in SLOTS:
        if studio and s.studio != studio:
            continue
        if day and s.day != day:
            continue
        if course_key:
            # course_key -> match name
            ck = norm2(course_key)
            nm = norm2(s.name)

            if ck == "reformer" and "reformer" not in nm:
                continue
            if ck == "crossformer" and "cross" not in nm:
                # Cross-Former contains "cross"
                if "former" not in nm:
                    continue
            if ck == "boxe" and "boxe" not in nm:
                continue
            if ck == "cross training" and "cross training" not in nm:
                continue
            if ck == "cross core" and "cross core" not in nm:
                continue
            if ck == "cross body" and "cross body" not in nm:
                continue
            if ck == "cross rox" and "cross rox" not in nm:
                continue
            if ck == "cross yoga" and "cross yoga" not in nm:
                continue
            if ck == "yoga vinyasa" and "vinyasa" not in nm:
                continue
            if ck == "hatha flow" and "hatha" not in nm:
                continue
            if ck == "classic pilates" and "classic" not in nm:
                continue
            if ck == "power pilates" and "power" not in nm:
                continue
            if ck == "core & stretch" and "stretch" not in nm:
                continue
            if ck == "yoga kids" and ("kids" not in nm or "yoga" not in nm):
                continue
            if ck == "training kids" and ("kids" not in nm or "training" not in nm):
                continue

        out.append(s)
    return out

def format_slots_grouped(slots: List[ClassSlot]) -> str:
    # regroupe par jour
    by_day: Dict[str, List[ClassSlot]] = {d: [] for d in DAY_ORDER}
    for s in slots:
        by_day[s.day].append(s)

    lines = []
    for d in DAY_ORDER:
        items = by_day[d]
        if not items:
            continue
        times = ", ".join([f"{x.time} ({x.name})" for x in sorted(items, key=lambda z: (len(z.time), z.time))])
        lines.append(f"- **{d.capitalize()}** : {times}")
    return "\n".join(lines) if lines else "Je n’ai rien trouvé sur le planning actuel."

def answer_planning(text: str) -> str:
    studio = extract_studio(text)
    day = extract_day(text)
    course_key = extract_course_key(text)

    # Cas 1 : “quel jour il y a du reformer”
    if course_key and not day:
        # Si le studio n’est pas précisé, on choisit celui le plus logique
        if studio is None:
            if course_key in ("reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch"):
                studio = "lavandieres"
            elif course_key in ("boxe", "afrodance", "cross training", "cross core", "cross body", "cross rox", "training kids", "yoga kids"):
                studio = "docks"

        found = slots_for(studio=studio, course_key=course_key) if studio else slots_for(course_key=course_key)

        if not found:
            return "Je ne vois pas ce cours sur le planning actuel. Tu parles de quel studio : Docks ou Lavandières ?"

        studio_txt = f" — {STUDIOS[studio]['label']}" if studio in STUDIOS else ""
        hint = tag_to_pass_hint(found[0].tag)
        return (
            f"Voilà les créneaux **{course_key.capitalize()}**{studio_txt} 👇\n\n"
            f"{format_slots_grouped(found)}\n\n"
            f"✅ Cours accessible via : **{hint}**"
        )

    # Cas 2 : “planning lavandières” / “horaires docks”
    if course_key is None and studio and not day:
        found = slots_for(studio=studio)
        return (
            f"Planning **{STUDIOS[studio]['label']}** 👇\n\n"
            f"{format_slots_grouped(found)}"
        )

    # Cas 3 : “jeudi reformer”
    if course_key and day:
        if studio is None:
            # studio par défaut cohérent
            studio = "lavandieres" if course_key in ("reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch") else "docks"

        found = slots_for(studio=studio, day=day, course_key=course_key)
        if not found:
            return f"Je ne vois pas **{course_key}** le **{day}** sur {STUDIOS[studio]['label']}. Tu veux que je te donne tous les jours où il y en a ?"
        hint = tag_to_pass_hint(found[0].tag)
        times = ", ".join([f"{x.time}" for x in found])
        return f"**{day.capitalize()}** : {course_key.capitalize()} à **{times}** ({STUDIOS[studio]['label']}). ✅ {hint}"

    # Cas 4 : “quel jour il y a des cours” sans préciser
    if course_key is None and not studio and not day:
        return (
            "Tu cherches le planning de quel studio ?\n"
            f"- **{STUDIOS['docks']['label']}** (Cross/Boxe/Kids…)\n"
            f"- **{STUDIOS['lavandieres']['label']}** (Reformer/Crossformer/Yoga…)\n\n"
            "Dis-moi juste “planning docks” ou “planning lavandières”."
        )

    # fallback
    if studio and day:
        found = slots_for(studio=studio, day=day)
        if not found:
            return f"Je ne vois rien le **{day}** sur {STUDIOS[studio]['label']}."
        return f"{STUDIOS[studio]['label']} — {day.capitalize()} 👇\n\n" + format_slots_grouped(found)

    return "Dis-moi le cours + le studio (ex: “Reformer lavandières” ou “Boxe docks”) et je te donne les créneaux."

# ==============================================================================
# 15) ROUTER DÉTERMINISTE (PRIORITÉS)
# ==============================================================================

def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
    t = norm2(user_text)

    # 0) humain direct
    if intent_human(user_text):
        return human_alert("OK 🙂 je te mets avec l’équipe." )

    # 1) Suspension (AVANT l'inscription)
    if intent_suspension(user_text):
        return answer_suspension(), False

    # 2) inscription
    if intent_signup(user_text):
        return answer_signup(), False

    # 3) planning
    # (on le met haut pour que “quel jour reformer” marche immédiatement)
    if intent_planning(user_text):
        # planning doit passer avant “prix” etc
        ck = extract_course_key(user_text)
        if ("planning" in t) or ("horaire" in t) or ("quel jour" in t) or ("a quelle heure" in t) or ck is not None:
            return answer_planning(user_text), False

    # 4) définitions
    if intent_definition(user_text):
        d = answer_definition(user_text)
        if d:
            return d, False

    # 5) essai / starter / boost / parrainage
    if intent_trial(user_text):
        return answer_trial(), False

    if intent_starter(user_text):
        return answer_starter(), False

    if intent_boost(user_text):
        return answer_boost(), False

    if intent_parrainage(user_text):
        return answer_parrainage(), False

    # 6) règles
    if intent_rules(user_text):
        return answer_rules(user_text), False

    # 7) coaching / kids
    if intent_coaching(user_text):
        return answer_coaching(user_text), False

    if intent_kids(user_text):
        return answer_kids(user_text), False

    # 8) prix spécifique : boxe (évite qu’il hésite)
    if "boxe" in t and ("combien" in t or "prix" in t or "tarif" in t or "coute" in t or "coûte" in t):
        return answer_boxe_price(), False

    # 9) séance supp
    if intent_extra_session(user_text):
        return answer_extra_session(user_text), False

    # 10) prix à l’unité
    if intent_unit_price(user_text):
        return answer_unit_price(user_text), False

    # 11) prix d’un pass
    if intent_pass_price(user_text):
        pk = find_pass_key(user_text)
        n = find_sessions_count(user_text)
        if pk and n:
            out = answer_pass_price(pk, n)
            if out:
                return out, False

    # rien trouvé
    return None, False

# ==============================================================================
# 16) GEMINI — ORIENTATION UNIQUEMENT (SANS GUARDRAILS)
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
Tu fais partie de l’équipe SVB. Tu écris comme une vraie personne (naturel, simple).
Tu NE dis JAMAIS que tu es une IA ou un bot.

RÈGLES ABSOLUES :
- Tu ne donnes AUCUN horaire précis.
- Tu n’inventes AUCUN prix.
- Si tu dois parler prix ou horaire, dis que tu ne les as pas et invite à préciser.
- Tu peux poser 1 ou 2 questions de qualification max.
- Si tu n’es pas sûr, tu proposes WhatsApp.

Ce que tu peux faire :
- Conseiller une orientation (Machine vs Training).
- Proposer un essai / starter (sans répéter des chiffres si pas nécessaire).
- Demander objectif, niveau, dispo, préférence studio.

IMPORTANT :
- Pas de “Bienvenue chez SVB” à chaque message.
- Pas de présentation répétée.
"""

def build_gemini_contents(history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    # On envoie un historique court
    max_turns = 18
    trimmed = history[-max_turns:]
    contents: List[Dict[str, Any]] = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for msg in trimmed:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents

def call_gemini(api_key: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    model = get_model(api_key)
    contents = build_gemini_contents(history)
    resp = model.generate_content(
        contents,
        generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 320},
    )
    text = (resp.text or "").strip()
    needs_whatsapp = False

    # Si la personne demande humain (Gemini parfois propose)
    if "whatsapp" in norm2(text) or "equipe" in norm2(text) or "équipe" in norm2(text):
        # On ne force pas le bouton, sauf si c’est vraiment un renvoi direct
        if "ecris nous" in norm2(text) or "écris nous" in norm2(text) or "contacte" in norm2(text):
            needs_whatsapp = True

    if not text:
        text = "Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?"

    return text, needs_whatsapp

# ==============================================================================
# 17) UX — ACCUEIL 1 FOIS / STYLE HUMAIN
# ==============================================================================

def first_message() -> str:
    variants = [
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ce que tu veux travailler (tonus, cardio, mobilité…) et je te guide.",
        "OK 🙂 Tu veux plutôt réserver aux Docks ou aux Lavandières ?",
    ]
    return random.choice(variants)

def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "did_greet" not in st.session_state:
        st.session_state.did_greet = False

    if not st.session_state.did_greet and len(st.session_state.messages) == 0:
        st.session_state.messages.append({"role": "assistant", "content": first_message()})
        st.session_state.did_greet = True

ensure_state()

# ==============================================================================
# 18) SIDEBAR — INFOS / DEBUG (optionnel)
# ==============================================================================

with st.sidebar:
    st.markdown("### SVB • Infos")
    st.caption(f"WhatsApp : {CONTACT['phone']}")
    st.caption(f"Email : {CONTACT['email']}")
    st.caption(f"Instagram : {CONTACT['instagram']}")
    st.divider()
    st.markdown("### Debug")
    if st.checkbox("Afficher le nombre de lignes du fichier", value=False):
        # approximatif : on affiche une aide, pas lecture du fichier
        st.info("Pour compter les lignes : `wc -l app.py` (ou ton nom de fichier).")

# ==============================================================================
# 19) UI — HISTORIQUE
# ==============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================================================================
# 20) CHAT LOOP
# ==============================================================================
api_key = get_api_key()
prompt = st.chat_input("Posez votre question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1) déterministe d’abord
    det, needs_wa = deterministic_router(prompt)

    if det is not None:
        with st.chat_message("assistant"):
            st.markdown(det)
        st.session_state.messages.append({"role": "assistant", "content": det})

        if needs_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

    else:
        # 2) Gemini (si dispo + clé)
        if not GEMINI_AVAILABLE or not api_key:
            txt, needs_wa2 = human_alert("Je peux te guider, mais là je préfère te mettre avec l’équipe 🙂")
            with st.chat_message("assistant"):
                st.markdown(txt)
            st.session_state.messages.append({"role": "assistant", "content": txt})
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        txt, needs_wa2 = call_gemini(api_key, st.session_state.messages)
                    st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})

                if needs_wa2:
                    st.markdown("---")
                    st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

            except Exception:
                log.exception("Erreur Gemini")
                txt, needs_wa2 = human_alert("Petit souci technique. Le plus simple : WhatsApp 🙂")
                with st.chat_message("assistant"):
                    st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
                st.markdown("---")
                st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

# ==============================================================================
# FIN
# ==============================================================================