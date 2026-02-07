# -*- coding: utf-8 -*-
"""
knowledge.py — Base de connaissance structurée SVB (tarifs, règles, planning, définitions).

✅ Objectif :
- Centraliser les "FACTS" vérifiés.
- Fournir des helpers (format €, extraction cours/pass, planning).
- Zéro logique UI ici : uniquement données + fonctions.

Sources utilisées pour cette version :
- Page Tarifs SVB (abonnements + contenus de pass)
- Page Studio / Planning (horaires)
- FAQ SVB (règles : chaussettes, annulation, retard, résiliation, suspension, engagement)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

# -----------------------------------------------------------------------------
# CONTACT / STUDIOS
# -----------------------------------------------------------------------------

CONTACT = {
    "whatsapp_url": "https://wa.me/33744919155",
    "whatsapp_label": "📞 Contacter l'équipe (WhatsApp)",
    "email": "hello@studiosvb.fr",
    "instagram": "@svb.officiel",
    "phone": "07 44 91 91 55",
}

STUDIOS: Dict[str, Dict[str, str]] = {
    "docks": {
        "label": "Parc des Docks",
        "address": "6 Mail André Breton, 93400 Saint-Ouen",
    },
    "lavandieres": {
        "label": "Cours Lavandières",
        "address": "40 Cours des Lavandières, 93400 Saint-Ouen",
    },
    "mixte": {
        "label": "Docks + Lavandières",
        "address": "Selon le cours",
    },
}

DAY_ORDER = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# -----------------------------------------------------------------------------
# FORMATTERS
# -----------------------------------------------------------------------------

def eur(x: float) -> str:
    # ex: 60.3 -> "60,30€"
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}€"

def strip_accents_cheap(s: str) -> str:
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

def norm(s: str) -> str:
    return (s or "").strip().lower()

def norm2(s: str) -> str:
    return strip_accents_cheap(norm(s))

# -----------------------------------------------------------------------------
# TARIFS — UNITÉ / ESSAI / STARTER / BOOST / FRAIS
# -----------------------------------------------------------------------------

UNIT_PRICE = {
    "training": 30.00,  # Boxe / Cross / Yoga / Danse / Stretch / Pilates sol
    "machine": 50.00,   # Reformer / Crossformer
}

TRIAL = {"price": 30.00, "refund_if_signup": 15.00}

STARTER = {
    "price": 99.90,
    "sessions": 5,
    "duration": "1 mois",
    "rule": "1 séance par discipline (pas 5 fois la même discipline).",
}

BOOST = {
    "price": 9.90,
    "includes": [
        "Frais d’inscription offerts",
        "1 essai gratuit / mois pour un proche (sous réserve de dispo)",
        "Suspension abonnement sans préavis",
    ],
    "engagement_note": "L’option Boost peut modifier certaines conditions selon la formule.",
}

FEES_AND_ENGAGEMENT = {
    "small_group_registration_fee": 49.00,
    "small_group_engagement_months": 3,  # affiché sur la page Tarifs
    "small_group_engagement_note": "La FAQ mentionne que certains abonnements mensuels peuvent être sur 3 ou 6 mois selon la formule.",
    "kids_registration_fee": 29.00,
    "kids_engagement_months": 4,
    "coaching_engagement_months": 3,
}

# -----------------------------------------------------------------------------
# PASSES (ABONNEMENTS) — STRUCTURÉS
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PassPrice:
    sessions: int
    total: float

@dataclass(frozen=True)
class PassConfig:
    key: str
    label: str
    duration_min: int
    where: str                 # docks / lavandieres / mixte
    prices: Dict[int, PassPrice]
    includes: List[str]        # résumé contenu (utile)
    category: str              # "training" | "machine"

PASS: Dict[str, PassConfig] = {}

def add_pass(p: PassConfig) -> None:
    PASS[p.key] = p

# Machines
add_pass(PassConfig(
    key="reformer",
    label="Pass Reformer",
    duration_min=50,
    where="lavandieres",
    category="machine",
    includes=["Pilates Reformer (machine)"],
    prices={
        2: PassPrice(2, 70.30),
        4: PassPrice(4, 136.30),
        6: PassPrice(6, 198.30),
        8: PassPrice(8, 256.30),
        10: PassPrice(10, 310.30),
        12: PassPrice(12, 360.30),
    },
))

add_pass(PassConfig(
    key="crossformer",
    label="Pass Crossformer",
    duration_min=50,
    where="lavandieres",
    category="machine",
    includes=["Pilates Crossformer (machine, + cardio / intense)"],
    prices={
        2: PassPrice(2, 78.30),
        4: PassPrice(4, 152.30),
        6: PassPrice(6, 222.30),
        8: PassPrice(8, 288.30),
        10: PassPrice(10, 350.30),
        12: PassPrice(12, 408.30),
    },
))

add_pass(PassConfig(
    key="full_former",
    label="Pass Full Former (Reformer + Crossformer)",
    duration_min=50,
    where="lavandieres",
    category="machine",
    includes=["Reformer", "Crossformer"],
    prices={
        2: PassPrice(2, 74.30),
        4: PassPrice(4, 144.30),
        6: PassPrice(6, 210.30),
        8: PassPrice(8, 272.30),
        10: PassPrice(10, 330.30),
        12: PassPrice(12, 384.30),
    },
))

# Training
add_pass(PassConfig(
    key="cross",
    label="Pass Cross",
    duration_min=55,
    where="docks",
    category="training",
    includes=["Cross Training", "Hyrox", "Core", "Body", "Cross Yoga"],
    prices={
        2: PassPrice(2, 30.30),
        4: PassPrice(4, 60.30),
        6: PassPrice(6, 90.30),
        8: PassPrice(8, 116.30),
        10: PassPrice(10, 145.30),
        12: PassPrice(12, 168.30),
    },
))

add_pass(PassConfig(
    key="focus",
    label="Pass Focus",
    duration_min=55,
    where="mixte",
    category="training",
    includes=["Yoga", "Pilates sol", "Boxe", "Danse", "Stretch (Core & Stretch)"],
    prices={
        2: PassPrice(2, 36.30),
        4: PassPrice(4, 72.30),
        6: PassPrice(6, 105.30),
        8: PassPrice(8, 136.30),
        10: PassPrice(10, 165.30),
        12: PassPrice(12, 192.30),
    },
))

add_pass(PassConfig(
    key="full",
    label="Pass Full (Cross + Focus)",
    duration_min=55,
    where="mixte",
    category="training",
    includes=["Tout le Pass Cross + tout le Pass Focus"],
    prices={
        2: PassPrice(2, 40.30),
        4: PassPrice(4, 80.30),
        6: PassPrice(6, 115.30),
        8: PassPrice(8, 150.30),
        10: PassPrice(10, 180.30),
        12: PassPrice(12, 210.30),
    },
))

# Kids (si tu l'utilises)
add_pass(PassConfig(
    key="kids",
    label="Pass Kids (hors juillet/août)",
    duration_min=55,
    where="docks",
    category="training",
    includes=["Training Kids", "Yoga Kids"],
    prices={
        2: PassPrice(2, 35.30),
        4: PassPrice(4, 65.30),
    },
))

KIDS = {"extra_session": 18.30, "note": "1 activité au choix"}

# Coaching (prix connus)
COACHING = {
    "good_vibes": {"label": "Coaching Pass Good Vibes", "duration_min": 55, "prices": {4: 300.30, 8: 560.30}},
    "duo": {"label": "Coaching Pass Duo", "duration_min": 55, "prices": {4: 400.60, 8: 720.60}, "per_person": {4: 200.30, 8: 360.30}},
}

# -----------------------------------------------------------------------------
# RÈGLES (FAQ) — formulation "safe" et actionnable
# -----------------------------------------------------------------------------

RULES = {
    "cancel_small_group": "Annulation : jusqu’à 1h avant le cours, sinon la séance est déduite.",
    "cancel_private": "Annulation coaching : jusqu’à 24h avant, sinon la séance est déduite.",
    "no_carry_over": "Les séances ne sont pas reportables au mois suivant.",
    "late_policy": "Au-delà de 5 minutes de retard : accès refusé et séance déduite.",
    "socks_lavandieres": "Reformer (Lavandières) : chaussettes antidérapantes obligatoires (en vente au studio).",
    "suspension": "Suspension : possible. En cas d’absence de plus de 10 jours, préavis d’un mois requis (sauf Boost).",
    "resiliation": "Résiliation : par e-mail, avec 1 mois de préavis (au-delà de la période d’engagement).",
    "engagement": f"Engagement abonnements : {FEES_AND_ENGAGEMENT['small_group_engagement_months']} mois (voir Tarifs). " + FEES_AND_ENGAGEMENT["small_group_engagement_note"],
}

PARRAINAGE = (
    "Offre de parrainage : parrainez un ami et recevez un cadeau 🎁 "
    "Pour chaque nouveau membre qui s’inscrit grâce à vous, vous recevez un cadeau exclusif."
)

# -----------------------------------------------------------------------------
# DÉFINITIONS (FAQ + wording simple)
# -----------------------------------------------------------------------------

DEFINITIONS: Dict[str, str] = {
    "reformer": (
        "Le **Reformer** = Pilates sur machine à ressorts. "
        "Très efficace pour gainer, se tonifier et améliorer la posture (débutant OK)."
    ),
    "crossformer": (
        "Le **Crossformer** = machine Pilates plus **cardio / intense**. "
        "Top si tu veux te tonifier + transpirer + booster le cardio."
    ),
    "cross training": "Le **Cross Training** = cardio + renfo (full body) avec des formats variés.",
    "cross core": "Le **Cross Core** cible surtout le gainage (abdos/dos) + stabilité.",
    "cross body": "Le **Cross Body** travaille tout le corps (renfo + cardio) avec focus tonus.",
    "cross rox": "Le **Cross Rox** = format plus intense/rythmé (cardio + renfo).",
    "cross yoga": "Le **Cross Yoga** mélange mobilité + gainage + flow.",
    "boxe": "La **Boxe** = cardio + technique + renfo (sans combat). Très efficace pour se défouler.",
    "afrodance": "L’**Afrodance'All** = danse cardio, fun, énergie, transpiration garantie.",
    "yoga vinyasa": "Le **Yoga Vinyasa** = enchaînements fluides, respiration, mobilité.",
    "hatha flow": "Le **Hatha Flow** = yoga plus doux/contrôlé, idéal pour bien commencer.",
    "classic pilates": "Le **Classic Pilates** = travail postural + gainage + mobilité (sans machine).",
    "power pilates": "Le **Power Pilates** = Pilates plus dynamique/intense.",
    "core & stretch": "Le **Core & Stretch** = gainage + étirements (parfait pour le dos et la mobilité).",
    "small group": "Small Group = petit groupe, coaching plus personnalisé, corrections et adaptations.",
    "coaching": "Coaching = séance personnalisée (individuel ou duo) selon ton objectif.",
    "yoga kids": "Le **Yoga Kids** = yoga adapté aux enfants (mobilité, coordination, fun).",
    "training kids": "Le **Training Kids** = sport adapté aux enfants (motricité, renfo, cardio).",
}

# -----------------------------------------------------------------------------
# PLANNING — STRUCTURÉ
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ClassSlot:
    studio: str   # docks / lavandieres
    day: str      # lundi...
    time: str     # "10h15"
    name: str     # label
    tag: str      # cross / focus / kids / reformer / crossformer

def normalize_time(h: str) -> str:
    # "08h" -> "8h", "10:15" -> "10h15"
    h = norm(h).replace(" ", "").replace(":", "h")
    h = re.sub(r"^0(\d)", r"\1", h)
    return h

def time_to_minutes(h: str) -> int:
    h = normalize_time(h)
    m = re.match(r"^(\d{1,2})h(\d{2})?$", h)
    if not m:
        return 0
    hh = int(m.group(1))
    mm = int(m.group(2) or "00")
    return hh * 60 + mm

SLOTS: List[ClassSlot] = []

def add_slot(studio: str, day: str, time: str, name: str, tag: str) -> None:
    SLOTS.append(ClassSlot(studio=studio, day=day, time=normalize_time(time), name=name, tag=tag))

# --- DOCKS ---
add_slot("docks", "lundi", "12h",   "Cross Training", "cross")
add_slot("docks", "lundi", "13h",   "Cross Core", "cross")
add_slot("docks", "lundi", "19h",   "Cross Training", "cross")
add_slot("docks", "lundi", "20h",   "Cross Body", "cross")

add_slot("docks", "mardi", "12h",   "Cross Rox", "cross")
add_slot("docks", "mardi", "19h",   "Cross Body", "cross")
add_slot("docks", "mardi", "20h",   "Cross Training", "cross")

add_slot("docks", "mercredi", "12h", "Cross Training", "cross")
add_slot("docks", "mercredi", "16h", "Yoga Kids", "kids")
add_slot("docks", "mercredi", "19h", "Cross Training", "cross")
add_slot("docks", "mercredi", "20h", "Boxe", "focus")

add_slot("docks", "jeudi", "8h",    "Cross Core", "cross")
add_slot("docks", "jeudi", "12h",   "Cross Body", "cross")
add_slot("docks", "jeudi", "13h",   "Boxe", "focus")
add_slot("docks", "jeudi", "18h",   "Cross Training", "cross")
add_slot("docks", "jeudi", "19h",   "Afrodance'All", "focus")

add_slot("docks", "vendredi", "18h", "Cross Rox", "cross")
add_slot("docks", "vendredi", "19h", "Cross Training", "cross")

add_slot("docks", "samedi", "9h30",  "Training Kids", "kids")
add_slot("docks", "samedi", "10h30", "Cross Body", "cross")
add_slot("docks", "samedi", "11h30", "Cross Training", "cross")

add_slot("docks", "dimanche", "10h30", "Cross Training", "cross")
add_slot("docks", "dimanche", "11h30", "Cross Yoga", "cross")

# --- LAVANDIÈRES ---
add_slot("lavandieres", "lundi", "12h",   "Cross-Former", "crossformer")
add_slot("lavandieres", "lundi", "12h15", "Reformer", "reformer")
add_slot("lavandieres", "lundi", "12h30", "Yoga Vinyasa", "focus")
add_slot("lavandieres", "lundi", "18h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "lundi", "19h",   "Yoga Vinyasa", "focus")
add_slot("lavandieres", "lundi", "19h15", "Reformer", "reformer")

add_slot("lavandieres", "mardi", "7h30",  "Hatha Flow", "focus")
add_slot("lavandieres", "mardi", "11h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "mardi", "12h",   "Power Pilates", "focus")
add_slot("lavandieres", "mardi", "13h15", "Reformer", "reformer")
add_slot("lavandieres", "mardi", "18h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "mardi", "19h15", "Reformer", "reformer")
add_slot("lavandieres", "mardi", "20h",   "Power Pilates", "focus")

add_slot("lavandieres", "mercredi", "10h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "mercredi", "12h",   "Reformer", "reformer")
add_slot("lavandieres", "mercredi", "12h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "mercredi", "19h",   "Reformer", "reformer")
add_slot("lavandieres", "mercredi", "19h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "mercredi", "20h",   "Reformer", "reformer")

add_slot("lavandieres", "jeudi", "7h",    "Classic Pilates", "focus")
add_slot("lavandieres", "jeudi", "12h",   "Yoga Vinyasa", "focus")
add_slot("lavandieres", "jeudi", "12h15", "Cross-Former", "crossformer")
add_slot("lavandieres", "jeudi", "12h30", "Reformer", "reformer")
add_slot("lavandieres", "jeudi", "18h",   "Cross-Former", "crossformer")
add_slot("lavandieres", "jeudi", "18h45", "Reformer", "reformer")
add_slot("lavandieres", "jeudi", "19h15", "Power Pilates", "focus")
add_slot("lavandieres", "jeudi", "20h15", "Cross Yoga", "cross")
add_slot("lavandieres", "jeudi", "20h30", "Cross-Former", "crossformer")

add_slot("lavandieres", "vendredi", "9h45",  "Cross-Former", "crossformer")
add_slot("lavandieres", "vendredi", "10h45", "Cross-Former", "crossformer")
add_slot("lavandieres", "vendredi", "12h",   "Reformer", "reformer")
add_slot("lavandieres", "vendredi", "13h",   "Reformer", "reformer")
add_slot("lavandieres", "vendredi", "18h",   "Classic Pilates", "focus")
add_slot("lavandieres", "vendredi", "18h30", "Reformer", "reformer")
add_slot("lavandieres", "vendredi", "19h15", "Cross-Former", "crossformer")

# Samedi (site)
add_slot("lavandieres", "samedi", "9h",    "Reformer", "reformer")
add_slot("lavandieres", "samedi", "9h30",  "Cross-Former", "crossformer")
add_slot("lavandieres", "samedi", "10h",   "Reformer", "reformer")
add_slot("lavandieres", "samedi", "10h15", "Classic Pilates", "focus")
add_slot("lavandieres", "samedi", "10h30", "Cross-Former", "crossformer")
add_slot("lavandieres", "samedi", "11h15", "Core & Stretch", "focus")

add_slot("lavandieres", "dimanche", "10h",   "Cross-Former", "crossformer")
add_slot("lavandieres", "dimanche", "10h15", "Reformer", "reformer")
add_slot("lavandieres", "dimanche", "11h",   "Cross-Former", "crossformer")
add_slot("lavandieres", "dimanche", "11h15", "Reformer", "reformer")
add_slot("lavandieres", "dimanche", "11h30", "Yoga Vinyasa", "focus")

# -----------------------------------------------------------------------------
# EXTRACTION (cours / pass / studio / jour / sessions)
# -----------------------------------------------------------------------------

PASS_ALIASES = [
    ("full former", "full_former"),
    ("fullformer", "full_former"),
    ("pass full", "full"),
    ("full", "full"),
    ("pass focus", "focus"),
    ("focus", "focus"),
    ("pass cross", "cross"),
    ("cross", "cross"),
    ("pass reformer", "reformer"),
    ("reformer", "reformer"),
    ("pass crossformer", "crossformer"),
    ("crossformer", "crossformer"),
    ("kids", "kids"),
    ("enfant", "kids"),
]

COURSE_ALIASES = {
    "pilates reformer": "reformer",
    "pilate reformer": "reformer",
    "reformer": "reformer",

    "pilates crossformer": "crossformer",
    "pilate crossformer": "crossformer",
    "crossformer": "crossformer",
    "cross-former": "crossformer",
    "cross former": "crossformer",

    "boxe": "boxe",
    "boxing": "boxe",

    "afrodance": "afrodance",
    "afrodance all": "afrodance",
    "afrodance'all": "afrodance",

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
    "hatha flow": "hatha flow",
    "hatha": "hatha flow",
    "classic pilates": "classic pilates",
    "power pilates": "power pilates",
    "core & stretch": "core & stretch",
    "core and stretch": "core & stretch",
    "stretch": "core & stretch",

    "yoga kids": "yoga kids",
    "training kids": "training kids",
}

def find_sessions_count(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm2(text))
    return int(m.group(1)) if m else None

def find_pass_key(text: str) -> Optional[str]:
    t = norm2(text)
    for needle, key in sorted(PASS_ALIASES, key=lambda x: len(x[0]), reverse=True):
        if needle in t:
            return key
    return None

def extract_course_key(text: str) -> Optional[str]:
    t = norm2(text)
    for k in sorted(COURSE_ALIASES.keys(), key=len, reverse=True):
        if k in t:
            return COURSE_ALIASES[k]
    return None

def extract_day(text: str) -> Optional[str]:
    t = norm2(text)
    for d in DAY_ORDER:
        if d in t:
            return d
    return None

def extract_studio(text: str) -> Optional[str]:
    t = norm2(text)
    if "dock" in t or "parc des docks" in t:
        return "docks"
    if "lavandi" in t or "cours lavandieres" in t:
        return "lavandieres"
    return None

def pass_unit_price(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    return round(total / sessions, 2)

# -----------------------------------------------------------------------------
# PLANNING HELPERS
# -----------------------------------------------------------------------------

def slots_for(studio: Optional[str] = None, day: Optional[str] = None, course_key: Optional[str] = None) -> List[ClassSlot]:
    out: List[ClassSlot] = []
    for s in SLOTS:
        if studio and s.studio != studio:
            continue
        if day and s.day != day:
            continue
        if course_key:
            ck = norm2(course_key)
            nm = norm2(s.name)

            if ck == "reformer" and "reformer" not in nm:
                continue
            if ck == "crossformer" and ("cross" not in nm or "former" not in nm):
                continue
            if ck == "boxe" and "boxe" not in nm:
                continue
            if ck == "afrodance" and "afrodance" not in nm:
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

def tag_to_pass_hint(tag: str) -> str:
    if tag == "cross":
        return "Pass Cross (ou Pass Full)"
    if tag == "focus":
        return "Pass Focus (ou Pass Full)"
    if tag == "reformer":
        return "Pass Reformer (ou Pass Full Former)"
    if tag == "crossformer":
        return "Pass Crossformer (ou Pass Full Former)"
    if tag == "kids":
        return "Pass Kids"
    return "selon la formule"

def format_slots_grouped(slots: List[ClassSlot]) -> str:
    by_day: Dict[str, List[ClassSlot]] = {d: [] for d in DAY_ORDER}
    for s in slots:
        by_day[s.day].append(s)

    lines: List[str] = []
    for d in DAY_ORDER:
        items = by_day[d]
        if not items:
            continue
        items_sorted = sorted(items, key=lambda z: time_to_minutes(z.time))
        times = ", ".join([f"{x.time} ({x.name})" for x in items_sorted])
        lines.append(f"- **{d.capitalize()}** : {times}")
    return "\n".join(lines) if lines else "Je n’ai rien trouvé sur le planning actuel."