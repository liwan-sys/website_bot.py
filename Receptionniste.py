# Receptionniste.py
from __future__ import annotations

import os
import re
import random
import logging
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ------------------------------------------------------------------------------
# 0) CHARGEMENT ROBUSTE DE knowledge.py (évite les ImportError)
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
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ------------------------------------------------------------------------------
# 2) PAGE CONFIG + CSS
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');
.stApp{background:linear-gradient(180deg,#F9F7F2 0%,#E6F0E6 100%);font-family:'Lato',sans-serif;color:#4A4A4A;}
#MainMenu, footer, header {visibility:hidden;}
h1{font-family:'Dancing Script',cursive;color:#8FB592;text-align:center;font-size:3.4rem !important;margin-bottom:0px !important;text-shadow:2px 2px 4px rgba(0,0,0,0.10);}
.subtitle{text-align:center;color:#EBC6A6;font-size:1.0rem;font-weight:700;margin-bottom:18px;text-transform:uppercase;letter-spacing:2px;}
.stChatMessage{background-color:rgba(255,255,255,0.95)!important;border:1px solid #EBC6A6;border-radius:15px;padding:14px;box-shadow:0 4px 6px rgba(0,0,0,0.05);color:#1f1f1f !important;}
.stChatMessage p,.stChatMessage li{color:#1f1f1f !important;line-height:1.6;}
.stButton button{background:linear-gradient(90deg,#25D366 0%,#128C7E 100%);color:white !important;border:none;border-radius:25px;padding:12px 25px;font-weight:800;width:100%;text-transform:uppercase;}
.stButton button:hover{transform: scale(1.02);}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

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
def find_sessions_count(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm2(text))
    return int(m.group(1)) if m else None

def intent_sessions_only(text: str) -> bool:
    return re.match(r"^\s*(2|4|6|8|10|12)\s*(seance|seances|séance|séances|session|sessions)?\s*$", text.strip(), re.I) is not None

def find_pass_key(text: str) -> Optional[str]:
    t = norm2(text)
    patterns = [
        ("full former","full_former"), ("fullformer","full_former"),
        ("pass full","full"), ("pass focus","focus"), ("pass cross","cross"),
        ("crossformer","crossformer"), ("reformer","reformer"),
        ("kids","kids"), ("enfant","kids"),
        ("full","full"), ("focus","focus"), ("cross","cross")
    ]
    for needle, key in patterns:
        if needle in t:
            return key
    return None

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

# ==============================================================================
# STATE (mémoire courte)
# ==============================================================================
def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "did_greet" not in st.session_state:
        st.session_state.did_greet = False
    if "profile" not in st.session_state:
        st.session_state.profile = {"course": None, "pass_key": None, "sessions": None}

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

def first_message() -> str:
    return random.choice([
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif (tonus, cardio, dos, mobilité…) et je te guide.",
    ])

ensure_state()
if not st.session_state.did_greet and len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": first_message()})
    st.session_state.did_greet = True

# ==============================================================================
# INTENTS
# ==============================================================================
def intent_price(text: str) -> bool:
    return has_any(text, ["tarif","prix","combien","coute","coûte","abonnement","forfait","mensuel","mois"])

def intent_unit_price(text: str) -> bool:
    return has_any(text, ["a l'unite","à l'unité","sans abonnement","sans abo","unité","unite"])

def intent_definition(text: str) -> bool:
    return has_any(text, ["c'est quoi","c quoi","definition","définition","explique","différence","difference"])

def intent_signup(text: str) -> bool:
    return has_any(text, ["m'inscrire","inscription","creer un compte","créer un compte","identifiant","connexion","appli","application","sportigo"])

# ==============================================================================
# RÉPONSES
# ==============================================================================
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

def answer_definition(text: str) -> Optional[str]:
    ck = extract_course_key(text)
    if ck and ck in DEFINITIONS:
        return safe_finalize(DEFINITIONS[ck])
    return None

def answer_unit_price(text: str) -> str:
    ck = extract_course_key(text)
    if ck in ("reformer","crossformer"):
        return safe_finalize(f"Sans abonnement, une séance **Machine** est à **{eur(UNIT_PRICE['machine'])}**.")
    return safe_finalize(f"Sans abonnement, une séance **Training / cours** est à **{eur(UNIT_PRICE['training'])}**.")

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
        f"- Prix / séance : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
        f"- Studio : {studio_txt}"
        f"{extra}"
    )

def answer_ask_sessions(ck: str) -> str:
    if ck in ("reformer","crossformer"):
        return safe_finalize("Tu veux **à l’unité** ou en abonnement : **2/4/6/8/10/12 sessions** par mois ?")
    return safe_finalize("Tu veux combien de sessions par mois : **2/4/6/8/10/12** ?")

def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
    prof = st.session_state.profile

    if intent_signup(user_text):
        return answer_signup(), True

    if intent_definition(user_text):
        d = answer_definition(user_text)
        if d:
            return d, False

    # ✅ réponse courte “4 session”
    if intent_sessions_only(user_text):
        n = find_sessions_count(user_text) or prof.get("sessions")
        pk = prof.get("pass_key") or infer_pass_from_course(prof.get("course"))
        if pk and n:
            out = answer_pass_price(pk, int(n))
            if out:
                return out, False
        return safe_finalize("OK 🙂 Tu parles de quel pass ? (Cross / Focus / Full / Reformer / Crossformer / Full Former)"), False

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

    return None, False

# ==============================================================================
# GEMINI fallback (optionnel)
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
Tu fais partie de l’équipe SVB.
Tu ne dis jamais “Bienvenue…”.
Tu n’inventes aucun prix/horaires/règles.
Tu finis toujours avec une phrase complète.
""".strip()

def sanitize_llm(text: str) -> str:
    t = (text or "").strip()
    t2 = norm2(t)
    if t2.startswith("bienvenue") or ("bienvenue" in t2[:40] and t2.startswith("hello")):
        t = re.sub(r"(?i)^.*?(\?\s*)", "", t).strip()
    return safe_finalize(t)

def call_gemini(api_key: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    model = get_model(api_key)
    contents: List[Dict[str, Any]] = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for msg in history[-18:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    resp = model.generate_content(contents, generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 220})
    txt = sanitize_llm(resp.text or "")
    if not txt:
        txt = "Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ? 🙂"
    return txt, ("whatsapp" in norm2(txt))

# ==============================================================================
# UI
# ==============================================================================
with st.sidebar:
    st.markdown("### SVB • Infos")
    st.caption(f"WhatsApp : {CONTACT['phone']}")
    st.caption(f"Email : {CONTACT['email']}")
    st.caption(f"Instagram : {CONTACT['instagram']}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

api_key = get_api_key()
prompt = st.chat_input("Posez votre question...")

if prompt:
    update_profile(prompt)
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
            txt = safe_finalize("Dis-moi juste : quel cours + combien de sessions (2/4/6/8/10/12) et je te calcule 🙂")
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