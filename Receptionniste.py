import os
import re
import json
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

import streamlit as st

# ==============================================================================
# 0) LOGGING (pour debug prod)
# ==============================================================================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ==============================================================================
# 1) DEPENDANCES IA
# ==============================================================================
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR : Installe 'google-generativeai' : pip install google-generativeai")
    st.stop()

# ==============================================================================
# 2) CONFIG STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# ==============================================================================
# 3) CSS (ton style)
# ==============================================================================
st.markdown("""
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
  font-size:3.5rem !important;
  margin-bottom:0px !important;
  text-shadow:2px 2px 4px rgba(0,0,0,0.1);
}
.subtitle{
  text-align:center;
  color:#EBC6A6;
  font-size:1.1rem;
  font-weight:bold;
  margin-bottom:25px;
  text-transform:uppercase;
  letter-spacing:2px;
}

.stChatMessage{
  background-color:rgba(255,255,255,0.95) !important;
  border:1px solid #EBC6A6;
  border-radius:15px;
  padding:15px;
  box-shadow:0 4px 6px rgba(0,0,0,0.05);
  color:#1f1f1f !important;
}
.stChatMessage p, .stChatMessage li{
  color:#1f1f1f !important;
  line-height:1.6;
}
.stButton button{
  background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
  color:white !important;
  border:none;
  border-radius:25px;
  padding:12px 25px;
  font-weight:bold;
  width:100%;
  text-transform:uppercase;
}
.stButton button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4) SOURCE DE VERITE - TARIFS & REGLES (depuis studiosvb.com/tarifs + /faq)
# ==============================================================================
# NB: Ne mets JAMAIS "30€ séance supp" ici si ce n'est pas écrit quelque part.
# Ici on met ce qui est sur la page tarifs et FAQ (annulation, retard, report, etc.).
# Sources:
# - https://studiosvb.com/tarifs
# - https://studiosvb.com/faq

@dataclass(frozen=True)
class PassPrice:
    sessions: int
    price: float  # en euros

@dataclass(frozen=True)
class PassConfig:
    key: str
    label: str
    duration_min: int
    includes: str
    category: str  # machines / training / coaching / kids
    studio_hint: str  # Lavandières / Docks / Mixte
    prices: Dict[int, PassPrice]  # sessions->PassPrice

# --- Tarifs (copiés de la page Tarifs) ---
# Small Group Machines
PASS_CROSSFORMER = PassConfig(
    key="crossformer",
    label="Pass Crossformer",
    duration_min=50,
    includes="Crossformer",
    category="machines",
    studio_hint="Lavandières",
    prices={
        2: PassPrice(2, 78.30),
        4: PassPrice(4, 152.30),
        6: PassPrice(6, 222.30),
        8: PassPrice(8, 288.30),
        10: PassPrice(10, 350.30),
        12: PassPrice(12, 408.30),
    },
)

PASS_REFORMER = PassConfig(
    key="reformer",
    label="Pass Reformer",
    duration_min=50,
    includes="Pilates Reformer",
    category="machines",
    studio_hint="Lavandières",
    prices={
        2: PassPrice(2, 70.30),
        4: PassPrice(4, 136.30),
        6: PassPrice(6, 198.30),
        8: PassPrice(8, 256.30),
        10: PassPrice(10, 310.30),
        12: PassPrice(12, 360.30),
    },
)

PASS_FULL_FORMER = PassConfig(
    key="full_former",
    label="Pass Full Former",
    duration_min=50,
    includes="Reformer & Crossformer",
    category="machines",
    studio_hint="Lavandières",
    prices={
        2: PassPrice(2, 74.30),
        4: PassPrice(4, 144.30),
        6: PassPrice(6, 210.30),
        8: PassPrice(8, 272.30),
        10: PassPrice(10, 330.30),
        12: PassPrice(12, 384.30),
    },
)

# Small Group Training
PASS_CROSS = PassConfig(
    key="cross",
    label="Pass Cross",
    duration_min=55,
    includes="Cross Training • Hyrox • Core • Body • Cross Yoga",
    category="training",
    studio_hint="Docks",
    prices={
        2: PassPrice(2, 30.30),
        4: PassPrice(4, 60.30),
        6: PassPrice(6, 90.30),
        8: PassPrice(8, 116.30),
        10: PassPrice(10, 145.30),
        12: PassPrice(12, 168.30),
    },
)

PASS_FOCUS = PassConfig(
    key="focus",
    label="Pass Focus",
    duration_min=55,
    includes="Yoga • Pilates Sol • Boxe • Danse • Stretch",
    category="training",
    studio_hint="Mixte",
    prices={
        2: PassPrice(2, 36.30),
        4: PassPrice(4, 72.30),
        6: PassPrice(6, 105.30),
        8: PassPrice(8, 136.30),
        10: PassPrice(10, 165.30),
        12: PassPrice(12, 192.30),
    },
)

PASS_FULL = PassConfig(
    key="full",
    label="Pass Full (Cross + Focus)",
    duration_min=55,
    includes="Accès à tous les cours Cross & Focus",
    category="training",
    studio_hint="Mixte",
    prices={
        2: PassPrice(2, 40.30),
        4: PassPrice(4, 80.30),
        6: PassPrice(6, 115.30),
        8: PassPrice(8, 150.30),
        10: PassPrice(10, 180.30),
        12: PassPrice(12, 210.30),
    },
)

# Kids (Tarifs: sessions + "Session supp 18,30")
PASS_KIDS = PassConfig(
    key="kids",
    label="Pass Kids",
    duration_min=55,  # variable, on garde une valeur neutre
    includes="Yoga Kids • Training Kids",
    category="kids",
    studio_hint="Docks",
    prices={
        2: PassPrice(2, 35.30),
        4: PassPrice(4, 65.30),
    },
)

ALL_PASSES: Dict[str, PassConfig] = {
    p.key: p
    for p in [
        PASS_CROSSFORMER,
        PASS_REFORMER,
        PASS_FULL_FORMER,
        PASS_CROSS,
        PASS_FOCUS,
        PASS_FULL,
        PASS_KIDS,
    ]
}

# --- Règles (FAQ + Tarifs) ---
RULES = {
    "trial": {
        "amount": 30.00,
        "note_training": "Séance d'essai à 30€ (15€ remboursés si inscription) sur le Training.",
        "note_machines": "Essai à 30€ sur Machines.",
    },
    "fees": {
        "dossier": 49.00,  # Tarifs
        "kids_dossier": 29.00,
    },
    "commitment": {
        "starter": "Sans engagement (Pass Starter).",
        "monthly": "Engagement 3 mois (sur la page Tarifs).",
        "kids": "Engagement 4 mois.",
    },
    "report": "Les séances non utilisées ne sont pas reportables sur le mois suivant.",
    "cancel_policy": {
        "small_group": "Annulation gratuite jusqu'à 1h avant.",
        "private": "Annulation gratuite jusqu'à 24h avant.",
    },
    "late_policy": "Au-delà de 5 minutes de retard, l’accès au cours est refusé et la séance est décomptée.",
}

# ==============================================================================
# 5) POLITIQUE "SEANCE SUPPLEMENTAIRE" (CONFIGURABLE)
# ==============================================================================
# TU VEUX: si quelqu’un veut payer une séance en plus => on calcule au prorata du pass (prix / nb sessions).
# Donc on ne dira plus jamais "30€" par défaut.
EXTRA_SESSION_POLICY = {
    "mode": "pro_rata_of_member_pass",  # "fixed", "pro_rata_of_member_pass", "ask_team"
    "fixed_price": None,  # ex: 30.0 si un jour tu veux
    "kids_extra": 18.30,  # sur Tarifs: "Session Supp. 18,30"
}

# ==============================================================================
# 6) OUTILS CALCUL / FORMAT
# ==============================================================================
def eur(x: float) -> str:
    return f"{x:,.2f}€".replace(",", " ").replace(".", ",")

def unit_price(pass_key: str, sessions: int) -> Optional[float]:
    p = ALL_PASSES.get(pass_key)
    if not p:
        return None
    if sessions not in p.prices:
        return None
    price = p.prices[sessions].price
    return round(price / sessions, 2)

def find_pass_in_text(text: str) -> Optional[str]:
    t = text.lower()
    # match simple
    mapping = {
        "crossformer": ["crossformer", "cross former"],
        "reformer": ["reformer"],
        "full_former": ["full former", "fullformer"],
        "cross": ["pass cross", "cross "],
        "focus": ["pass focus", "focus "],
        "full": ["pass full", "full "],
        "kids": ["kids", "enfant", "enfants"],
    }
    for k, keys in mapping.items():
        if any(s in t for s in keys):
            return k
    return None

def find_sessions_count(text: str) -> Optional[int]:
    # cherche "4 séances", "8 sessions", "12 / mois" etc.
    m = re.search(r"\b(2|4|6|8|10|12)\b\s*(séances|sessions)?", text.lower())
    if m:
        return int(m.group(1))
    return None

def is_pricing_question(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in [
        "prix", "tarif", "coût", "combien", "abonnement", "pass", "séance", "session",
        "dossier", "engagement", "annulation", "report", "retard"
    ])

def wants_extra_session(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in ["séance supp", "séance supplémentaire", "session supp", "rajouter une séance", "ajouter une séance"])

# ==============================================================================
# 7) REPONSES DETERMINISTES (ZÉRO HALLUCINATION)
# ==============================================================================
def answer_rules_question(text: str) -> Optional[str]:
    t = text.lower()

    if "annul" in t:
        return (
            "✅ Annulation :\n"
            f"- Small Group : {RULES['cancel_policy']['small_group']}\n"
            f"- Coaching privé : {RULES['cancel_policy']['private']}\n"
            "Passé le délai, la séance est décomptée."
        )

    if "retard" in t:
        return f"⏰ Retard : {RULES['late_policy']}"

    if "report" in t or "cumul" in t:
        return f"📌 Report : {RULES['report']}"

    if "engagement" in t or "résili" in t or "resili" in t:
        return (
            "📌 Engagement / Résiliation :\n"
            f"- Pass Starter : {RULES['commitment']['starter']}\n"
            f"- Abonnements mensuels : {RULES['commitment']['monthly']}\n"
            f"- Pass Kids : {RULES['commitment']['kids']}\n"
            "Résiliation : par mail avec 1 mois de préavis (FAQ)."
        )

    if "frais" in t and ("dossier" in t or "inscription" in t):
        return (
            "📌 Frais de dossier :\n"
            f"- Abonnements (hors Kids) : {eur(RULES['fees']['dossier'])}\n"
            f"- Kids : {eur(RULES['fees']['kids_dossier'])}"
        )

    return None

def answer_pass_price(pass_key: str, sessions: int) -> Optional[str]:
    p = ALL_PASSES.get(pass_key)
    if not p:
        return None
    if sessions not in p.prices:
        return None
    total = p.prices[sessions].price
    u = unit_price(pass_key, sessions)
    return (
        f"📌 {p.label} — {sessions} sessions/mois\n"
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance (calcul) : **{eur(u)}**\n"
        f"- Durée : {p.duration_min} minutes\n"
        f"- Inclus : {p.includes}\n"
        f"- Studio : {p.studio_hint}"
    )

def answer_extra_session(text: str) -> str:
    """
    Règle anti-erreur : on ne donne pas un prix fixe inventé.
    On applique la policy.
    """
    pass_key = find_pass_in_text(text)
    sessions = find_sessions_count(text)

    # Kids : sur la page tarifs il y a "Session supp. 18,30"
    if pass_key == "kids":
        return f"👶 Pour le Kids : la **session supplémentaire** est à **{eur(EXTRA_SESSION_POLICY['kids_extra'])}**."

    mode = EXTRA_SESSION_POLICY["mode"]

    if mode == "fixed" and EXTRA_SESSION_POLICY["fixed_price"] is not None:
        return f"➕ Séance supplémentaire : **{eur(float(EXTRA_SESSION_POLICY['fixed_price']))}**."

    if mode == "pro_rata_of_member_pass":
        # On a besoin du pass + nb sessions pour calculer
        if not pass_key or not sessions:
            return (
                "➕ Pour calculer une **séance supplémentaire au prorata**, j’ai besoin de 2 infos :\n"
                "1) Votre pass (Cross / Focus / Full / Reformer / Crossformer / Full Former)\n"
                "2) Le nombre de sessions de votre forfait (2/4/6/8/10/12)\n\n"
                "Exemple : *Pass Cross 4 sessions* → prix séance = (60,30€ / 4)."
            )

        u = unit_price(pass_key, sessions)
        if u is None:
            return (
                "Je peux calculer au prorata, mais je n’ai pas reconnu le pass exact.\n"
                "Dites-moi : Cross / Focus / Full / Reformer / Crossformer / Full Former + 2/4/6/8/10/12."
            )

        p = ALL_PASSES[pass_key]
        return (
            "➕ Séance supplémentaire (calcul prorata de votre abonnement) :\n"
            f"- Votre formule : **{p.label} {sessions} sessions**\n"
            f"- Calcul : {eur(p.prices[sessions].price)} / {sessions} = **{eur(u)} par séance**\n\n"
            "Si vous me dites sur quel cours/studio vous voulez ajouter la séance, je vous guide sur la meilleure option."
        )

    # fallback
    return "Pour être sûr à 100%, je préfère vous mettre en relation avec l’équipe. [HUMAN_ALERT]"

def deterministic_answer(user_text: str) -> Optional[str]:
    # 1) règles
    r = answer_rules_question(user_text)
    if r:
        return r

    # 2) extra session
    if wants_extra_session(user_text):
        return answer_extra_session(user_text)

    # 3) prix pass
    pass_key = find_pass_in_text(user_text)
    sessions = find_sessions_count(user_text)
    if pass_key and sessions:
        pr = answer_pass_price(pass_key, sessions)
        if pr:
            return pr

    # 4) question générale prix séance ?
    if "prix" in user_text.lower() and "séance" in user_text.lower() and ("à l'unité" in user_text.lower() or "unité" in user_text.lower()):
        # IMPORTANT : le site ne donne pas explicitement "prix à l'unité" sur la page tarifs/faq que j’ai vues.
        # Donc on ne l’invente pas : on demande précision / ou WhatsApp.
        return (
            "Pour le **prix à l’unité**, je préfère vous confirmer selon le cours (Machines / Training / Coaching).\n"
            "Dites-moi : Reformer, Crossformer, Cross, Focus, Full, ou Coaching ?"
        )

    return None

# ==============================================================================
# 8) IA (UNIQUEMENT POUR ORIENTATION, PAS POUR TARIFS)
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
Tu es Sarah, l’assistante SVB (premium, claire, orientée conversion).

RÈGLE CRITIQUE ANTI-ERREUR :
- Tu n’inventes JAMAIS un prix, une règle, un engagement, une pénalité.
- Si une info tarifaire/règle n’est pas dans les "FACTS", tu dis : "Je préfère confirmer avec l’équipe" + [HUMAN_ALERT].

TON :
- Parle au nom de "l’équipe".
- Pose 1 à 3 questions max si nécessaire.
- Termine avec une action (essai / pass / WhatsApp).

FACTS (source site Tarifs + FAQ) :
{json.dumps({"passes": {k: {"label": v.label, "duration_min": v.duration_min, "includes": v.includes, "studio": v.studio_hint,
                            "prices": {s: v.prices[s].price for s in v.prices}}
                      for k, v in ALL_PASSES.items()},
            "rules": RULES,
            "extra_session_policy": EXTRA_SESSION_POLICY}, ensure_ascii=False, indent=2)}
"""

# ==============================================================================
# 9) UI
# ==============================================================================
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>VOTRE ASSISTANTE SVB</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡 Dites-moi votre objectif (remise en forme, perte de poids, renfo, mobilité) et je vous recommande la meilleure formule + le studio adapté."}
    ]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

api_key = get_api_key()
user_text = st.chat_input("Posez votre question...")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 1) déterministe si tarif/règle
    det = deterministic_answer(user_text)
    if det:
        with st.chat_message("assistant"):
            show_whatsapp = "[HUMAN_ALERT]" in det
            det_clean = det.replace("[HUMAN_ALERT]", "").strip()
            st.markdown(det_clean)
            st.session_state.messages.append({"role": "assistant", "content": det_clean})

            if show_whatsapp:
                st.markdown("---")
                st.link_button("📞 Contacter l'équipe (WhatsApp)", "https://wa.me/33744919155")
        st.stop()

    # 2) sinon IA (orientation)
    if not api_key:
        with st.chat_message("assistant"):
            st.warning("Clé API manquante (GOOGLE_API_KEY).")
        st.stop()

    try:
        model = get_model(api_key)

        # historique simple
        history = st.session_state.messages[-18:]
        contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        with st.chat_message("assistant"):
            with st.spinner("Sarah réfléchit..."):
                resp = model.generate_content(
                    contents,
                    generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 420}
                )
                text = (resp.text or "").strip()

                show_whatsapp = False
                if "[HUMAN_ALERT]" in text:
                    show_whatsapp = True
                    text = text.replace("[HUMAN_ALERT]", "").strip()

                if not text:
                    text = "Vous cherchez plutôt un format **Machines (Reformer/Crossformer)** ou **Training (Cross/Focus)** ?"

                st.markdown(text)
                st.session_state.messages.append({"role": "assistant", "content": text})

                if show_whatsapp:
                    st.markdown("---")
                    st.link_button("📞 Contacter l'équipe (WhatsApp)", "https://wa.me/33744919155")

    except Exception as e:
        log.exception("Erreur IA")
        with st.chat_message("assistant"):
            st.error("Erreur technique. Réessayez dans quelques secondes.")