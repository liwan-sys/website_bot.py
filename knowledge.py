# knowledge.py
# =============================================================================
# SVB — KNOWLEDGE BASE (SOURCE DE VÉRITÉ)
# Tarifs / Planning / Règles / Définitions
# =============================================================================

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re
import unicodedata

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def norm(s: str) -> str:
    """
    Normalise agressivement :
    - minuscules
    - accents supprimés
    - apostrophes typographiques ’ remplacées
    - espaces nettoyés
    """
    s = (s or "").strip().lower()
    s = _strip_accents(s)

    # apostrophes typographiques -> apostrophe simple
    s = s.replace("’", "'").replace("‘", "'").replace("´", "'").replace("`", "'")

    # tirets typographiques -> tiret simple
    s = s.replace("–", "-").replace("—", "-")

    # espaces
    s = re.sub(r"\s+", " ", s)
    return s

def eur(x: float) -> str:
    return f"{x:,.2f}€".replace(",", " ").replace(".", ",")

# -----------------------------------------------------------------------------
# Contact / identité
# -----------------------------------------------------------------------------
CONTACT = {
    "phone": "07 44 91 91 55",
    "whatsapp_url": "https://wa.me/33744919155",
    "email": "hello@studiosvb.fr",
    "instagram": "@svb.officiel",
    "website": "https://www.studiosvb.com",
}

STUDIOS = {
    "docks": {
        "name": "Parc des Docks",
        "address": "6 Mail André Breton, 93400 Saint-Ouen",
        "vibe": "Small group training (Cross / Boxe / Danse / Kids) + Coaching",
    },
    "lavandieres": {
        "name": "Cours Lavandières",
        "address": "40 Cours des Lavandières, 93400 Saint-Ouen",
        "vibe": "Machines (Reformer / Crossformer) + Yoga / Pilates / Stretch",
    },
}

# -----------------------------------------------------------------------------
# Définitions
# -----------------------------------------------------------------------------
DEFINITIONS = {
    "reformer": (
        "Le **Pilates Reformer**, c’est du Pilates sur machine avec un chariot et des ressorts. "
        "Ça renforce en profondeur, améliore la posture, et c’est top pour le dos."
    ),
    "crossformer": (
        "Le **Pilates Crossformer**, c’est une machine plus **intense** : mix Pilates + cardio. "
        "On transpire, on sculpte, et ça reste **sans impact**."
    ),
    "cross training": (
        "Le **Cross Training**, c’est un entraînement fonctionnel au sol : renforcement, cardio, circuits. "
        "Travail complet (tonus, endurance, performance)."
    ),
    "boxe": (
        "La **Boxe**, c’est un cours fitness basé sur des enchaînements (technique + cardio + renfo). "
        "Accessible même si tu débutes."
    ),
    "yoga vinyasa": "Le **Yoga Vinyasa**, c’est un yoga dynamique (enchaîné) : mobilité, souffle, renforcement.",
    "hatha flow": "Le **Hatha Flow**, c’est un yoga plus accessible, alignement + respiration + mobilité.",
    "power pilates": "Le **Power Pilates**, c’est un pilates plus dynamique : renfo + gainage + intensité.",
    "classic pilates": "Le **Classic Pilates**, c’est le pilates traditionnel au sol : posture, gainage, contrôle.",
    "core & stretch": "Le **Core & Stretch**, c’est gainage + mobilité/étirements pour récupérer et se renforcer.",
    "cross yoga": "Le **Cross Yoga**, c’est un mix mobilité + renfo + flow (plus tonique qu’un yoga doux).",
    "hyrox": "Le **Hyrox**, c’est un format training orienté performance (cardio + renforcement).",
    "afrodance'all": "L’**Afrodance’All**, c’est un cours danse énergique : cardio, fun et accessible.",
    "groove & tone": "Le **Groove & Tone**, c’est danse + renforcement (tonus, cardio, coordination).",
    "kids": "Les cours **Kids**, ce sont des séances adaptées enfants : énergie, coordination, fun, sécurité.",
}

# -----------------------------------------------------------------------------
# Tarifs à l’unité (validés)
# -----------------------------------------------------------------------------
UNIT_PRICE = {
    "training": 30.0,
    "machine": 50.0,
}

# -----------------------------------------------------------------------------
# Essai / Starter / Boost
# -----------------------------------------------------------------------------
TRIAL = {"price": 30.0, "refund_if_signup": 15.0}

STARTER = {
    "name": "New Pass Starter",
    "price": 99.90,
    "sessions": 5,
    "validity": "1 mois",
    "rule": "5 sessions différentes au choix (pas 5 fois la même discipline).",
}

BOOST = {
    "price_per_month": 9.90,
    "benefits": [
        "Frais d’inscription offerts",
        "1 essai gratuit / mois pour un proche (selon dispo)",
        "Suspension abonnement sans préavis",
    ],
}

# -----------------------------------------------------------------------------
# Règlement
# -----------------------------------------------------------------------------
RULES = {
    "booking": "Tu peux réserver tes sessions **avec 1 mois d’avance**.",
    "credits": "Les sessions du mois en cours **ne peuvent pas être reportées** sur le mois suivant.",
    "cancel_small_group": "Annulation small group **jusqu’à 1h avant** sans perdre de crédit.",
    "cancel_private": "Annulation coaching privé **jusqu’à 24h avant** sans perdre de crédit.",
    "late_policy": "**+ de 5 minutes de retard = cours refusé** (sécurité).",
    "socks": (
        "À Lavandières : chaussettes antidérapantes **obligatoires**. "
        "Achat 10€ ou prêt 3€ (10€ facturés si pas rendu)."
    ),
    "resiliation": (
        "Résiliation par mail : **préavis d’1 mois** dès la fin d’engagement. "
        "Pas de préavis pour un abonnement supérieur. 1 mois pour un abonnement inférieur."
    ),
}

# -----------------------------------------------------------------------------
# Pass & coaching — prix mensuels
# -----------------------------------------------------------------------------
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
    duration_min: int
    includes: str
    prices: Dict[int, PassPrice]

PASS: Dict[str, PassConfig] = {}

def add_pass(cfg: PassConfig) -> None:
    PASS[cfg.key] = cfg

# Machines
add_pass(PassConfig(
    key="reformer", label="Pass Reformer", category="machine",
    studio_hint="Cours Lavandières", duration_min=50, includes="Pilates Reformer",
    prices={2: PassPrice(2, 70.30), 4: PassPrice(4, 136.30), 6: PassPrice(6, 198.30),
            8: PassPrice(8, 256.30), 10: PassPrice(10, 310.30), 12: PassPrice(12, 360.30)}
))
add_pass(PassConfig(
    key="crossformer", label="Pass Crossformer", category="machine",
    studio_hint="Cours Lavandières", duration_min=50, includes="Pilates Crossformer",
    prices={2: PassPrice(2, 78.30), 4: PassPrice(4, 152.30), 6: PassPrice(6, 222.30),
            8: PassPrice(8, 288.30), 10: PassPrice(10, 350.30), 12: PassPrice(12, 408.30)}
))
add_pass(PassConfig(
    key="full_former", label="Pass Full Former", category="machine",
    studio_hint="Cours Lavandières", duration_min=50, includes="Reformer + Crossformer",
    prices={2: PassPrice(2, 74.30), 4: PassPrice(4, 144.30), 6: PassPrice(6, 210.30),
            8: PassPrice(8, 272.30), 10: PassPrice(10, 330.30), 12: PassPrice(12, 384.30)}
))

# Training
add_pass(PassConfig(
    key="cross", label="Pass Cross", category="training",
    studio_hint="Parc des Docks", duration_min=55,
    includes="Cross Training • Core • Body • Rox • Yoga",
    prices={2: PassPrice(2, 30.30), 4: PassPrice(4, 60.30), 6: PassPrice(6, 90.30),
            8: PassPrice(8, 116.30), 10: PassPrice(10, 145.30), 12: PassPrice(12, 168.30)}
))
add_pass(PassConfig(
    key="focus", label="Pass Focus", category="training",
    studio_hint="Mixte", duration_min=55,
    includes="Boxe • Danse • Yoga • Pilates Mat",
    prices={2: PassPrice(2, 36.30), 4: PassPrice(4, 72.30), 6: PassPrice(6, 105.30),
            8: PassPrice(8, 136.30), 10: PassPrice(10, 165.30), 12: PassPrice(12, 192.30)}
))
add_pass(PassConfig(
    key="full", label="Pass Full (Cross + Focus)", category="training",
    studio_hint="Mixte", duration_min=55,
    includes="Cours Cross + Focus",
    prices={2: PassPrice(2, 40.30), 4: PassPrice(4, 80.30), 6: PassPrice(6, 115.30),
            8: PassPrice(8, 150.30), 10: PassPrice(10, 180.30), 12: PassPrice(12, 210.30)}
))

# Kids
add_pass(PassConfig(
    key="kids", label="Pass Kids", category="kids",
    studio_hint="Parc des Docks", duration_min=55,
    includes="Kids (hors juillet/août)",
    prices={2: PassPrice(2, 35.30), 4: PassPrice(4, 65.30)}
))
KIDS_EXTRA_SESSION = 18.30
KIDS_FILE_FEE = 29.0
KIDS_COMMITMENT = "4 mois"

# Coaching (privé)
add_pass(PassConfig(
    key="coaching_good_vibes", label="Coaching Pass Good Vibes", category="coaching",
    studio_hint="Selon dispo", duration_min=55, includes="Coaching individuel",
    prices={4: PassPrice(4, 300.30), 8: PassPrice(8, 560.30)}
))
add_pass(PassConfig(
    key="coaching_duo", label="Coaching Pass Duo", category="coaching",
    studio_hint="Selon dispo", duration_min=55, includes="Coaching duo",
    prices={4: PassPrice(4, 400.60), 8: PassPrice(8, 720.60)}
))

# -----------------------------------------------------------------------------
# Planning (exemple issu des brochures)
# -----------------------------------------------------------------------------
PLANNING: Dict[str, Dict[str, List[Tuple[str, str]]]] = {
    "docks": {
        "lundi": [("12:00", "Cross Training"), ("13:00", "Cross Core"), ("19:00", "Cross Training"), ("20:00", "Cross Body")],
        "mardi": [("12:00", "Cross Rox"), ("19:00", "Cross Body"), ("20:00", "Cross Training")],
        "mercredi": [("12:00", "Cross Training"), ("16:00", "Yoga Kids"), ("19:00", "Cross Training"), ("20:00", "Boxe")],
        "jeudi": [("08:00", "Cross Core"), ("12:00", "Cross Body"), ("13:00", "Boxe"), ("18:00", "Cross Training"), ("19:00", "Afrodance'All")],
        "vendredi": [("18:00", "Cross Rox"), ("19:00", "Cross Training")],
        "samedi": [("09:30", "Training Kids"), ("10:30", "Cross Body"), ("11:30", "Cross Training")],
        "dimanche": [("10:30", "Cross Training"), ("11:30", "Cross Yoga")],
    },
    "lavandieres": {
        "lundi": [("12:00", "Cross-Former"), ("12:15", "Reformer"), ("12:30", "Yoga Vinyasa"), ("18:45", "Cross-Former"), ("19:00", "Yoga Vinyasa"), ("19:15", "Reformer")],
        "mardi": [("07:30", "Hatha Flow"), ("11:45", "Cross-Former"), ("12:00", "Power Pilates"), ("13:15", "Reformer"), ("18:45", "Cross-Former"), ("19:15", "Reformer"), ("20:00", "Power Pilates")],
        "mercredi": [("10:15", "Cross-Former"), ("12:00", "Reformer"), ("12:15", "Cross-Former"), ("19:00", "Reformer"), ("19:15", "Cross-Former"), ("20:00", "Reformer")],
        "jeudi": [("07:00", "Classic Pilates"), ("12:00", "Yoga Vinyasa"), ("12:15", "Cross-Former"), ("12:30", "Reformer"), ("18:00", "Cross-Former"), ("18:45", "Reformer"), ("19:15", "Power Pilates"), ("20:15", "Cross Yoga"), ("20:30", "Cross-Former")],
        "vendredi": [("09:45", "Cross-Former"), ("10:45", "Cross-Former"), ("12:00", "Reformer"), ("13:00", "Reformer"), ("18:00", "Classic Pilates"), ("18:30", "Reformer"), ("19:15", "Cross-Former")],
        "samedi": [("08:45", "Reformer"), ("09:00", "Cross-Former"), ("09:45", "Reformer"), ("10:15", "Classic Pilates"), ("11:15", "Core & Stretch"), ("11:30", "Cross-Former")],
        "dimanche": [("10:00", "Cross-Former"), ("10:15", "Reformer"), ("11:00", "Cross-Former"), ("11:15", "Reformer"), ("11:30", "Yoga Vinyasa")],
    },
}

def list_days() -> List[str]:
    return ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

def get_pass(pass_key: str) -> Optional[PassConfig]:
    return PASS.get(pass_key)

def get_pass_price(pass_key: str, sessions: int) -> Optional[float]:
    cfg = PASS.get(pass_key)
    if not cfg:
        return None
    pp = cfg.prices.get(sessions)
    return pp.price if pp else None

def price_per_session(pass_key: str, sessions: int) -> Optional[float]:
    total = get_pass_price(pass_key, sessions)
    if total is None:
        return None
    return round(total / sessions, 2)

def extra_session_price_for_member(pass_key: str, sessions: int) -> Optional[float]:
    cfg = PASS.get(pass_key)
    if not cfg:
        return None
    if cfg.category == "kids":
        return KIDS_EXTRA_SESSION
    return price_per_session(pass_key, sessions)

def find_schedule(discipline_query: str, studio_key: Optional[str] = None) -> Dict[str, List[Tuple[str, str]]]:
    q = norm(discipline_query)
    studios_to_scan = [studio_key] if studio_key in PLANNING else list(PLANNING.keys())
    out: Dict[str, List[Tuple[str, str]]] = {}

    for sk in studios_to_scan:
        for day in list_days():
            events = PLANNING.get(sk, {}).get(day, [])
            for (t, label) in events:
                if q in norm(label):
                    out.setdefault(day, []).append((t, f"{label} ({STUDIOS[sk]['name']})"))
    return out

def format_schedule(found: Dict[str, List[Tuple[str, str]]]) -> str:
    if not found:
        return ""
    lines = []
    for day in list_days():
        if day in found:
            ev = sorted(found[day], key=lambda x: x[0])
            times = ", ".join([f"**{t}** {lbl}" for (t, lbl) in ev])
            lines.append(f"- **{day.capitalize()}** : {times}")
    return "\n".join(lines)
