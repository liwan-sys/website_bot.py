<<<<<<< HEAD
# ==============================================================================
# SARAH — SVB CHATBOT (Streamlit + Gemini) — VERSION PROPRE "ANTI-ERREURS"
# ==============================================================================
#
# OBJECTIF (VALIDÉ PAR TOI)
# 1) ZÉRO ERREUR sur tarifs / règles / inscription / prix à l’unité / séance supp.
#    => Tout ce qui est "chiffré" ou "règle" = DÉTERMINISTE (Python).
# 2) Gemini = uniquement pour l’orientation, la reformulation, le ton humain,
#    et les questions de qualification. Jamais de prix inventé.
# 3) "Humain" : pas de présentation répétée, pas de ton bot, réponses naturelles.
#
# RÈGLES OFFICIELLES (TES RÉPONSES)
# - Source de vérité: SITE (studiosvb.com) + tes règles internes validées ici.
# - Ajout / séance supplémentaire quand on est abonné : AU PRORATA DU PASS (prix / nb sessions).
# - Prix à l’unité (non abonné) : Training = 30€ ; Machine = 50€.
# - Essai : 30€ remboursé si inscription.
# - Offre Starter 99,90€ : 5 sessions / 1 mois MAIS 1 séance par discipline (pas 5 fois la même discipline).
# - Human alert : si le client demande un humain OU si question trop complexe / info incertaine.
#
# ==============================================================================
# IMPORTANT
# - Tu peux adapter les valeurs/labels/tarifs dans CONFIG_TARIFS si ton site change.
# - Ne mets jamais une règle "inventée" ici. Si doute => [HUMAN_ALERT]
# ==============================================================================
=======
# Receptionniste.py
from __future__ import annotations
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

import os
import re
import random
import logging
<<<<<<< HEAD
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple, Any
=======
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

import streamlit as st

<<<<<<< HEAD
# ------------------------------------------------------------------------------
# 0) Logging
# ------------------------------------------------------------------------------
=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ------------------------------------------------------------------------------
<<<<<<< HEAD
# 1) Dépendance Gemini
=======
# 0) CHARGEMENT ROBUSTE DE knowledge.py (évite les ImportError)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ------------------------------------------------------------------------------
def load_knowledge_module():
    here = Path(__file__).resolve().parent
    kp = here / "knowledge.py"

    if not kp.exists():
        st.error("❌ Fichier **knowledge.py** introuvable.")
        st.info("👉 Mets **knowledge.py** dans le **même dossier** que Receptionniste.py (dans ton repo Streamlit Cloud).")
        st.stop()

    import importlib.util
    spec = importlib.util.spec_from_file_location("knowledge", str(kp))
    if spec is None or spec.loader is None:
        st.error("❌ Impossible de charger knowledge.py (spec/loader).")
        st.stop()

    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        st.error("❌ Erreur dans **knowledge.py** (syntaxe / copier-coller incomplet).")
        st.code(traceback.format_exc())
        st.info("👉 Corrige l’erreur affichée ci-dessus (ou recolle un knowledge.py propre).")
        st.stop()

K = load_knowledge_module()

# ------------------------------------------------------------------------------
# 1) GEMINI (optionnel)
# ------------------------------------------------------------------------------
try:
<<<<<<< HEAD
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR : module 'google.generativeai' manquant. Installe: pip install google-generativeai")
    st.stop()
=======
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

# ------------------------------------------------------------------------------
<<<<<<< HEAD
# 2) Page config
=======
# 2) PAGE CONFIG + CSS
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

<<<<<<< HEAD
# ------------------------------------------------------------------------------
# 3) CSS (ton identité)
# ------------------------------------------------------------------------------
=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');
<<<<<<< HEAD

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
=======
.stApp{background:linear-gradient(180deg,#F9F7F2 0%,#E6F0E6 100%);font-family:'Lato',sans-serif;color:#4A4A4A;}
#MainMenu, footer, header {visibility:hidden;}
h1{font-family:'Dancing Script',cursive;color:#8FB592;text-align:center;font-size:3.4rem !important;margin-bottom:0px !important;text-shadow:2px 2px 4px rgba(0,0,0,0.10);}
.subtitle{text-align:center;color:#EBC6A6;font-size:1.0rem;font-weight:700;margin-bottom:18px;text-transform:uppercase;letter-spacing:2px;}
.stChatMessage{background-color:rgba(255,255,255,0.95)!important;border:1px solid #EBC6A6;border-radius:15px;padding:14px;box-shadow:0 4px 6px rgba(0,0,0,0.05);color:#1f1f1f !important;}
.stChatMessage p,.stChatMessage li{color:#1f1f1f !important;line-height:1.6;}
.stButton button{background:linear-gradient(90deg,#25D366 0%,#128C7E 100%);color:white !important;border:none;border-radius:25px;padding:12px 25px;font-weight:800;width:100%;text-transform:uppercase;}
.stButton button:hover{transform: scale(1.02);}
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
</style>
""",
    unsafe_allow_html=True,
)

<<<<<<< HEAD
# ------------------------------------------------------------------------------
# 4) Header
# ------------------------------------------------------------------------------
=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

<<<<<<< HEAD
# ==============================================================================
# 5) CONFIG — SOURCE DE VERITÉ (Tarifs + Règles)
# ==============================================================================
=======
# ------------------------------------------------------------------------------
# 3) ON RÉCUPÈRE TOUT DE knowledge.py
# ------------------------------------------------------------------------------
CONTACT = K.CONTACT
STUDIOS = K.STUDIOS
UNIT_PRICE = K.UNIT_PRICE
TRIAL = K.TRIAL
STARTER = K.STARTER
BOOST = K.BOOST
FEES_AND_ENGAGEMENT = K.FEES_AND_ENGAGEMENT
COACHING = K.COACHING
PASS = K.PASS
KIDS = K.KIDS
RULES = K.RULES
PARRAINAGE = K.PARRAINAGE
DAY_ORDER = K.DAY_ORDER
SLOTS = K.SLOTS
DEFINITIONS = K.DEFINITIONS
PASS_INCLUDES = K.PASS_INCLUDES
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
WHATSAPP_URL = "https://wa.me/33744919155"
WHATSAPP_LABEL = "📞 Contacter l'équipe (WhatsApp)"

# ---- Prix à l’unité (non abonné) — OFFICIEL ----
UNIT_PRICE = {
    "training": 30.0,  # Cross / Focus / Full (sol / training)
    "machine": 50.0,   # Reformer / Crossformer / Full Former (machines)
}

# ---- Essai — OFFICIEL ----
TRIAL = {
    "price": 30.0,
    "refunded_if_signup": True,  # remboursé si inscription
}

# ---- Starter — OFFICIEL ----
STARTER = {
    "price": 99.90,
    "sessions": 5,
    "duration_days": 30,  # 1 mois
    "discipline_rule": "1 séance par discipline (pas 5 fois la même discipline).",
}

# ---- Séance supplémentaire (abonné) — OFFICIEL : prorata du pass ----
EXTRA_SESSION_POLICY = {
    "mode": "pro_rata_of_member_pass",  # (seule règle active)
}

# ---- Infos studios (neutres, sans inventer de règles) ----
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

# ---- Discipline / catégories pour router les prix ----
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

# ---- Pass mensuels (ceux que tu avais dans ton code) ----
# Si ton site change, modifie ici.
@dataclass(frozen=True)
class PassPrice:
    sessions: int
    price: float  # euros

@dataclass(frozen=True)
class PassConfig:
    key: str
    label: str
    category: str          # "training" / "machine" / "kids"
    studio_hint: str       # Docks / Lavandières / Mixte
    includes: str
    duration_min: int
    prices: Dict[int, PassPrice]  # sessions -> price

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

# Kids (tarifs limités)
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
# 6) Helpers format / parsing
# ==============================================================================

def eur(value: float) -> str:
    # 60.30 -> "60,30€"
    return f"{value:,.2f}€".replace(",", " ").replace(".", ",")

def normalize(text: str) -> str:
    return (text or "").strip().lower()

=======
# ==============================================================================
# HELPERS
# ==============================================================================
def eur(x: float) -> str:
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s}€"

def norm(s: str) -> str:
    return (s or "").strip().lower()

def strip_accents_cheap(s: str) -> str:
    repl = {"é":"e","è":"e","ê":"e","ë":"e","à":"a","â":"a","î":"i","ï":"i","ô":"o","ù":"u","û":"u","ç":"c","’":"'","“":'"',"”":'"'}
    for k,v in repl.items():
        s = s.replace(k,v)
    return s

def norm2(s: str) -> str:
    return strip_accents_cheap(norm(s))

def safe_finalize(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return t
    words = norm2(t).split()
    last = words[-1] if words else ""
    if last in {"si","mais","car","donc","parce","parceque","alors"}:
        return "Tu pensais à l’unité ou en abonnement (2/4/6/8/10/12 sessions) ? 🙂"
    if re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]$", t) and not re.search(r"[\.!\?…]$", t):
        return t + " 🙂"
    return t

def wa_button():
    st.markdown("---")
    st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

def has_any(text: str, words: List[str]) -> bool:
    t = norm2(text)
    return any(w in t for w in words)

# ==============================================================================
# EXTRACTION
# ==============================================================================
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
def find_sessions_count(text: str) -> Optional[int]:
    # capture 2/4/6/8/10/12
    m = re.search(r"\b(2|4|6|8|10|12)\b", normalize(text))
    if m:
        return int(m.group(1))
    return None

def intent_sessions_only(text: str) -> bool:
    return re.match(r"^\s*(2|4|6|8|10|12)\s*(seance|seances|séance|séances|session|sessions)?\s*$", text.strip(), re.I) is not None

def find_pass_key(text: str) -> Optional[str]:
<<<<<<< HEAD
    t = normalize(text)

    # mapping "user words" -> pass key
=======
    t = norm2(text)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    patterns = [
<<<<<<< HEAD
        ("full former", "full_former"),
        ("fullformer", "full_former"),
        ("reformer", "reformer"),
        ("crossformer", "crossformer"),
        ("pass cross", "cross"),
        ("cross", "cross"),
        ("pass focus", "focus"),
        ("focus", "focus"),
        ("pass full", "full"),
        ("full", "full"),
        ("kids", "kids"),
        ("enfant", "kids"),
        ("enfants", "kids"),
=======
        ("full former","full_former"), ("fullformer","full_former"),
        ("pass full","full"), ("pass focus","focus"), ("pass cross","cross"),
        ("crossformer","crossformer"), ("reformer","reformer"),
        ("kids","kids"), ("enfant","kids"),
        ("full","full"), ("focus","focus"), ("cross","cross")
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    ]
    for needle, key in patterns:
        if needle in t:
            return key
    return None

<<<<<<< HEAD
def unit_price_from_pass(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS_CONFIGS.get(pass_key)
    if not p:
        return None
    if sessions not in p.prices:
        return None
    total = p.prices[sessions].price
    return round(total / sessions, 2)

=======
def extract_course_key(text: str) -> Optional[str]:
    t = norm2(text)
    aliases = {
        "pilates reformer":"reformer","pilate reformer":"reformer","reformer":"reformer",
        "cross-former":"crossformer","cross former":"crossformer","crossformer":"crossformer",
        "boxe":"boxe","boxing":"boxe","afrodance":"afrodance","afrodance all":"afrodance","afrodance'all":"afrodance",
        "cross training":"cross training","cross core":"cross core","cross body":"cross body","cross rox":"cross rox","cross yoga":"cross yoga",
        "yoga vinyasa":"yoga vinyasa","vinyasa":"yoga vinyasa",
        "hatha flow":"hatha flow","hatha":"hatha flow",
        "classic pilates":"classic pilates","power pilates":"power pilates",
        "core & stretch":"core & stretch","core and stretch":"core & stretch","stretch":"core & stretch",
        "yoga kids":"yoga kids","training kids":"training kids",
    }
    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t:
            return aliases[k]
    return None

def canonical_to_course_name(ck: str) -> Optional[str]:
    m = {
        "reformer":"Reformer","crossformer":"Cross-Former",
        "boxe":"Boxe","afrodance":"Afrodance'All",
        "cross training":"Cross Training","cross core":"Cross Core","cross body":"Cross Body","cross rox":"Cross Rox","cross yoga":"Cross Yoga",
        "yoga vinyasa":"Yoga Vinyasa","hatha flow":"Hatha Flow","classic pilates":"Classic Pilates","power pilates":"Power Pilates","core & stretch":"Core & Stretch",
        "yoga kids":"Yoga Kids","training kids":"Training Kids",
    }
    return m.get(ck)

def infer_pass_from_course(ck: Optional[str]) -> Optional[str]:
    if not ck:
        return None
    cname = canonical_to_course_name(ck)
    if not cname:
        return None
    for pk, courses in PASS_INCLUDES.items():
        if cname in courses:
            return pk
    return None

def pass_unit_price(pass_key: str, sessions: int) -> Optional[float]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    return round(p.prices[sessions].total / sessions, 2)

>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ==============================================================================
<<<<<<< HEAD
# 7) Détection d’intentions (deterministic router)
=======
# STATE (mémoire courte)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ==============================================================================
def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "did_greet" not in st.session_state:
        st.session_state.did_greet = False
    if "profile" not in st.session_state:
        st.session_state.profile = {"course": None, "pass_key": None, "sessions": None}

<<<<<<< HEAD
def is_human_request(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "humain", "quelqu'un", "conseiller", "équipe", "equipe",
        "whatsapp", "appeler", "téléphone", "telephone",
        "contact", "joindre", "parler à", "parler a"
    ])
=======
def update_profile(text: str):
    p = st.session_state.profile
    ck = extract_course_key(text)
    if ck:
        p["course"] = ck
    pk = find_pass_key(text)
    if pk:
        p["pass_key"] = pk
    n = find_sessions_count(text)
    if n:
        p["sessions"] = n
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def is_signup_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "m'inscrire", "inscription", "inscrire", "s’inscrire", "s'inscrire",
        "abonner", "abonnement",
        "créer un compte", "creer un compte",
        "identifiant", "identifiants", "mot de passe",
        "connexion", "se connecter", "connecter"
=======
def first_message() -> str:
    return random.choice([
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif (tonus, cardio, dos, mobilité…) et je te guide.",
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    ])

<<<<<<< HEAD
def is_trial_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "essai", "séance d'essai", "seance d'essai",
        "découverte", "decouverte", "tester", "test"
    ])
=======
ensure_state()
if not st.session_state.did_greet and len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": first_message()})
    st.session_state.did_greet = True
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def is_starter_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "starter", "new pass starter", "pass starter", "offre starter",
        "99,90", "99.90", "99,9", "99.9", "99€"
    ])

def is_unit_price_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "à l'unité", "a l'unite", "unité", "unite",
        "sans abonnement", "sans abo", "sans être abonné", "sans etre abonne",
        "prix d'une séance", "prix d’une séance", "prix séance", "prix seance"
    ])
=======
# ==============================================================================
# INTENTS
# ==============================================================================
def intent_price(text: str) -> bool:
    return has_any(text, ["tarif","prix","combien","coute","coûte","abonnement","forfait","mensuel","mois"])

def intent_unit_price(text: str) -> bool:
    return has_any(text, ["a l'unite","à l'unité","sans abonnement","sans abo","unité","unite"])
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def is_extra_session_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "séance supp", "seance supp", "séance supplémentaire", "seance supplementaire",
        "ajouter une séance", "ajouter une seance", "rajouter une séance", "rajouter une seance",
        "séance en plus", "seance en plus"
    ])

def is_pass_price_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "tarif", "prix", "coût", "cout", "combien",
        "abonnement", "pass", "forfait"
    ])
=======
def intent_definition(text: str) -> bool:
    return has_any(text, ["c'est quoi","c quoi","definition","définition","explique","différence","difference"])
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def is_studio_access_question(text: str) -> bool:
    t = normalize(text)
    return any(x in t for x in [
        "autre studio", "deux studios", "2 studios",
        "lavandières", "lavandieres", "docks",
        "je peux aller", "je peux réserver", "je peux reserver",
        "accès", "acces", "réserver dans l'autre", "reserver dans l'autre"
    ])
=======
def intent_signup(text: str) -> bool:
    return has_any(text, ["m'inscrire","inscription","creer un compte","créer un compte","identifiant","connexion","appli","application","sportigo"])
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

# ==============================================================================
<<<<<<< HEAD
# 8) Réponses déterministes (tarifs/règles/inscription)
=======
# RÉPONSES
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ==============================================================================
<<<<<<< HEAD

HUMAN_ACKS = [
    "OK 🙂", "Parfait.", "Je vois.", "Bien sûr.", "Top.", "D’accord.", "Yes.", "Très bien."
]

def ack() -> str:
    return random.choice(HUMAN_ACKS)

def signup_answer() -> str:
    # EXACTEMENT ce que tu as validé
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
=======
def answer_signup() -> str:
    return safe_finalize(
        "Pour t’inscrire :\n\n"
        "1) Tu souscris ton abonnement en ligne.\n"
        "2) Après le paiement, tu reçois automatiquement un e-mail avec tes identifiants.\n"
        "3) Tu télécharges l’application (SVB / Sportigo).\n"
        "4) Tu rentres les identifiants reçus par e-mail.\n"
        "5) Ensuite tu réserves tes séances ✅\n\n"
        "Si tu ne reçois pas l’e-mail (spam / délai), écris-nous sur WhatsApp."
    )
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def starter_answer() -> str:
    return (
        f"⭐ Offre Starter : **{eur(STARTER['price'])}** — **{STARTER['sessions']} sessions** sur **1 mois**.\n"
        f"📌 Règle : **{STARTER['discipline_rule']}**"
    )
=======
def answer_definition(text: str) -> Optional[str]:
    ck = extract_course_key(text)
    if ck and ck in DEFINITIONS:
        return safe_finalize(DEFINITIONS[ck])
    return None
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def unit_price_answer(text: str) -> str:
    t = normalize(text)

    # essaie de détecter si client parle training vs machine
    cat = None
    for k, v in DISCIPLINE_TO_CATEGORY.items():
        if k in t:
            cat = v
            break

    # si pas trouvé, on propose les deux (officiel)
    if cat is None or cat not in ("training", "machine"):
        return (
            "À l’unité (sans abonnement) :\n"
            f"- Training : **{eur(UNIT_PRICE['training'])}**\n"
            f"- Machines : **{eur(UNIT_PRICE['machine'])}**\n\n"
            "Vous cherchez plutôt un cours Training (Cross/Boxe/Yoga…) ou une Machine (Reformer/Crossformer) ?"
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
=======
def answer_unit_price(text: str) -> str:
    ck = extract_course_key(text)
    if ck in ("reformer","crossformer"):
        return safe_finalize(f"Sans abonnement, une séance **Machine** est à **{eur(UNIT_PRICE['machine'])}**.")
    return safe_finalize(f"Sans abonnement, une séance **Training / cours** est à **{eur(UNIT_PRICE['training'])}**.")
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def pass_price_answer(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS_CONFIGS.get(pass_key)
    if not p:
=======
def answer_pass_price(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
        return None
<<<<<<< HEAD
    if sessions not in p.prices:
        return None
    total = p.prices[sessions].price
    unit = unit_price_from_pass(pass_key, sessions)
    return (
        f"📌 {p.label} — {sessions} sessions/mois\n"
=======
    total = p.prices[sessions].total
    unit = pass_unit_price(pass_key, sessions)
    extra = ""
    if pass_key == "kids":
        extra = f"\n- Séance supplémentaire kids : **{eur(KIDS['extra_session'])}**"
    studio_txt = STUDIOS[p.where]["label"] if p.where in STUDIOS else p.where
    return safe_finalize(
        f"📌 **{p.label}** — {sessions} sessions / mois\n"
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
<<<<<<< HEAD
        f"- Studio : {p.studio_hint}\n"
        f"- Inclus : {p.includes}"
=======
        f"- Studio : {studio_txt}"
        f"{extra}"
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    )

<<<<<<< HEAD
def extra_session_answer(text: str) -> str:
    # OFFICIEL : prorata du pass
    pass_key = find_pass_key(text)
    sessions = find_sessions_count(text)
=======
def answer_ask_sessions(ck: str) -> str:
    if ck in ("reformer","crossformer"):
        return safe_finalize("Tu veux **à l’unité** ou en abonnement : **2/4/6/8/10/12 sessions** par mois ?")
    return safe_finalize("Tu veux combien de sessions par mois : **2/4/6/8/10/12** ?")
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
    if not pass_key or not sessions:
        return (
            "Pour que je calcule au prorata, il me faut :\n"
            "1) votre pass (Cross / Focus / Full / Reformer / Crossformer / Full Former / Kids)\n"
            "2) le nombre de sessions (2/4/6/8/10/12)\n\n"
            "Exemple : *Pass Cross 4* → prix séance = (prix du pass / 4)."
        )

    # Kids : on peut aussi faire prorata (puisque tu as dit Q2/A général),
    # donc on applique pareil, sauf si tu veux une règle spéciale plus tard.
    u = unit_price_from_pass(pass_key, sessions)
    if u is None:
        return (
            "Je peux le calculer, mais je n’ai pas reconnu la formule exacte.\n"
            "Dites-moi : Cross / Focus / Full / Reformer / Crossformer / Full Former + 2/4/6/8/10/12."
        )

    p = PASS_CONFIGS[pass_key]
    total = p.prices[sessions].price
    return (
        "Séance supplémentaire (au prorata de votre abonnement) :\n"
        f"- Formule : **{p.label} {sessions}**\n"
        f"- Calcul : {eur(total)} / {sessions} = **{eur(u)}**\n\n"
        "Vous voulez l’ajouter sur quel cours (et quel studio) ?"
    )

def studio_access_answer(text: str) -> str:
    # Q4 = D (ça dépend) => on ne doit surtout pas inventer.
    # On pose une question claire pour trancher.
    return (
        "Ça dépend de votre formule.\n"
        "Dites-moi : vous avez quel abonnement (Cross / Focus / Full / Reformer / Crossformer / Full Former) "
        "et vous voulez réserver dans quel studio (Docks ou Lavandières) ?"
    )

def human_alert_answer(reason: str = "") -> str:
    # Réponse naturelle + tag pour afficher bouton
    if reason:
        return f"{reason}\n\n[HUMAN_ALERT]"
    return "Je préfère vous mettre directement avec l’équipe pour être sûr à 100%. \n\n[HUMAN_ALERT]"

# ==============================================================================
# 9) Router déterministe (priorités)
# ==============================================================================

=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
<<<<<<< HEAD
    """
    Retourne (answer, needs_whatsapp)
    Si answer None => on passe à Gemini.
    """
=======
    prof = st.session_state.profile
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
    # 1) Si demande un humain
    if is_human_request(user_text):
        ans = human_alert_answer("OK, je vous mets avec l’équipe 🙂")
        return ans.replace("[HUMAN_ALERT]", ""), True

    # 2) Inscription (tu as donné le flow exact)
    if is_signup_question(user_text):
        return signup_answer(), False

    # 3) Essai
    if is_trial_question(user_text):
        return trial_answer(), False
=======
    if intent_signup(user_text):
        return answer_signup(), True
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
    # 4) Starter
    if is_starter_question(user_text):
        return starter_answer(), False

    # 5) Séance supplémentaire (prorata)
    if is_extra_session_question(user_text):
        return extra_session_answer(user_text), False
=======
    if intent_definition(user_text):
        d = answer_definition(user_text)
        if d:
            return d, False
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
    # 6) Prix à l’unité (non abonné)
    if is_unit_price_question(user_text):
        return unit_price_answer(user_text), False
=======
    # ✅ réponse courte “4 session”
    if intent_sessions_only(user_text):
        n = find_sessions_count(user_text) or prof.get("sessions")
        pk = prof.get("pass_key") or infer_pass_from_course(prof.get("course"))
        if pk and n:
            out = answer_pass_price(pk, int(n))
            if out:
                return out, False
        return safe_finalize("OK 🙂 Tu parles de quel pass ? (Cross / Focus / Full / Reformer / Crossformer / Full Former)"), False
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
    # 7) Accès autre studio (ça dépend)
    if is_studio_access_question(user_text):
        return studio_access_answer(user_text), False

    # 8) Prix d’un pass si pass + sessions
    if is_pass_price_question(user_text):
        pk = find_pass_key(user_text)
        s = find_sessions_count(user_text)
        if pk and s:
            pp = pass_price_answer(pk, s)
            if pp:
                return pp, False
=======
    if intent_unit_price(user_text):
        return answer_unit_price(user_text), False

    if intent_price(user_text):
        ck = extract_course_key(user_text)
        if ck and not find_sessions_count(user_text) and not find_pass_key(user_text) and not intent_unit_price(user_text):
            return answer_ask_sessions(ck), False

        pk = find_pass_key(user_text) or prof.get("pass_key") or infer_pass_from_course(extract_course_key(user_text) or prof.get("course"))
        n = find_sessions_count(user_text) or prof.get("sessions")
        if pk and n:
            out = answer_pass_price(pk, int(n))
            if out:
                return out, False
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
    # sinon => Gemini
=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    return None, False

# ==============================================================================
<<<<<<< HEAD
# 10) Gemini — uniquement orientation / qualification (sans chiffres inventés)
=======
# GEMINI fallback (optionnel)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
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

<<<<<<< HEAD
# Instructions système (humain + anti hallucination)
SYSTEM_PROMPT = f"""
Tu es Sarah (SVB). Tu réponds comme une vraie personne (naturel, simple, pas robot).
Tu NE dis JAMAIS que tu es un bot/IA.
=======
SYSTEM_PROMPT = """
Tu fais partie de l’équipe SVB.
Tu ne dis jamais “Bienvenue…”.
Tu n’inventes aucun prix/horaires/règles.
Tu finis toujours avec une phrase complète.
""".strip()
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
RÈGLE ABSOLUE ANTI-ERREUR :
- Tu n’inventes jamais un prix, un montant, une règle, un délai, une pénalité.
- Si la question implique un chiffre/règle que tu n’as pas dans FACTS, tu réponds :
  "Je préfère confirmer avec l’équipe" + [HUMAN_ALERT].
=======
def sanitize_llm(text: str) -> str:
    t = (text or "").strip()
    t2 = norm2(t)
    if t2.startswith("bienvenue") or ("bienvenue" in t2[:40] and t2.startswith("hello")):
        t = re.sub(r"(?i)^.*?(\?\s*)", "", t).strip()
    return safe_finalize(t)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
STYLE :
- Pas de présentation répétée.
- Court, clair.
- 0 à 2 questions de qualification max, seulement si nécessaire.
- Pas de "Bienvenue chez SVB" à chaque message.

FACTS AUTORISÉS (uniquement ceux-là) :
- Prix à l’unité : Training {eur(UNIT_PRICE['training'])} ; Machine {eur(UNIT_PRICE['machine'])}
- Essai : {eur(TRIAL['price'])} (remboursé si inscription)
- Starter : {eur(STARTER['price'])} / {STARTER['sessions']} sessions / 1 mois ; règle = {STARTER['discipline_rule']}
- Séance supp abonné : au prorata du pass (prix du pass / nombre de sessions)
- Inscription : paiement en ligne -> mail auto identifiants -> app (SVB/Sportigo) -> entrer identifiants -> réserver

Ce que tu peux faire avec Gemini :
- Reformuler, rassurer, orienter.
- Poser des questions (objectif, niveau, préférence machine/training, studio).
- Proposer un essai ou Starter.
- Si besoin humain => [HUMAN_ALERT]
"""

def build_gemini_contents(history: List[Dict[str, str]], user_text: str) -> List[Dict[str, Any]]:
    """
    Construit le payload Gemini sous forme de 'contents'.
    On garde un historique court.
    """
    max_turns = 16
    trimmed = history[-max_turns:]

    contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]

    for msg in trimmed:
=======
def call_gemini(api_key: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    model = get_model(api_key)
    contents: List[Dict[str, Any]] = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for msg in history[-18:]:
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
<<<<<<< HEAD

    # dernier user_text déjà dans history côté UI, mais on le remet si besoin:
    # (on évite double injection; ici on fait confiance à l'historique affiché)
    return contents
=======
    resp = model.generate_content(contents, generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 220})
    txt = sanitize_llm(resp.text or "")
    if not txt:
        txt = "Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ? 🙂"
    return txt, ("whatsapp" in norm2(txt))
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

<<<<<<< HEAD
def gemini_answer(api_key: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    """
    Appelle Gemini.
    Retourne (text, needs_whatsapp)
    """
    model = get_model(api_key)
    contents = build_gemini_contents(history, "")

    resp = model.generate_content(
        contents,
        generation_config={
            "temperature": 0.35,
            "top_p": 0.9,
            "max_output_tokens": 420,
        },
    )
    text = (resp.text or "").strip()
    needs_whatsapp = False

    if "[HUMAN_ALERT]" in text:
        needs_whatsapp = True
        text = text.replace("[HUMAN_ALERT]", "").strip()

    # fallback si vide
    if not text:
        text = "Vous cherchez plutôt une séance Machine (Reformer/Crossformer) ou un cours Training (Cross/Boxe/Yoga) ?"

    return text, needs_whatsapp

=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ==============================================================================
<<<<<<< HEAD
# 11) "Humain" : ne pas se présenter sans arrêt
=======
# UI
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
# ==============================================================================
<<<<<<< HEAD

def first_message() -> str:
    # Accueil 1 seule fois, naturel
    variants = [
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ce que tu veux travailler (tonus, perte de poids, mobilité…) et je te guide.",
        "OK, raconte-moi ce que tu recherches et je te propose la meilleure option.",
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
# 12) UI — Affichage historique
# ==============================================================================
=======
with st.sidebar:
    st.markdown("### SVB • Infos")
    st.caption(f"WhatsApp : {CONTACT['phone']}")
    st.caption(f"Email : {CONTACT['email']}")
    st.caption(f"Instagram : {CONTACT['instagram']}")

>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

<<<<<<< HEAD
# ==============================================================================
# 13) Chat loop
# ==============================================================================
=======
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
api_key = get_api_key()
prompt = st.chat_input("Posez votre question...")

if prompt:
<<<<<<< HEAD
    # user message
=======
    update_profile(prompt)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

<<<<<<< HEAD
    # 1) déterministe d'abord
    det_answer, needs_whatsapp = deterministic_router(prompt)
=======
    det, needs_wa = deterministic_router(prompt)
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7

    if det_answer is not None:
        # option: ack humain léger parfois, sans spammer
        # On évite d'ajouter un "OK" si réponse déjà courte
        response_text = det_answer
        with st.chat_message("assistant"):
<<<<<<< HEAD
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            if needs_whatsapp:
                st.markdown("---")
                st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)

=======
            st.markdown(det)
        st.session_state.messages.append({"role": "assistant", "content": det})
        if needs_wa:
            wa_button()
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
    else:
<<<<<<< HEAD
        # 2) Gemini (orientation) — si pas de clé, on escalade humain plutôt que dire n'importe quoi
        if not api_key:
            response_text = human_alert_answer("Je peux vous répondre, mais je préfère vous mettre avec l’équipe pour aller vite.")
=======
        if not GEMINI_AVAILABLE or not api_key:
            txt = safe_finalize("Dis-moi juste : quel cours + combien de sessions (2/4/6/8/10/12) et je te calcule 🙂")
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
            with st.chat_message("assistant"):
<<<<<<< HEAD
                st.markdown(response_text.replace("[HUMAN_ALERT]", ""))
                st.session_state.messages.append({"role": "assistant", "content": response_text.replace("[HUMAN_ALERT]", "")})
                st.markdown("---")
                st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)
=======
                st.markdown(txt)
            st.session_state.messages.append({"role": "assistant", "content": txt})
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("..."):
<<<<<<< HEAD
                        text, needs_whatsapp = gemini_answer(api_key, st.session_state.messages)

                    st.markdown(text)
                    st.session_state.messages.append({"role": "assistant", "content": text})

                    if needs_whatsapp:
                        st.markdown("---")
                        st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)

            except Exception as e:
=======
                        txt, needs_wa2 = call_gemini(api_key, st.session_state.messages)
                    st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
                if needs_wa2:
                    wa_button()
            except Exception:
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
                log.exception("Erreur Gemini")
<<<<<<< HEAD
                # En cas d'erreur, on ne sort pas une réponse hasardeuse.
                fallback = human_alert_answer("Petit souci technique. Le plus simple : on vous répond sur WhatsApp.")
=======
                txt = safe_finalize("Petit souci technique. Le plus simple : WhatsApp 🙂")
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7
                with st.chat_message("assistant"):
<<<<<<< HEAD
                    st.markdown(fallback.replace("[HUMAN_ALERT]", ""))
                    st.session_state.messages.append({"role": "assistant", "content": fallback.replace("[HUMAN_ALERT]", "")})
                    st.markdown("---")
                    st.link_button(WHATSAPP_LABEL, WHATSAPP_URL)

# ==============================================================================
# FIN
# ==============================================================================
=======
                    st.markdown(txt)
                st.session_state.messages.append({"role": "assistant", "content": txt})
                wa_button()
>>>>>>> e661a8d807f355a6d104129dc5bbc11ae28bade7