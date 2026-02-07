# receptionniste.py
from __future__ import annotations

import os
import re
import random
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

import streamlit as st

from knowledge import (
    CONTACT,
    STUDIOS,
    UNIT_PRICE,
    TRIAL,
    STARTER,
    BOOST,
    FEES_AND_ENGAGEMENT,
    COACHING,
    PASS,
    KIDS,
    RULES,
    PARRAINAGE,
    DAY_ORDER,
    SLOTS,
    DEFINITIONS,
    PASS_INCLUDES,
)

# ------------------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ------------------------------------------------------------------------------
# GEMINI (optionnel)
# ------------------------------------------------------------------------------
try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# ------------------------------------------------------------------------------
# CSS
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
small { color:#555; }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------------------
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

# ==============================================================================
# HELPERS — NORMALISATION / FORMAT
# ==============================================================================

def eur(x: float) -> str:
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}€"

def norm(s: str) -> str:
    return (s or "").strip().lower()

def strip_accents_cheap(s: str) -> str:
    repl = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a",
        "î": "i", "ï": "i",
        "ô": "o",
        "ù": "u", "û": "u",
        "ç": "c",
        "’": "'", "“": '"', "”": '"',
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s

def norm2(s: str) -> str:
    return strip_accents_cheap(norm(s))

def safe_finalize(text: str) -> str:
    """Évite les fins 'coupées' côté LLM ou texte sans ponctuation."""
    t = (text or "").strip()
    if not t:
        return t
    if re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]$", t) and not re.search(r"[\.!\?…]$", t):
        return t + " 🙂"
    return t

def has_any(text: str, words: List[str]) -> bool:
    t = norm2(text)
    return any(w in t for w in words)

# ==============================================================================
# EXTRACTION — STUDIO / JOUR / COURS / SESSIONS / OBJECTIFS
# ==============================================================================

def extract_studio(text: str) -> Optional[str]:
    t = norm2(text)
    if "dock" in t or "parc des docks" in t:
        return "docks"
    if "lavandi" in t or "cours lavandieres" in t:
        return "lavandieres"
    return None

def extract_day(text: str) -> Optional[str]:
    t = norm2(text)
    for d in DAY_ORDER:
        if d in t:
            return d
    return None

def find_sessions_count(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm2(text))
    return int(m.group(1)) if m else None

def find_pass_key(text: str) -> Optional[str]:
    t = norm2(text)
    patterns = [
        ("full former", "full_former"),
        ("fullformer", "full_former"),
        ("crossformer", "crossformer"),
        ("pass crossformer", "crossformer"),
        ("reformer", "reformer"),
        ("pass reformer", "reformer"),
        ("pass full", "full"),
        ("pass focus", "focus"),
        ("pass cross", "cross"),
        ("kids", "kids"),
        ("enfant", "kids"),
        ("full", "full"),
        ("focus", "focus"),
        ("cross", "cross"),
    ]
    for needle, key in patterns:
        if needle in t:
            return key
    return None

def extract_course_key(text: str) -> Optional[str]:
    """Retourne une clé canonique de cours."""
    t = norm2(text)

    aliases = {
        # machines
        "crossformer": "crossformer",
        "cross-former": "crossformer",
        "cross former": "crossformer",
        "reformer": "reformer",
        "pilate reformer": "reformer",
        "pilates reformer": "reformer",
        "pilate crossformer": "crossformer",
        "pilates crossformer": "crossformer",

        # docks
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

        "boxe": "boxe",
        "boxing": "boxe",

        "afrodance": "afrodance",
        "afrodance'all": "afrodance",
        "afrodance all": "afrodance",

        # yoga/pilates sol
        "yoga vinyasa": "yoga vinyasa",
        "vinyasa": "yoga vinyasa",
        "hatha flow": "hatha flow",
        "hatha": "hatha flow",
        "classic pilates": "classic pilates",
        "pilates classic": "classic pilates",
        "power pilates": "power pilates",
        "core & stretch": "core & stretch",
        "core and stretch": "core & stretch",
        "core stretch": "core & stretch",
        "stretch": "core & stretch",

        # kids
        "yoga kids": "yoga kids",
        "training kids": "training kids",
    }

    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t:
            return aliases[k]
    return None

GOAL_KEYWORDS = {
    "dos": ["dos", "lombaire", "sciatique", "posture"],
    "tonus": ["tonifier", "tonus", "raffermir", "fessier", "ventre"],
    "cardio": ["cardio", "transpirer", "perdre du poids", "maigrir", "souffle"],
    "mobilite": ["souplesse", "mobilite", "mobilité", "flexibilite", "flexibilité", "etire", "étire"],
    "stress": ["stress", "detente", "détente", "relax", "relaxation"],
    "debutant": ["debutant", "débutant", "jamais", "premiere fois", "première fois"],
}

def extract_goals(text: str) -> Set[str]:
    t = norm2(text)
    found: Set[str] = set()
    for k, arr in GOAL_KEYWORDS.items():
        if any(norm2(w) in t for w in arr):
            found.add(k)
    return found

# ==============================================================================
# MÉMO CONVERSATION — petit "cerveau" deterministic
# ==============================================================================

def ensure_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "did_greet" not in st.session_state:
        st.session_state.did_greet = False
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "studio": None,
            "course": None,
            "goals": set(),
            "sessions": None,
            "pass_key": None,
        }

def update_profile_from_text(text: str) -> None:
    p = st.session_state.profile
    s = extract_studio(text)
    if s:
        p["studio"] = s
    ck = extract_course_key(text)
    if ck:
        p["course"] = ck
    goals = extract_goals(text)
    if goals:
        p["goals"] = set(p["goals"]) | goals
    n = find_sessions_count(text)
    if n:
        p["sessions"] = n
    pk = find_pass_key(text)
    if pk:
        p["pass_key"] = pk

def first_message() -> str:
    variants = [
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif (tonus, cardio, dos, mobilité…) et je te guide.",
        "OK 🙂 Tu veux plutôt venir aux Docks ou aux Lavandières ?",
    ]
    return random.choice(variants)

ensure_state()
if not st.session_state.did_greet and len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": first_message()})
    st.session_state.did_greet = True

# ==============================================================================
# INTENTS (plus précis pour éviter les réponses à côté)
# ==============================================================================

def intent_human(text: str) -> bool:
    return has_any(text, ["humain", "conseiller", "equipe", "équipe", "whatsapp", "joindre", "appeler", "telephone", "téléphone"])

def intent_signup(text: str) -> bool:
    # IMPORTANT: PAS "abonnement" tout seul
    return has_any(text, ["m'inscrire", "inscrire", "inscription", "creer un compte", "créer un compte", "identifiant", "mot de passe", "connexion", "connecter", "appli", "application", "sportigo"])

def intent_pause_subscription(text: str) -> bool:
    return has_any(text, ["pause", "mettre en pause", "suspendre", "suspension", "arreter provisoirement", "stopper provisoirement"])

def intent_rules(text: str) -> bool:
    return has_any(text, ["annulation", "annuler", "report", "reporter", "cumul", "resiliation", "résiliation", "preavis", "préavis", "retard", "chaussette", "chaussettes", "reglement", "règlement", "interieur", "intérieur", "absence"])

def intent_trial(text: str) -> bool:
    return has_any(text, ["essai", "seance d'essai", "séance d'essai", "tester", "decouverte", "découverte"])

def intent_starter(text: str) -> bool:
    return has_any(text, ["starter", "new pass starter"])

def intent_boost(text: str) -> bool:
    return has_any(text, ["boost", "option boost"])

def intent_parrainage(text: str) -> bool:
    return has_any(text, ["parrainage", "parrainer", "parrain"])

def intent_definition(text: str) -> bool:
    return has_any(text, ["c'est quoi", "c quoi", "ça veut dire", "explique", "definition", "définition", "difference", "différence"])

def intent_planning(text: str) -> bool:
    return has_any(text, ["planning", "horaire", "horaires", "quel jour", "quels jours", "a quelle heure", "à quelle heure", "quand"])

def intent_pass_info(text: str) -> bool:
    return has_any(text, ["c'est quoi le pass", "c est quoi le pass", "donne acces", "donne accès", "ça donne accès", "inclut", "comprend", "pass focus", "pass cross", "pass full", "pass reformer", "pass crossformer", "full former"])

def intent_pass_price(text: str) -> bool:
    return has_any(text, ["tarif", "prix", "combien", "coute", "coûte", "abonnement", "forfait", "mensuel", "mois"])

def intent_unit_price(text: str) -> bool:
    return has_any(text, ["a l'unite", "à l'unité", "sans abonnement", "sans abo", "unité", "unite"])

def intent_interest(text: str) -> bool:
    return has_any(text, ["je veux", "j'aimerais", "je voudrais", "je cherche", "je souhaite", "je suis interesse", "je suis intéressé"])

# ==============================================================================
# RÉPONSES DÉTERMINISTES
# ==============================================================================

def wa_button() -> None:
    st.markdown("---")
    st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

def answer_signup() -> str:
    return safe_finalize(
        "Pour t’inscrire :\n\n"
        "1) Tu souscris ton abonnement en ligne.\n"
        "2) Après le paiement, tu reçois automatiquement un e-mail avec tes identifiants.\n"
        "3) Tu télécharges l’application (SVB / Sportigo).\n"
        "4) Tu rentres les identifiants reçus par e-mail dans l’application.\n"
        "5) Ensuite tu réserves tes séances sur le planning ✅\n\n"
        "Si tu ne reçois pas l’e-mail (spam / délai), écris-nous sur WhatsApp."
    )

def answer_pause() -> str:
    return safe_finalize(
        "Oui c’est possible 🙂\n\n"
        f"📌 {RULES['suspension_absence']}\n\n"
        "Si tu me dis ton pass (Cross/Focus/Full/Reformer/Crossformer) je te dis la marche à suivre la plus simple."
    )

def answer_trial() -> str:
    return safe_finalize(
        f"La séance d’essai est à **{eur(TRIAL['price'])}**.\n"
        f"👉 **{eur(TRIAL['refund_if_signup'])} remboursés si inscription** ✅"
    )

def answer_starter() -> str:
    return safe_finalize(
        f"⭐ **New Pass Starter** : **{eur(STARTER['price'])}** — **{STARTER['sessions']} sessions** — valable **{STARTER['duration']}**.\n"
        "✅ Pas d’engagement / pas de reconduction.\n"
        f"📌 Règle : **{STARTER['rule']}**"
    )

def answer_boost() -> str:
    bullets = "\n".join([f"- {x}" for x in BOOST["includes"]])
    return safe_finalize(
        f"⚡ **Option SVB Boost** : **{eur(BOOST['price'])}/mois** (en + d’un pass)\n"
        f"{bullets}\n\n"
        f"📌 {BOOST['engagement_note']}"
    )

def answer_parrainage() -> str:
    return safe_finalize(PARRAINAGE)

def pass_unit_price(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    return round(total / sessions, 2)

def answer_pass_price(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    unit = pass_unit_price(pass_key, sessions)
    extra = ""
    if pass_key == "kids":
        extra = f"\n- Séance supplémentaire kids : **{eur(KIDS['extra_session'])}**"
    studio_txt = STUDIOS[p.where]["label"] if p.where in STUDIOS else p.where
    return safe_finalize(
        f"📌 **{p.label}** — {sessions} sessions / mois\n"
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance (calcul) : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
        f"- Studio : {studio_txt}\n"
        f"{extra}"
    )

def course_to_pass_options(course_name: str) -> List[str]:
    options = []
    for pk, courses in PASS_INCLUDES.items():
        if course_name in courses:
            mapping = {
                "cross": "Pass Cross",
                "focus": "Pass Focus",
                "full": "Pass Full",
                "reformer": "Pass Reformer",
                "crossformer": "Pass Crossformer",
                "full_former": "Pass Full Former",
                "kids": "Pass Kids",
            }
            options.append(mapping.get(pk, pk))
    order = {"Pass Reformer": 1, "Pass Crossformer": 2, "Pass Full Former": 3, "Pass Cross": 4, "Pass Focus": 5, "Pass Full": 6, "Pass Kids": 7}
    return sorted(set(options), key=lambda x: order.get(x, 99))

def answer_pass_info(text: str) -> str:
    pk = find_pass_key(text)
    t = norm2(text)

    if ("premium" in t or "plus premium" in t or "je veux tout" in t or "mixer" in t) and pk in (None, "focus", "cross"):
        pk = "full"

    if pk is None:
        return safe_finalize(
            "Tu parles de quel pass ?\n"
            "- Pass Cross\n- Pass Focus\n- Pass Full\n- Pass Reformer\n- Pass Crossformer\n- Pass Full Former\n\n"
            "Dis-moi juste le nom et je te détaille ce que ça inclut 🙂"
        )

    pretty = {
        "cross": "Pass Cross",
        "focus": "Pass Focus",
        "full": "Pass Full",
        "reformer": "Pass Reformer",
        "crossformer": "Pass Crossformer",
        "full_former": "Pass Full Former",
        "kids": "Pass Kids",
    }.get(pk, pk)

    if pk in PASS_INCLUDES:
        items = sorted(PASS_INCLUDES[pk])
        bullets = "\n".join([f"- {x}" for x in items])
        note = ""
        if pk == "focus":
            note = "\n\n📌 À noter : **Cross Training / Cross Core / Cross Body / Cross Rox / Cross Yoga** = c’est **Pass Cross** (ou **Pass Full**)."
        if pk == "cross":
            note = "\n\n📌 Pour Boxe/Yoga/Pilates sol/Core & Stretch = **Pass Focus** (ou **Pass Full**)."
        if pk == "full":
            note = "\n\n✅ Le plus “premium” si tu veux mixer Cross + Focus."
        if pk == "full_former":
            note = "\n\n✅ Si tu veux **Reformer + Cross-Former** (machines)."
        return safe_finalize(f"**{pretty}** donne accès à 👇\n{bullets}{note}")

    return safe_finalize("Je n’ai pas reconnu la formule exacte. Dis-moi : Cross / Focus / Full / Reformer / Crossformer / Full Former.")

def answer_unit_price(text: str) -> str:
    ck = extract_course_key(text)
    if ck in ("reformer", "crossformer"):
        return safe_finalize(f"Sans abonnement, une séance **Machine** est à **{eur(UNIT_PRICE['machine'])}**.")
    if ck is not None:
        return safe_finalize(f"Sans abonnement, une séance **Training / cours** est à **{eur(UNIT_PRICE['training'])}**.")
    return safe_finalize(
        "Sans abonnement :\n"
        f"- Cours **Training** : **{eur(UNIT_PRICE['training'])}**\n"
        f"- Séance **Machine** : **{eur(UNIT_PRICE['machine'])}**\n\n"
        "Tu cherches plutôt un cours Training (Boxe/Cross/Yoga/Pilates sol…) ou une Machine (Reformer/Crossformer) ?"
    )

def answer_rules(text: str) -> str:
    t = norm2(text)
    if any(k in t for k in ["annuler", "annulation"]):
        return safe_finalize(f"{RULES['cancel_small_group']}\n\n{RULES['cancel_private']}")
    if any(k in t for k in ["report", "reporter", "cumul", "cumulable"]):
        return safe_finalize(RULES["no_carry_over"])
    if any(k in t for k in ["resiliation", "résiliation", "preavis", "préavis", "modifier", "modification"]):
        return safe_finalize(RULES["resiliation"])
    if any(k in t for k in ["suspension", "absence", "absent", "pause"]):
        return safe_finalize(RULES["suspension_absence"])
    if "retard" in t:
        return safe_finalize(RULES["late_policy"])
    if "chaussette" in t:
        return safe_finalize(f"{RULES['socks_lavandieres']}\n{RULES['late_policy']}")
    return safe_finalize(
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
    t = norm2(text)
    ck = extract_course_key(text)

    if ("difference" in t or "différence" in t) and ("reformer" in t) and ("crossformer" in t or "cross-former" in t or "cross former" in t):
        return safe_finalize(
            "Différence **Reformer vs Crossformer** :\n"
            "- **Reformer** : Pilates machine plus contrôlé, super pour posture/gainage/tonus.\n"
            "- **Crossformer** : machine plus **cardio / intense**, ça monte plus vite en rythme.\n"
            "Les deux sont adaptés débutants : le coach ajuste."
        )

    if ck == "crossformer":
        return safe_finalize(DEFINITIONS["crossformer"])
    if ck == "reformer":
        return safe_finalize(DEFINITIONS["reformer"])
    if ck and ck in DEFINITIONS:
        return safe_finalize(DEFINITIONS[ck])
    return None

# ------------------------------------------------------------------------------
# PLANNING helpers
# ------------------------------------------------------------------------------
def slots_for(studio: Optional[str] = None, day: Optional[str] = None, course_key: Optional[str] = None) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
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
            if ck == "crossformer" and ("former" not in nm):
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

        out.append({"studio": s.studio, "day": s.day, "time": s.time, "name": s.name, "tag": s.tag})
    return out

def format_slots_grouped(slots: List[Dict[str, str]]) -> str:
    by_day: Dict[str, List[Dict[str, str]]] = {d: [] for d in DAY_ORDER}
    for s in slots:
        by_day[s["day"]].append(s)
    lines: List[str] = []
    for d in DAY_ORDER:
        items = by_day[d]
        if not items:
            continue
        items_sorted = sorted(items, key=lambda z: (len(z["time"]), z["time"]))
        times = ", ".join([f"{x['time']} ({x['name']})" for x in items_sorted])
        lines.append(f"- **{d.capitalize()}** : {times}")
    return "\n".join(lines) if lines else "Je n’ai rien trouvé sur le planning actuel."

def answer_planning(text: str) -> str:
    studio = extract_studio(text) or st.session_state.profile.get("studio")
    day = extract_day(text)
    ck = extract_course_key(text) or st.session_state.profile.get("course")

    if ck and not studio:
        if ck in ("reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch"):
            studio = "lavandieres"
        else:
            studio = "docks"

    if studio and not ck and not day:
        found = slots_for(studio=studio)
        return safe_finalize(f"Planning **{STUDIOS[studio]['label']}** 👇\n\n{format_slots_grouped(found)}")

    if ck and not day:
        found = slots_for(studio=studio, course_key=ck) if studio else slots_for(course_key=ck)
        if not found:
            return safe_finalize("Je ne vois pas ce cours sur le planning actuel. Tu parles de quel studio : Docks ou Lavandières ?")
        studio_txt = f" — {STUDIOS[studio]['label']}" if studio in STUDIOS else ""
        course_name = found[0]["name"]
        options = course_to_pass_options(course_name)
        opt_txt = " / ".join(options) if options else "selon la formule"
        return safe_finalize(
            f"Voilà les créneaux **{ck.capitalize()}**{studio_txt} 👇\n\n"
            f"{format_slots_grouped(found)}\n\n"
            f"✅ Accès via : **{opt_txt}**"
        )

    if ck and day:
        found = slots_for(studio=studio, day=day, course_key=ck)
        if not found:
            return safe_finalize(f"Je ne vois pas **{ck}** le **{day}** sur {STUDIOS[studio]['label']}. Tu veux que je te donne tous les jours où il y en a ?")
        times = ", ".join([x["time"] for x in found])
        course_name = found[0]["name"]
        opt_txt = " / ".join(course_to_pass_options(course_name))
        return safe_finalize(f"**{day.capitalize()}** : {ck.capitalize()} à **{times}** ({STUDIOS[studio]['label']}). ✅ {opt_txt}")

    return safe_finalize("Dis-moi le cours + le studio (ex: “Reformer lavandières” ou “Boxe docks”) et je te donne les créneaux.")

# ------------------------------------------------------------------------------
# RECO / "RÉFLEXION" deterministic
# ------------------------------------------------------------------------------
def recommend_from_profile() -> str:
    p = st.session_state.profile
    goals = set(p.get("goals") or set())
    studio = p.get("studio")

    suggestions: List[str] = []
    if "dos" in goals or "debutant" in goals:
        suggestions.append("Reformer")
    if "mobilite" in goals or "stress" in goals:
        suggestions.append("Yoga Vinyasa")
        suggestions.append("Core & Stretch")
    if "cardio" in goals:
        suggestions.append("Crossformer")
        suggestions.append("Boxe")
    if "tonus" in goals:
        suggestions.append("Reformer")
        suggestions.append("Power Pilates")

    if not suggestions:
        suggestions = ["Reformer", "Crossformer"]

    suggestions = list(dict.fromkeys(suggestions))[:2]
    studio_txt = f"Tu préfères plutôt **{STUDIOS[studio]['label']}** ou l’autre studio ?" if studio in STUDIOS else "Tu préfères plutôt **Docks** ou **Lavandières** ?"

    return safe_finalize(
        "OK 🙂 Voilà ce que je te conseillerais :\n"
        + "\n".join([f"- **{s}**" for s in suggestions])
        + f"\n\n{studio_txt}"
    )

# ==============================================================================
# ROUTER DÉTERMINISTE (anti “répond à côté”)
# ==============================================================================
def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
    if intent_human(user_text):
        return safe_finalize("OK 🙂 Je te mets avec l’équipe."), True

    if intent_pause_subscription(user_text):
        return answer_pause(), False

    if intent_rules(user_text):
        return answer_rules(user_text), False

    if intent_signup(user_text):
        return answer_signup(), True

    if intent_trial(user_text):
        return answer_trial(), False
    if intent_starter(user_text):
        return answer_starter(), False
    if intent_boost(user_text):
        return answer_boost(), False
    if intent_parrainage(user_text):
        return answer_parrainage(), False

    if intent_definition(user_text):
        d = answer_definition(user_text)
        if d:
            return d, False

    if intent_planning(user_text):
        return answer_planning(user_text), False

    if intent_pass_info(user_text):
        return answer_pass_info(user_text), False

    if intent_pass_price(user_text):
        pk = find_pass_key(user_text) or st.session_state.profile.get("pass_key")
        n = find_sessions_count(user_text) or st.session_state.profile.get("sessions")
        if pk and n:
            out = answer_pass_price(pk, n)
            if out:
                return out, False

    if intent_unit_price(user_text):
        return answer_unit_price(user_text), False

    if intent_interest(user_text):
        ck = extract_course_key(user_text)
        if ck:
            base = DEFINITIONS.get(ck, "OK 🙂")
            pl = answer_planning(ck)
            return safe_finalize(base + "\n\n" + pl + "\n\nTu préfères plutôt midi, fin d’après-midi ou soir ?"), False
        return recommend_from_profile(), False

    return None, False

# ==============================================================================
# GEMINI (optionnel) — orientation seulement
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

def allowed_amounts_set() -> Set[str]:
    allowed: Set[str] = set()
    allowed.add(eur(UNIT_PRICE["training"]))
    allowed.add(eur(UNIT_PRICE["machine"]))
    allowed.add(eur(TRIAL["price"]))
    allowed.add(eur(TRIAL["refund_if_signup"]))
    allowed.add(eur(STARTER["price"]))
    allowed.add(eur(BOOST["price"]))
    allowed.add(eur(FEES_AND_ENGAGEMENT["small_group_registration_fee"]))
    allowed.add(eur(FEES_AND_ENGAGEMENT["kids_registration_fee"]))
    allowed.add(eur(KIDS["extra_session"]))

    for p in PASS.values():
        for pp in p.prices.values():
            allowed.add(eur(pp.total))
            allowed.add(eur(round(pp.total / pp.sessions, 2)))

    for v in COACHING["good_vibes"]["prices"].values():
        allowed.add(eur(v))
    for v in COACHING["duo"]["prices"].values():
        allowed.add(eur(v))
    for v in COACHING["duo"]["per_person"].values():
        allowed.add(eur(v))
    return allowed

ALLOWED_AMOUNTS = allowed_amounts_set()
ALLOWED_TIMES = set([s.time for s in SLOTS])

def extract_euro_tokens(text: str) -> List[str]:
    tokens = re.findall(r"\b\d{1,3}(?:[ \.\,]\d{1,2})?\s?€\b", text)
    cleaned: List[str] = []
    for tok in tokens:
        tok = tok.replace(" ", "")
        m = re.match(r"^(\d{1,3})(?:[\,\.](\d{1,2}))?€$", tok)
        if m:
            euros = int(m.group(1))
            cents = m.group(2) if m.group(2) else "00"
            if len(cents) == 1:
                cents = cents + "0"
            cleaned.append(f"{euros},{cents}€")
        else:
            cleaned.append(tok)
    return cleaned

def extract_time_tokens(text: str) -> List[str]:
    raw = re.findall(r"\b\d{1,2}(?:h|:)\d{0,2}\b", text.lower())
    return [r.replace(":", "h") for r in raw]

def violates_guardrails(text: str) -> bool:
    for tok in extract_euro_tokens(text):
        if tok not in ALLOWED_AMOUNTS:
            return True
    for tok in extract_time_tokens(text):
        if tok in ("1h", "24h"):
            continue
        if tok not in ALLOWED_TIMES:
            return True
    return False

SYSTEM_PROMPT = """
Tu fais partie de l’équipe SVB. Tu écris comme une vraie personne (naturel, simple).
Tu NE dis JAMAIS que tu es une IA ou un bot.

RÈGLES ABSOLUES :
- Tu n’inventes AUCUN prix, AUCUN horaire, AUCUNE règle.
- Si la question contient des prix/horaires/règlement => tu poses 1 question courte OU tu proposes WhatsApp.
- Tu peux aider à choisir (orientation) selon objectif/niveau/studio.
- Style : doux, cocon, pro. Réponses courtes.

IMPORTANT :
- Pas de “Bienvenue chez SVB” à chaque message.
- Pas de phrases coupées : finis toujours ta réponse par une phrase complète.
""".strip()

def build_gemini_contents(history: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    trimmed = history[-18:]
    contents: List[Dict[str, Any]] = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for msg in trimmed:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return contents

def call_gemini(api_key: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    model = get_model(api_key)
    resp = model.generate_content(
        build_gemini_contents(history),
        generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 320},
    )
    text = safe_finalize((resp.text or "").strip())
    if not text:
        text = "Tu préfères plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ? 🙂"

    if violates_guardrails(text):
        return safe_finalize("Je préfère te répondre correctement : écris-nous sur WhatsApp et on te répond tout de suite 🙂"), True

    needs_wa = any(k in norm2(text) for k in ["whatsapp", "equipe", "équipe", "écris-nous", "ecris-nous", "contacte"])
    return text, needs_wa

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("### SVB • Infos")
    st.caption(f"WhatsApp : {CONTACT['phone']}")
    st.caption(f"Email : {CONTACT['email']}")
    st.caption(f"Instagram : {CONTACT['instagram']}")

# ==============================================================================
# UI — HISTORIQUE
# ==============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================================================================
# CHAT LOOP
# ==============================================================================
api_key = get_api_key()
prompt = st.chat_input("Posez votre question...")

if prompt:
    update_profile_from_text(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    det, needs_wa = deterministic_router(prompt)

    if det is not None:
        with st.chat_message("assistant"):
            st.markdown(det)
        st.session_state.messages.append({"role": "assistant", "content": det})
        if needs_wa:
            wa_button()
    else:
        if not GEMINI_AVAILABLE or not api_key:
            txt = safe_finalize("Je peux te guider 🙂 Dis-moi ton objectif (tonus, cardio, dos, mobilité) et ton studio (Docks ou Lavandières).")
            with st.chat_message("assistant"):
                st.markdown(txt)
            st.session_state.messages.append({"role": "assistant", "content": txt})
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        txt, needs_wa2 = call_gemini(api_key, st.session_state.messages)
                    st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
                if needs_wa2:
                    wa_button()
            except Exception:
                log.exception("Erreur Gemini")
                txt = safe_finalize("Petit souci technique. Le plus simple : WhatsApp 🙂")
                with st.chat_message("assistant"):
                    st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
                wa_button()