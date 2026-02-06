# receptionniste.py
# =============================================================================
# SARAH — SVB CHATBOT (Streamlit)
# - Deterministic (prix/règles/planning/définitions) via knowledge.py
# - Gemini seulement pour le ton/orientation (sans chiffres/horaires)
# =============================================================================

import os
import re
import random
import logging
from typing import Dict, List, Optional, Tuple

import streamlit as st
import knowledge as kb

# Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH_APP")

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

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
  font-size:3.2rem !important;
  margin-bottom:0 !important;
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
.stChatMessage p,.stChatMessage li{ color:#1f1f1f !important; line-height:1.6; }
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
.smallhint{ color:#6b6b6b; font-size:0.92rem; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------
def get_api_key() -> Optional[str]:
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY")

def needs_human_button(text: str) -> bool:
    # simple flag
    return "[HUMAN_ALERT]" in text

def strip_human_flag(text: str) -> str:
    return text.replace("[HUMAN_ALERT]", "").strip()

def human_alert(msg: str = "Je te mets avec l’équipe pour être sûr à 100%.") -> str:
    return f"{msg}\n\n[HUMAN_ALERT]"

def show_whatsapp():
    st.markdown("---")
    st.link_button(kb.CONTACT["phone"], kb.CONTACT["whatsapp_url"])
    st.caption("Ou écris-nous directement sur WhatsApp.")

def smart_greeting() -> str:
    options = [
        "Salut 🙂 Tu cherches plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif (tonus, cardio, mobilité…) et je te guide.",
        "OK 🙂 Tu veux venir tester plutôt aux Docks ou aux Lavandières ?",
    ]
    return random.choice(options)

def norm(s: str) -> str:
    return kb.norm(s)

# -----------------------------------------------------------------------------
# Intent detection (simple + robuste)
# -----------------------------------------------------------------------------
def is_human_request(t: str) -> bool:
    t = norm(t)
    triggers = [
        "humain", "conseiller", "equipe", "équipe", "whatsapp",
        "appeler", "telephone", "téléphone", "contact", "joindre",
    ]
    return any(x in t for x in triggers)

def is_signup(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["m'inscrire", "inscription", "s'inscrire", "abonnement", "abonner", "creer un compte", "créer un compte", "identifiant", "mot de passe"])

def is_planning(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["planning", "horaire", "horaires", "quel jour", "quelle heure", "c'est quand", "c est quand", "quand est-ce", "quand est ce"])

def is_definition(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["c'est quoi", "c est quoi", "ça veut dire", "ca veut dire", "explique", "definition", "définition"])

def is_price_unit(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["prix", "tarif", "combien", "coute", "coûte", "a l'unite", "à l'unité", "unite", "sans abonnement", "sans abo"])

def is_pass_price(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["pass", "forfait", "abonnement", "mensuel", "par mois"])

def is_rules(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["annulation", "annuler", "report", "retard", "chaussette", "resiliation", "résiliation", "preavis", "préavis", "reglement", "règlement"])

def is_extra_session(t: str) -> bool:
    t = norm(t)
    return any(x in t for x in ["seance supp", "séance supp", "seance supplementaire", "séance supplémentaire", "rajouter", "ajouter une seance", "ajouter une séance", "seance en plus", "séance en plus"])

# -----------------------------------------------------------------------------
# Parsing helpers (pass / sessions / discipline)
# -----------------------------------------------------------------------------
PASS_ALIASES = [
    ("full former", "full_former"),
    ("fullformer", "full_former"),
    ("crossformer", "crossformer"),
    ("reformer", "reformer"),
    ("pass cross", "cross"),
    ("cross", "cross"),
    ("pass focus", "focus"),
    ("focus", "focus"),
    ("pass full", "full"),
    ("full", "full"),
    ("kids", "kids"),
    ("enfant", "kids"),
]

def find_pass_key(text: str) -> Optional[str]:
    t = norm(text)
    for needle, key in PASS_ALIASES:
        if needle in t:
            return key
    # coaching
    if "good vibes" in t or "goodvibes" in t:
        return "coaching_good_vibes"
    if "duo" in t and ("coaching" in t or "coach" in t):
        return "coaching_duo"
    return None

def find_sessions(text: str) -> Optional[int]:
    m = re.search(r"\b(2|4|6|8|10|12)\b", norm(text))
    return int(m.group(1)) if m else None

def find_discipline_query(text: str) -> Optional[str]:
    t = norm(text)
    # map common user requests
    keys = [
        "reformer", "crossformer", "cross-former", "cross former",
        "boxe", "cross training", "cross core", "cross body", "cross rox",
        "yoga vinyasa", "hatha flow", "power pilates", "classic pilates",
        "core & stretch", "cross yoga", "hyrox", "afrodance", "kids", "training kids"
    ]
    for k in keys:
        if k in t:
            # normalize to match planning labels
            return k.replace("cross-former", "cross former")
    return None

def find_studio_key(text: str) -> Optional[str]:
    t = norm(text)
    if "dock" in t:
        return "docks"
    if "lavand" in t:
        return "lavandieres"
    return None

# -----------------------------------------------------------------------------
# Deterministic answers
# -----------------------------------------------------------------------------
def answer_signup() -> str:
    return (
        "Pour t’inscrire :\n\n"
        "1) Tu souscris ton abonnement en ligne.\n"
        "2) Après paiement, tu reçois un e-mail automatique avec tes identifiants.\n"
        "3) Tu télécharges l’application (SVB / Sportigo).\n"
        "4) Tu rentres les identifiants reçus.\n"
        "5) Tu réserves ensuite tes séances sur le planning ✅\n\n"
        "Si tu ne reçois pas l’e-mail (spam / délai), écris-nous sur WhatsApp."
    )

def answer_unit_price_for_discipline(text: str) -> str:
    t = norm(text)
    # machine vs training
    if "reformer" in t or "crossformer" in t or "machine" in t:
        return f"À l’unité (sans abonnement), une séance **Machine** est à **{kb.eur(kb.UNIT_PRICE['machine'])}**."
    # boxe/cross/yoga etc
    return f"À l’unité (sans abonnement), un cours **Training** (ex: boxe/cross…) est à **{kb.eur(kb.UNIT_PRICE['training'])}**."

def answer_boxe_price() -> str:
    return (
        f"Pour la **Boxe** :\n"
        f"- À l’unité (sans abonnement) : **{kb.eur(kb.UNIT_PRICE['training'])}**\n"
        f"- En abonnement, ça passe via **Pass Focus** (ou **Pass Full** si tu veux mixer Cross + Focus).\n"
        f"Si tu me dis **2/4/6/8/10/12 sessions**, je te donne le total + le prix par séance."
    )

def answer_pass_price(text: str) -> Optional[str]:
    pk = find_pass_key(text)
    s = find_sessions(text)
    if not pk or not s:
        return None
    total = kb.get_pass_price(pk, s)
    if total is None:
        return None
    per = kb.price_per_session(pk, s)
    cfg = kb.get_pass(pk)
    if not cfg:
        return None

    lines = [
        f"📌 **{cfg.label}** — {s} sessions/mois",
        f"- Total : **{kb.eur(total)}**",
    ]
    if per is not None:
        lines.append(f"- Prix / séance (calcul) : **{kb.eur(per)}**")
    lines += [
        f"- Durée : {cfg.duration_min} min",
        f"- Studio : {cfg.studio_hint}",
        f"- Inclus : {cfg.includes}",
    ]
    return "\n".join(lines)

def answer_extra_session(text: str) -> str:
    pk = find_pass_key(text)
    s = find_sessions(text)
    if not pk or not s:
        return (
            "Pour que je calcule exactement, dis-moi :\n"
            "- ton **pass** (Cross / Focus / Full / Reformer / Crossformer / Full Former / Kids)\n"
            "- et le format **2/4/6/8/10/12**.\n\n"
            "Exemple : *Pass Cross 4* → prix séance = (prix du pass / 4)."
        )
    cfg = kb.get_pass(pk)
    if not cfg:
        return human_alert("Je n’ai pas reconnu ta formule exacte. Je te mets avec l’équipe.")
    price = kb.extra_session_price_for_member(pk, s)
    if price is None:
        return human_alert("Je préfère confirmer avec l’équipe pour éviter une erreur.")
    if cfg.category == "kids":
        return (
            f"Pour **Kids** : la séance supplémentaire est à **{kb.eur(kb.KIDS_EXTRA_SESSION)}**.\n"
            f"(Frais de dossier : {kb.eur(kb.KIDS_FILE_FEE)} • Engagement : {kb.KIDS_COMMITMENT})"
        )
    total = kb.get_pass_price(pk, s) or 0.0
    return (
        "Séance supplémentaire (abonné) = **au prorata de ton pass** :\n"
        f"- Formule : **{cfg.label} {s}**\n"
        f"- Calcul : {kb.eur(total)} / {s} = **{kb.eur(price)}**"
    )

def answer_definition(text: str) -> Optional[str]:
    t = norm(text)
    # try match key
    for key in kb.DEFINITIONS.keys():
        if key in t:
            return kb.DEFINITIONS[key]
    # some synonyms
    if "cross former" in t or "cross-former" in t:
        return kb.DEFINITIONS.get("crossformer")
    if "pilate" in t and "reformer" in t:
        return kb.DEFINITIONS.get("reformer")
    return None

def answer_rules(text: str) -> Optional[str]:
    t = norm(text)
    if "annul" in t:
        return (
            f"• Small group : {kb.RULES['cancel_small_group']}\n"
            f"• Coaching privé : {kb.RULES['cancel_private']}"
        )
    if "report" in t or "credit" in t:
        return kb.RULES["credits"]
    if "retard" in t:
        return kb.RULES["late_policy"]
    if "chaussette" in t:
        return kb.RULES["socks"]
    if "resili" in t or "preavis" in t:
        return kb.RULES["resiliation"]
    if "reglement" in t:
        return (
            f"- {kb.RULES['booking']}\n"
            f"- {kb.RULES['credits']}\n"
            f"- {kb.RULES['cancel_small_group']}\n"
            f"- {kb.RULES['cancel_private']}\n"
            f"- {kb.RULES['late_policy']}\n"
            f"- {kb.RULES['socks']}"
        )
    return None

def answer_planning(text: str) -> str:
    discipline = find_discipline_query(text)
    studio_key = find_studio_key(text)

    if not discipline:
        # If user asks just "planning" or "horaires"
        return (
            "Tu cherches le planning de quel studio ?\n"
            "- **Parc des Docks** (Cross/Boxe/Danse/Kids)\n"
            "- **Cours Lavandières** (Reformer/Crossformer/Yoga/Pilates)\n\n"
            "Dis-moi aussi la discipline (ex: **Reformer**, **Crossformer**, **Boxe**…)."
        )

    found = kb.find_schedule(discipline, studio_key=studio_key)
    formatted = kb.format_schedule(found)

    if not formatted:
        # if discipline known but not found => maybe synonym
        if discipline in ["cross former", "cross-former"]:
            found = kb.find_schedule("cross-former", studio_key=studio_key)
            formatted = kb.format_schedule(found)
        if not formatted:
            return human_alert("Je préfère confirmer avec l’équipe pour être sûre des horaires.")
    return f"Voici les créneaux **{discipline.title()}** :\n\n{formatted}"

def answer_contact() -> str:
    return (
        f"📍 **{kb.STUDIOS['docks']['name']}** — {kb.STUDIOS['docks']['address']}\n"
        f"📍 **{kb.STUDIOS['lavandieres']['name']}** — {kb.STUDIOS['lavandieres']['address']}\n\n"
        f"WhatsApp : {kb.CONTACT['phone']} • Insta : {kb.CONTACT['instagram']} • Mail : {kb.CONTACT['email']}"
    )

def deterministic_router(user_text: str) -> Tuple[Optional[str], bool]:
    t = user_text or ""

    # 1) humain
    if is_human_request(t):
        return human_alert("OK 🙂 Je te mets avec l’équipe."), True

    # 2) inscription
    if is_signup(t):
        return answer_signup(), False

    # 3) définitions
    if is_definition(t):
        d = answer_definition(t)
        if d:
            return d, False

    # 4) planning / horaires
    if is_planning(t):
        return answer_planning(t), False

    # 5) règles
    if is_rules(t):
        r = answer_rules(t)
        if r:
            return r, False

    # 6) séance supp (prorata)
    if is_extra_session(t):
        return answer_extra_session(t), False

    # 7) prix boxe (question fréquente)
    if "boxe" in norm(t) and is_price_unit(t):
        return answer_boxe_price(), False

    # 8) prix d’un pass si pass + sessions
    if is_pass_price(t):
        pp = answer_pass_price(t)
        if pp:
            return pp, False

    # 9) prix unité
    if is_price_unit(t):
        # si on détecte machine/training via texte
        return answer_unit_price_for_discipline(t), False

    # 10) contact / adresses
    if any(x in norm(t) for x in ["adresse", "ou", "où", "localisation", "contact", "instagram", "mail"]):
        return answer_contact(), False

    return None, False

# -----------------------------------------------------------------------------
# Gemini (ton humain seulement)
# -----------------------------------------------------------------------------
def gemini_safe_prompt() -> str:
    # IMPORTANT: Gemini n’a pas le droit de donner chiffres/prix/horaires.
    # Les réponses factuelles sont gérées par Python.
    return (
        "Tu es Sarah (SVB). Tu réponds comme une vraie personne, naturel, court.\n"
        "Tu NE dis jamais que tu es une IA.\n\n"
        "RÈGLES:\n"
        "- Tu ne donnes AUCUN prix, aucun montant, aucun horaire, aucun chiffre.\n"
        "- Si on te demande un prix/horaire, tu poses une question simple (objectif / studio / discipline) "
        "et tu invites à regarder le planning dans l’app.\n"
        "- Si c’est trop spécifique, tu proposes WhatsApp.\n\n"
        "Objectif: aider la personne à choisir (Machines vs Training), proposer essai/Starter, et orienter."
    )

def gemini_output_guard(text: str) -> str:
    # On bloque si Gemini sort des € / horaires
    if not text:
        return ""
    if "€" in text:
        return ""
    if re.search(r"\b\d{1,2}\s*h\b|\b\d{1,2}h\d{2}\b|\b\d{1,2}:\d{2}\b", text.lower()):
        return ""
    return text.strip()

def call_gemini(history: List[Dict[str, str]], api_key: str) -> str:
    if not GEMINI_AVAILABLE or not api_key:
        return ""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # petite mémoire (dernier échanges)
    trimmed = history[-14:]
    sys = gemini_safe_prompt()

    # On envoie en mode simple: system + historique + dernier message user
    # (Streamlit history inclut déjà le dernier user)
    convo = sys + "\n\n"
    for msg in trimmed:
        role = "CLIENT" if msg["role"] == "user" else "SARAH"
        convo += f"{role}: {msg['content']}\n"

    resp = model.generate_content(
        convo,
        generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 220},
    )
    return (resp.text or "").strip()

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": smart_greeting()}]

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input
prompt = st.chat_input("Posez votre question…")
api_key = get_api_key()

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Deterministic first
    det, want_whatsapp = deterministic_router(prompt)

    if det is not None:
        with st.chat_message("assistant"):
            st.markdown(strip_human_flag(det))
        st.session_state.messages.append({"role": "assistant", "content": strip_human_flag(det)})

        if wants := needs_human_button(det) or want_whatsapp:
            show_whatsapp()

    else:
        # Gemini fallback: ton/orientation
        if not api_key or not GEMINI_AVAILABLE:
            msg = human_alert("Je te réponds plus vite sur WhatsApp 🙂")
            with st.chat_message("assistant"):
                st.markdown(strip_human_flag(msg))
            st.session_state.messages.append({"role": "assistant", "content": strip_human_flag(msg)})
            show_whatsapp()
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        out = call_gemini(st.session_state.messages, api_key)
                        out = gemini_output_guard(out)

                        if not out:
                            out = "Tu veux plutôt **Machines** (Reformer/Crossformer) ou **Training** (Cross/Boxe/Yoga) ?"

                        st.markdown(out)

                st.session_state.messages.append({"role": "assistant", "content": out})

            except Exception:
                msg = human_alert("Petit souci technique. Le plus simple : WhatsApp 🙂")
                with st.chat_message("assistant"):
                    st.markdown(strip_human_flag(msg))
                st.session_state.messages.append({"role": "assistant", "content": strip_human_flag(msg)})
                show_whatsapp()
