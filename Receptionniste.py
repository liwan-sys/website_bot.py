# receptionniste.py
from __future__ import annotations

import os
import re
import random
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

import streamlit as st

from knowledge import (
    CONTACT, STUDIOS, UNIT_PRICE, TRIAL, STARTER, BOOST,
    FEES_AND_ENGAGEMENT, COACHING, PASS, KIDS,
    RULES, PARRAINAGE, DAY_ORDER, SLOTS,
    DEFINITIONS, PASS_INCLUDES,
)

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
# HELPERS
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

def has_any(text: str, words: List[str]) -> bool:
    t = norm2(text)
    return any(w in t for w in words)

def safe_finalize(text: str) -> str:
    """Empêche les fins de phrase ‘coupées’ / sans ponctuation."""
    t = (text or "").strip()
    if not t:
        return t
    # si finit par une conjonction => on remplace par une question claire
    tail = norm2(t).split()[-1] if norm2(t).split() else ""
    if tail in {"si", "mais", "car", "donc", "parce", "parceque", "alors"}:
        return "Tu pensais à l’unité ou en abonnement (2/4/6/8/10/12 sessions) ? 🙂"
    # si pas de ponctuation finale => on ajoute un petit ‘🙂’
    if re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]$", t) and not re.search(r"[\.!\?…]$", t):
        return t + " 🙂"
    return t

def wa_button() -> None:
    st.markdown("---")
    st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

# ==============================================================================
# EXTRACTION — studio / jour / cours / sessions / pass
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

def intent_sessions_only(text: str) -> bool:
    # ex: "4", "4 session", "4 séances"
    return re.match(r"^\s*(2|4|6|8|10|12)\s*(seance|seances|séance|séances|session|sessions)?\s*$", text.strip(), re.I) is not None

def find_pass_key(text: str) -> Optional[str]:
    t = norm2(text)
    patterns = [
        ("full former", "full_former"),
        ("fullformer", "full_former"),
        ("pass full former", "full_former"),
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
    t = norm2(text)
    aliases = {
        "reformer": "reformer",
        "pilate reformer": "reformer",
        "pilates reformer": "reformer",
        "crossformer": "crossformer",
        "cross-former": "crossformer",
        "cross former": "crossformer",
        "pilates crossformer": "crossformer",
        "boxe": "boxe",
        "boxing": "boxe",
        "afrodance": "afrodance",
        "afrodance all": "afrodance",
        "afrodance'all": "afrodance",
        "cross training": "cross training",
        "cross-core": "cross core",
        "cross core": "cross core",
        "cross-body": "cross body",
        "cross body": "cross body",
        "cross-rox": "cross rox",
        "cross rox": "cross rox",
        "cross-yoga": "cross yoga",
        "cross yoga": "cross yoga",
        "yoga vinyasa": "yoga vinyasa",
        "vinyasa": "yoga vinyasa",
        "hatha flow": "hatha flow",
        "hatha": "hatha flow",
        "classic pilates": "classic pilates",
        "power pilates": "power pilates",
        "core & stretch": "core & stretch",
        "core and stretch": "core & stretch",
        "core stretch": "core & stretch",
        "stretch": "core & stretch",
        "yoga kids": "yoga kids",
        "training kids": "training kids",
    }
    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t:
            return aliases[k]
    return None

def canonical_to_course_name(ck: str) -> Optional[str]:
    """Pour relier la clé canonique à un nom exact dans PASS_INCLUDES."""
    mapping = {
        "reformer": "Reformer",
        "crossformer": "Cross-Former",
        "boxe": "Boxe",
        "afrodance": "Afrodance'All",
        "cross training": "Cross Training",
        "cross core": "Cross Core",
        "cross body": "Cross Body",
        "cross rox": "Cross Rox",
        "cross yoga": "Cross Yoga",
        "yoga vinyasa": "Yoga Vinyasa",
        "hatha flow": "Hatha Flow",
        "classic pilates": "Classic Pilates",
        "power pilates": "Power Pilates",
        "core & stretch": "Core & Stretch",
        "yoga kids": "Yoga Kids",
        "training kids": "Training Kids",
    }
    return mapping.get(ck)

def infer_pass_from_course(ck: Optional[str]) -> Optional[str]:
    if not ck:
        return None
    course_name = canonical_to_course_name(ck)
    if not course_name:
        return None
    for pk, courses in PASS_INCLUDES.items():
        if course_name in courses:
            # on renvoie la formule la plus “directe” (pas full par défaut)
            return pk
    return None

def pass_unit_price(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    return round(p.prices[sessions].total / sessions, 2)

# ==============================================================================
# MÉMO CONVERSATION (profil)
# ==============================================================================

def ensure_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "did_greet" not in st.session_state:
        st.session_state.did_greet = False
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "studio": None,
            "course": None,     # ex: "reformer"
            "pass_key": None,   # ex: "reformer"/"focus"/"cross"...
            "sessions": None,   # 2/4/6/8/10/12
            "last_topic": None, # "price" / "planning" / ...
        }

def update_profile_from_text(text: str) -> None:
    p = st.session_state.profile
    s = extract_studio(text)
    if s:
        p["studio"] = s
    ck = extract_course_key(text)
    if ck:
        p["course"] = ck
    pk = find_pass_key(text)
    if pk:
        p["pass_key"] = pk
    n = find_sessions_count(text)
    if n:
        p["sessions"] = n

def first_message() -> str:
    return random.choice([
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif (tonus, cardio, dos, mobilité…) et je te guide.",
        "OK 🙂 Tu veux plutôt venir aux Docks ou aux Lavandières ?",
    ])

ensure_state()
if not st.session_state.did_greet and len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": first_message()})
    st.session_state.did_greet = True

# ==============================================================================
# INTENTS (plus précis)
# ==============================================================================

def intent_human(text: str) -> bool:
    return has_any(text, ["humain", "conseiller", "equipe", "équipe", "whatsapp", "joindre", "appeler", "telephone", "téléphone"])

def intent_pause_subscription(text: str) -> bool:
    return has_any(text, ["pause", "mettre en pause", "suspendre", "suspension", "arreter provisoirement", "stopper provisoirement"])

def intent_rules(text: str) -> bool:
    return has_any(text, ["annulation", "annuler", "report", "reporter", "cumul", "resiliation", "résiliation",
                          "preavis", "préavis", "retard", "chaussette", "chaussettes", "reglement", "règlement",
                          "interieur", "intérieur", "absence"])

def intent_signup(text: str) -> bool:
    # IMPORTANT: pas "abonnement" seul
    return has_any(text, ["m'inscrire", "inscrire", "inscription", "creer un compte", "créer un compte",
                          "identifiant", "mot de passe", "connexion", "connecter", "appli", "application", "sportigo"])

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
    return has_any(text, ["donne acces", "donne accès", "ça donne accès", "inclut", "comprend", "c'est quoi le pass", "pass "])

def intent_price(text: str) -> bool:
    return has_any(text, ["tarif", "prix", "combien", "coute", "coûte", "mensuel", "mois", "abonnement", "forfait"])

def intent_unit_price(text: str) -> bool:
    return has_any(text, ["a l'unite", "à l'unité", "sans abonnement", "sans abo", "unité", "unite"])

# ==============================================================================
# RÉPONSES DÉTERMINISTES
# ==============================================================================

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
        "Si tu veux, dis-moi ton pass et je te dis la marche à suivre la plus simple."
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
    ck = extract_course_key(text)
    if ck and ck in DEFINITIONS:
        return safe_finalize(DEFINITIONS[ck])
    return None

def answer_unit_price(text: str) -> str:
    ck = extract_course_key(text)
    if ck in ("reformer", "crossformer"):
        return safe_finalize(f"Sans abonnement, une séance **Machine** est à **{eur(UNIT_PRICE['machine'])}**.")
    return safe_finalize(f"Sans abonnement, une séance **Training / cours** est à **{eur(UNIT_PRICE['training'])}**.")

def answer_pass_price(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    unit = pass_unit_price(pass_key, sessions)
    studio_txt = STUDIOS[p.where]["label"] if p.where in STUDIOS else p.where
    extra = ""
    if pass_key == "kids":
        extra = f"\n- Séance supplémentaire kids : **{eur(KIDS['extra_session'])}**"
    return safe_finalize(
        f"📌 **{p.label}** — {sessions} sessions / mois\n"
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance (calcul) : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
        f"- Studio : {studio_txt}"
        f"{extra}"
    )

def answer_ask_sessions_for_course(ck: str) -> str:
    # question déterministe (pas Gemini)
    if ck in ("reformer", "crossformer"):
        return safe_finalize("Tu veux **à l’unité** ou en abonnement : **2/4/6/8/10/12 sessions** par mois ?")
    return safe_finalize("Tu veux plutôt **2/4/6/8/10/12 sessions** par mois ? (et tu préfères Pass Cross, Focus ou Full ?)")

# ------------------------------------------------------------------------------
# PLANNING
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
            if ck == "crossformer" and "former" not in nm:
                continue
            if ck == "boxe" and "boxe" not in nm:
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
        studio = "lavandieres" if ck in ("reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch") else "docks"

    if studio and not ck and not day:
        found = slots_for(studio=studio)
        return safe_finalize(f"Planning **{STUDIOS[studio]['label']}** 👇\n\n{format_slots_grouped(found)}")

    if ck and not day:
        found = slots_for(studio=studio, course_key=ck)
        if not found:
            return safe_finalize("Je ne vois pas ce cours sur le planning actuel. Tu parles de quel studio : Docks ou Lavandières ?")
        return safe_finalize(f"Voilà les créneaux **{ck.capitalize()}** — {STUDIOS[studio]['label']} 👇\n\n{format_slots_grouped(found)}")

    if ck and day:
        found = slots_for(studio=studio, day=day, course_key=ck)
        if not found:
            return safe_finalize(f"Je ne vois pas **{ck}** le **{day}** sur {STUDIOS[studio]['label']}. Tu veux tous les jours où il y en a ?")
        times = ", ".join([x["time"] for x in found])
        return safe_finalize(f"**{day.capitalize()}** : {ck.capitalize()} à **{times}** ({STUDIOS[studio]['label']}).")

    return safe_finalize("Dis-moi le cours + le studio (ex: “Reformer lavandières” ou “Boxe docks”) et je te donne les créneaux.")

# ==============================================================================
# ROUTER — le vrai FIX est ici : intent_sessions_only() + inference
# ==============================================================================
def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
    p = st.session_state.profile

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

    # ✅ CAS CRITIQUE : réponse courte "4 session"
    if intent_sessions_only(user_text):
        n = find_sessions_count(user_text) or p.get("sessions")
        ck = p.get("course")
        pk = p.get("pass_key")

        if not pk:
            pk = infer_pass_from_course(ck)

        if pk and n:
            out = answer_pass_price(pk, int(n))
            if out:
                return out, False

        # si on ne peut pas inférer
        if ck:
            return safe_finalize(f"OK 🙂 Pour **{ck}**, tu veux quelle formule exactement ? (Pass Reformer / Crossformer / Full Former / Full)"), False
        return safe_finalize("OK 🙂 Tu parles de quel cours / pass ?"), False

    # Prix (même si le user écrit juste "combien le reformer")
    if intent_price(user_text):
        ck = extract_course_key(user_text)
        if ck and not find_sessions_count(user_text) and not intent_unit_price(user_text):
            # on demande les sessions pour éviter Gemini
            p["last_topic"] = "price"
            return answer_ask_sessions_for_course(ck), False

        # si on a déjà sessions + pass (ou inférence)
        pk = find_pass_key(user_text) or p.get("pass_key")
        n = find_sessions_count(user_text) or p.get("sessions")

        if not pk:
            pk = infer_pass_from_course(extract_course_key(user_text) or p.get("course"))

        if pk and n:
            out = answer_pass_price(pk, int(n))
            if out:
                return out, False

    if intent_unit_price(user_text):
        return answer_unit_price(user_text), False

    return None, False

# ==============================================================================
# GEMINI — ORIENTATION ONLY (et on sanitize “Bienvenue”)
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

SYSTEM_PROMPT = """
Tu fais partie de l’équipe SVB. Style humain, simple, premium.
Tu NE dis JAMAIS “Bienvenue chez SVB” et tu ne te présentes pas.

RÈGLES :
- Tu n’inventes aucun prix, aucun horaire, aucune règle.
- Si l’utilisateur demande prix/horaires/règlement => 1 question courte max ou WhatsApp.
- Finis TOUJOURS avec une phrase complète.
""".strip()

def sanitize_llm(text: str) -> str:
    t = (text or "").strip()
    t2 = norm2(t)
    if t2.startswith("hello") and "bienvenue" in t2[:40]:
        # on coupe l’accueil
        t = re.sub(r"(?i)^hello\s*!?\s*bienvenue.*?\?\s*", "", t).strip()
    if t2.startswith("bienvenue"):
        t = re.sub(r"(?i)^bienvenue.*?\?\s*", "", t).strip()
    return safe_finalize(t)

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
        generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 220},
    )
    text = sanitize_llm(resp.text or "")
    if not text:
        text = "Tu préfères Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ? 🙂"
    needs_wa = "whatsapp" in norm2(text)
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
            txt = safe_finalize("Dis-moi ton objectif + ton studio (Docks ou Lavandières) et je te guide 🙂")
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