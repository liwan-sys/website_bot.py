# -*- coding: utf-8 -*-
"""
receptionniste.py — Sarah (SVB) : UI Streamlit + routeur déterministe + fallback Gemini contrôlé.

Objectif :
- 95% déterministe (zéro erreur tarifs/planning).
- Gemini uniquement pour reformuler / poser 1-2 questions / humaniser (sans prix ni horaires).
"""

from __future__ import annotations

import os
import re
import random
import logging
from typing import Dict, List, Optional, Tuple

import streamlit as st

from knowledge import (
    CONTACT, STUDIOS,
    eur, norm2,
    UNIT_PRICE, TRIAL, STARTER, BOOST, FEES_AND_ENGAGEMENT, COACHING, KIDS,
    PASS, PARRAINAGE, RULES, DEFINITIONS,
    find_pass_key, find_sessions_count, extract_course_key, extract_day, extract_studio,
    pass_unit_price,
    slots_for, format_slots_grouped, tag_to_pass_hint,
)

# ------------------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("SVB_SARAH")

# ------------------------------------------------------------------------------
# GEMINI (OPTIONNEL)
# ------------------------------------------------------------------------------
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

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
Tu fais partie de l’équipe SVB. Tu écris comme une vraie personne (naturel, simple).
Tu NE dis JAMAIS que tu es une IA ou un bot.

RÈGLES ABSOLUES :
- Tu ne donnes AUCUN prix (pas de €), ni aucun tarif, ni aucun calcul.
- Tu ne donnes AUCUN horaire précis (pas de "10h15", pas de jours + heures).
- Tu poses 1 ou 2 questions maximum.
- Si tu n’es pas sûr : tu proposes WhatsApp.

But : aider à choisir (Machine vs Training), orienter vers le bon pass, ou demander le studio / objectif.
"""

PRICE_OR_TIME_REGEX = re.compile(r"(€|\b\d{1,2}h\d{0,2}\b)", re.IGNORECASE)

def ensure_clean_gemini(text: str) -> Tuple[str, bool]:
    """Si Gemini sort un prix/horaire, on bascule WhatsApp plutôt que risquer."""
    t = (text or "").strip()
    if not t:
        return "Tu veux plutôt **Machines** (Reformer/Crossformer) ou **Training** (Cross/Boxe/Yoga) ?", False

    if PRICE_OR_TIME_REGEX.search(t):
        return "Je préfère te confirmer ça avec l’équipe pour être sûre à 100% 🙂", True

    # évite l'effet "phrase coupée"
    if t[-1] not in ".!?…":
        t = t.rstrip() + " 🙂"
    return t, False

def build_history_text(history: List[Dict[str, str]], max_turns: int = 10) -> str:
    trimmed = history[-max_turns:]
    lines = []
    for msg in trimmed:
        who = "Client" if msg["role"] == "user" else "Sarah"
        content = msg["content"].strip()
        lines.append(f"{who}: {content}")
    return "\n".join(lines)

def call_gemini(api_key: str, history: List[Dict[str, str]], prompt: str) -> Tuple[str, bool]:
    model = get_model(api_key)
    hist = build_history_text(history, max_turns=12)
    full = f"{SYSTEM_PROMPT}\n\n{hist}\nClient: {prompt}\nSarah:"
    resp = model.generate_content(
        full,
        generation_config={"temperature": 0.35, "top_p": 0.9, "max_output_tokens": 220},
    )
    txt = (resp.text or "").strip()
    return ensure_clean_gemini(txt)

# ------------------------------------------------------------------------------
# PAGE CONFIG + CSS
# ------------------------------------------------------------------------------
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

st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SVB</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# HELPERS UI / STATE
# ------------------------------------------------------------------------------
ACKS = ["OK 🙂", "Parfait.", "Je vois.", "Bien sûr.", "Top.", "D’accord.", "Yes.", "Très bien."]

def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "did_greet" not in st.session_state:
        st.session_state.did_greet = False
    if "last_pass" not in st.session_state:
        st.session_state.last_pass = None  # ex: "focus"

def first_message() -> str:
    variants = [
        "Salut 🙂 Tu cherches plutôt **Machines** (Reformer/Crossformer) ou **Training** (Cross/Boxe/Yoga) ?",
        "Hello 🙂 Dis-moi ton objectif (tonus, cardio, mobilité…) et je te guide.",
        "OK 🙂 Tu veux plutôt réserver aux **Docks** ou aux **Lavandières** ?",
    ]
    return random.choice(variants)

ensure_state()
if not st.session_state.did_greet and len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": first_message()})
    st.session_state.did_greet = True

# ------------------------------------------------------------------------------
# SIDEBAR (infos)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### SVB • Infos")
    st.caption(f"WhatsApp : {CONTACT['phone']}")
    st.caption(f"Email : {CONTACT['email']}")
    st.caption(f"Instagram : {CONTACT['instagram']}")
    st.divider()
    st.markdown("### Debug")
    if st.checkbox("Afficher la formule mémorisée", value=False):
        st.info(f"last_pass = {st.session_state.last_pass}")

# ------------------------------------------------------------------------------
# INTENTS
# ------------------------------------------------------------------------------
def has_any(text: str, words: List[str]) -> bool:
    t = norm2(text)
    return any(w in t for w in words)

def intent_human(text: str) -> bool:
    return has_any(text, ["humain", "conseiller", "equipe", "équipe", "whatsapp", "appeler", "telephone", "téléphone", "contact"])

def intent_trial(text: str) -> bool:
    return has_any(text, ["essai", "seance d'essai", "séance d'essai", "tester", "découverte", "decouverte"])

def intent_starter(text: str) -> bool:
    return has_any(text, ["starter", "new pass starter", "99,90", "99.90"])

def intent_boost(text: str) -> bool:
    return has_any(text, ["boost", "option boost", "svb boost"])

def intent_parrainage(text: str) -> bool:
    return has_any(text, ["parrainage", "parrainer", "parraine", "parrain"])

def intent_rules(text: str) -> bool:
    return has_any(text, ["annulation", "annuler", "report", "reporter", "cumul", "cumulable",
                          "resiliation", "résiliation", "preavis", "préavis", "retard",
                          "chaussette", "chaussettes", "reglement", "règlement",
                          "suspension", "suspendre", "pause", "mettre en pause",
                          "engagement"])

def intent_pause(text: str) -> bool:
    return has_any(text, ["pause", "mettre en pause", "suspendre", "suspension"])

def intent_signup(text: str) -> bool:
    # IMPORTANT : on retire "abonnement" pour éviter les faux positifs (pause/résiliation)
    return has_any(text, ["m'inscrire", "inscrire", "inscription", "souscrire",
                          "creer un compte", "créer un compte", "identifiant", "identifiants",
                          "mot de passe", "connexion", "connecter", "application", "appli"])

def intent_unit_price(text: str) -> bool:
    return has_any(text, ["a l'unite", "à l'unité", "sans abonnement", "sans abo",
                          "prix d'une seance", "prix d’une seance", "prix seance",
                          "combien coute une seance", "combien ca coute", "tarif a l'unite"])

def intent_planning(text: str) -> bool:
    return has_any(text, ["planning", "horaire", "horaires", "quel jour", "quels jours",
                          "a quelle heure", "à quelle heure", "quand", "cours de", "séance de", "seance de"])

def intent_definition(text: str) -> bool:
    return has_any(text, ["c'est quoi", "c quoi", "ça veut dire", "definition", "définition", "explique", "difference", "différence"])

def intent_pass_info(text: str) -> bool:
    t = norm2(text)
    return ("pass" in t) and any(k in t for k in ["c'est quoi", "c quoi", "donne", "acces", "accès", "inclu", "comprend", "permet"])

def intent_pass_price(text: str) -> bool:
    return has_any(text, ["pass", "forfait", "tarif", "prix", "combien", "coute", "coûte"])

def intent_extra_session(text: str) -> bool:
    return has_any(text, ["seance supp", "séance supp", "seance supplementaire", "séance supplémentaire",
                          "ajouter une seance", "ajouter une séance", "rajouter", "seance en plus", "séance en plus"])

def intent_interest(text: str) -> bool:
    t = norm2(text)
    desire = any(k in t for k in ["je veux", "j'aimerais", "jaimerais", "je souhaite", "je cherche", "je voudrais", "commencer", "tester", "faire"])
    ck = extract_course_key(text)
    return desire and (ck is not None)

def intent_premium(text: str) -> bool:
    return has_any(text, ["premium", "plus premium", "version premium", "plus haut", "upgrade", "mieux", "plus complet"])

def intent_coaching(text: str) -> bool:
    return has_any(text, ["coaching", "coach", "individuel", "duo", "good vibes"])

def intent_kids(text: str) -> bool:
    return has_any(text, ["kids", "enfant", "enfants", "ado", "training kids", "yoga kids"])

# ------------------------------------------------------------------------------
# RÉPONSES DÉTERMINISTES
# ------------------------------------------------------------------------------
def human_alert(reason: str = "") -> Tuple[str, bool]:
    txt = reason.strip() if reason else "Je te mets directement avec l’équipe pour être sûre à 100% 🙂"
    return txt, True

def answer_signup() -> str:
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

def answer_rules(text: str) -> str:
    t = norm2(text)

    if any(k in t for k in ["pause", "mettre en pause", "suspendre", "suspension"]):
        return answer_pause()

    if "engagement" in t:
        return RULES["engagement"]

    if any(k in t for k in ["annuler", "annulation"]):
        return f"{RULES['cancel_small_group']}\n\n{RULES['cancel_private']}"
    if any(k in t for k in ["report", "reporter", "cumul", "cumulable"]):
        return RULES["no_carry_over"]
    if "retard" in t:
        return RULES["late_policy"]
    if any(k in t for k in ["chaussette", "chaussettes"]):
        return RULES["socks_lavandieres"]
    if any(k in t for k in ["resiliation", "résiliation"]):
        return RULES["resiliation"]

    return (
        "Règlement (résumé) :\n"
        f"- {RULES['cancel_small_group']}\n"
        f"- {RULES['cancel_private']}\n"
        f"- {RULES['no_carry_over']}\n"
        f"- {RULES['late_policy']}\n"
        f"- {RULES['socks_lavandieres']}\n"
        f"- {RULES['suspension']}\n"
        f"- {RULES['resiliation']}\n"
        f"- {RULES['engagement']}"
    )

def answer_pause() -> str:
    return (
        "Pour mettre en pause / suspendre :\n"
        f"- {RULES['suspension']}\n"
        f"- Avec **Boost** : suspension sans préavis ✅\n\n"
        "Si tu veux, dis-moi si tu as Boost + la durée d’absence, et je te guide."
    )

def answer_definition(text: str) -> Optional[str]:
    ck = extract_course_key(text)
    if ck and ck in DEFINITIONS:
        return DEFINITIONS[ck]

    # différence reformer vs crossformer
    t = norm2(text)
    if ("reformer" in t) and ("crossformer" in t or "cross-former" in t or "cross former" in t) and ("diff" in t):
        return (
            "Différence **Reformer vs Crossformer** :\n"
            "- **Reformer** : plus contrôlé, parfait posture/gainage/tonus.\n"
            "- **Crossformer** : plus **cardio / intense**, ça monte plus vite en rythme.\n"
            "Les deux sont adaptés débutants : le coach ajuste."
        )
    return None

def answer_unit_price(text: str) -> str:
    ck = extract_course_key(text)
    if ck in ("reformer", "crossformer"):
        return f"Sans abonnement, une séance **Machine** est à **{eur(UNIT_PRICE['machine'])}**."
    if ck:
        return f"Sans abonnement, une séance **Training / cours** est à **{eur(UNIT_PRICE['training'])}**."
    return (
        "Sans abonnement :\n"
        f"- Cours **Training** : **{eur(UNIT_PRICE['training'])}**\n"
        f"- Séance **Machine** : **{eur(UNIT_PRICE['machine'])}**\n\n"
        "Tu cherches plutôt une Machine (Reformer/Crossformer) ou un cours Training (Cross/Boxe/Yoga…) ?"
    )

def answer_coaching() -> str:
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

def answer_kids() -> str:
    return (
        f"Kids (hors juillet/août) — engagement **{FEES_AND_ENGAGEMENT['kids_engagement_months']} mois** :\n"
        f"- 2 séances/mois : **{eur(PASS['kids'].prices[2].total)}**\n"
        f"- 4 séances/mois : **{eur(PASS['kids'].prices[4].total)}**\n"
        f"- Séance supplémentaire : **{eur(KIDS['extra_session'])}**\n"
        f"- Frais de dossier : **{eur(FEES_AND_ENGAGEMENT['kids_registration_fee'])}**\n"
        f"📌 {KIDS['note']}"
    )

def answer_pass_price(pass_key: str, sessions: int) -> Optional[str]:
    p = PASS.get(pass_key)
    if not p or sessions not in p.prices:
        return None
    total = p.prices[sessions].total
    unit = pass_unit_price(pass_key, sessions)
    studio_label = STUDIOS.get(p.where, {"label": p.where}).get("label", p.where)

    extra = ""
    if pass_key == "kids":
        extra = f"\n- Séance supplémentaire kids : **{eur(KIDS['extra_session'])}**"
    elif p.category in ("training", "machine"):
        extra = f"\n- Engagement : **{FEES_AND_ENGAGEMENT['small_group_engagement_months']} mois**"

    return (
        f"📌 **{p.label}** — {sessions} sessions / mois\n"
        f"- Total : **{eur(total)}**\n"
        f"- Prix / séance (calcul) : **{eur(unit)}**\n"
        f"- Durée : {p.duration_min} min\n"
        f"- Studio : {studio_label}\n"
        f"{extra}"
    )

def answer_extra_session(text: str) -> str:
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
            "Exemple : *Pass Focus 4* → (prix du pass / 4)."
        )

    u = pass_unit_price(pk, n)
    if u is None:
        return "Je n’ai pas reconnu la formule exacte. Écris : Cross/Focus/Full/Reformer/Crossformer/Full Former + 2/4/6/8/10/12."

    p = PASS[pk]
    total = p.prices[n].total
    return (
        "✅ Séance supplémentaire (au prorata de ton abonnement) :\n"
        f"- Formule : **{p.label} {n}**\n"
        f"- Calcul : {eur(total)} / {n} = **{eur(u)}**"
    )

def answer_pass_info(pass_key: str) -> str:
    p = PASS.get(pass_key)
    if not p:
        return "Tu parles de quel pass : Cross, Focus, Full, Reformer, Crossformer ou Full Former ?"
    includes = "\n".join([f"- {x}" for x in p.includes])
    studio_label = STUDIOS.get(p.where, {"label": p.where}).get("label", p.where)

    note = ""
    if pass_key == "focus":
        note = "\n\n✅ Le **Pass Focus** ne donne pas accès au **Cross Training** (ça, c’est Pass Cross / Pass Full)."
    if pass_key == "cross":
        note = "\n\n✅ Le **Pass Cross** = les formats Cross (Training/Core/Body/Yoga…)."
    if pass_key in ("reformer", "crossformer"):
        note = "\n\n✅ Machine = aux Lavandières."
    if pass_key in ("full", "full_former"):
        note = "\n\n⭐ C’est la version **plus premium / plus complète** de la gamme."

    return (
        f"**{p.label}** — accessible sur : **{studio_label}**\n"
        f"Ce que ça inclut 👇\n{includes}"
        f"{note}"
    )

def answer_planning(text: str) -> str:
    studio = extract_studio(text)
    day = extract_day(text)
    course_key = extract_course_key(text)

    # Si on a un cours, on force le studio le plus logique
    if course_key and studio is None:
        if course_key in ("reformer", "crossformer", "yoga vinyasa", "hatha flow", "classic pilates", "power pilates", "core & stretch"):
            studio = "lavandieres"
        elif course_key in ("boxe", "afrodance", "cross training", "cross core", "cross body", "cross rox", "cross yoga", "training kids", "yoga kids"):
            studio = "docks"

    # Cas : "quel jour reformer"
    if course_key and not day:
        found = slots_for(studio=studio, course_key=course_key) if studio else slots_for(course_key=course_key)
        if not found:
            return "Je ne vois pas ce cours sur le planning actuel. Tu parles de quel studio : Docks ou Lavandières ?"
        studio_txt = f" — {STUDIOS[studio]['label']}" if studio in STUDIOS else ""
        hint = tag_to_pass_hint(found[0].tag)
        return (
            f"Voilà les créneaux **{course_key.capitalize()}**{studio_txt} 👇\n\n"
            f"{format_slots_grouped(found)}\n\n"
            f"✅ Accessible via : **{hint}**"
        )

    # Cas : "jeudi reformer"
    if course_key and day:
        if studio is None:
            studio = "lavandieres"
        found = slots_for(studio=studio, day=day, course_key=course_key)
        if not found:
            return f"Je ne vois pas **{course_key}** le **{day}** sur {STUDIOS[studio]['label']}. Tu veux que je te donne tous les jours où il y en a ?"
        hint = tag_to_pass_hint(found[0].tag)
        times = ", ".join([x.time for x in found])
        return f"**{day.capitalize()}** : {course_key.capitalize()} à **{times}** ({STUDIOS[studio]['label']}). ✅ {hint}"

    # Cas : "planning lavandières"
    if (course_key is None) and studio and not day:
        found = slots_for(studio=studio)
        return f"Planning **{STUDIOS[studio]['label']}** 👇\n\n{format_slots_grouped(found)}"

    # fallback
    if course_key is None and not studio and not day:
        return (
            "Tu veux le planning de quel studio ?\n"
            f"- **{STUDIOS['docks']['label']}** (Cross/Boxe/Kids…)\n"
            f"- **{STUDIOS['lavandieres']['label']}** (Reformer/Crossformer/Yoga…)\n\n"
            "Dis-moi juste “planning docks” ou “planning lavandières”."
        )

    if studio and day:
        found = slots_for(studio=studio, day=day)
        if not found:
            return f"Je ne vois rien le **{day}** sur {STUDIOS[studio]['label']}."
        return f"{STUDIOS[studio]['label']} — {day.capitalize()} 👇\n\n{format_slots_grouped(found)}"

    return "Dis-moi le cours + le studio (ex: “Reformer lavandières” ou “Boxe docks”) et je te donne les créneaux."

def answer_interest(text: str) -> str:
    ck = extract_course_key(text)
    if not ck:
        return "Tu veux plutôt Machines (Reformer/Crossformer) ou Training (Cross/Boxe/Yoga) ?"
    d = DEFINITIONS.get(ck)
    if d:
        return d + "\n\n" + answer_planning(text)
    return answer_planning(text)

def answer_premium_upgrade() -> str:
    lp = st.session_state.last_pass
    if lp in ("focus", "cross"):
        return "Si tu veux la version plus premium : prends le **Pass Full** ✅ (ça te donne **Cross + Focus**)."
    if lp in ("reformer", "crossformer"):
        return "Si tu veux la version plus premium : prends le **Pass Full Former** ✅ (ça te donne **Reformer + Crossformer**)."
    return "Tu veux une version premium côté **Training** (Full) ou côté **Machines** (Full Former) ?"

# ------------------------------------------------------------------------------
# ROUTER (priorités)
# ------------------------------------------------------------------------------
def deterministic_router(user_text: str) -> Tuple[Optional[str], bool, Optional[str]]:
    """
    Returns: (answer, needs_whatsapp, pass_key_to_store)
    """
    # 0) humain direct
    if intent_human(user_text):
        txt, wa = human_alert("OK 🙂 je te mets avec l’équipe.")
        return txt, wa, None

    # 1) upgrade premium (avec contexte)
    if intent_premium(user_text):
        return answer_premium_upgrade(), False, None

    # 2) pause / règles (avant inscription)
    if intent_pause(user_text) or intent_rules(user_text):
        return answer_rules(user_text), False, None

    # 3) planning (haut pour répondre vite)
    if intent_planning(user_text):
        return answer_planning(user_text), False, None

    # 4) “je veux faire du reformer”
    if intent_interest(user_text):
        return answer_interest(user_text), False, None

    # 5) définitions
    if intent_definition(user_text):
        d = answer_definition(user_text)
        if d:
            return d, False, None

    # 6) essai / starter / boost / parrainage
    if intent_trial(user_text):
        return answer_trial(), False, None
    if intent_starter(user_text):
        return answer_starter(), False, None
    if intent_boost(user_text):
        return answer_boost(), False, None
    if intent_parrainage(user_text):
        return answer_parrainage(), False, None

    # 7) coaching / kids
    if intent_coaching(user_text):
        return answer_coaching(), False, None
    if intent_kids(user_text):
        return answer_kids(), False, None

    # 8) info pass (sans chiffres)
    if intent_pass_info(user_text):
        pk = find_pass_key(user_text)
        if pk:
            return answer_pass_info(pk), False, pk
        return "Tu parles de quel pass : Cross, Focus, Full, Reformer, Crossformer ou Full Former ?", False, None

    # 9) inscription
    if intent_signup(user_text):
        return answer_signup(), False, None

    # 10) séance supp
    if intent_extra_session(user_text):
        return answer_extra_session(user_text), False, None

    # 11) prix à l’unité
    if intent_unit_price(user_text):
        return answer_unit_price(user_text), False, None

    # 12) prix d’un pass (avec sessions)
    if intent_pass_price(user_text):
        pk = find_pass_key(user_text)
        n = find_sessions_count(user_text)
        if pk and n:
            out = answer_pass_price(pk, n)
            if out:
                return out, False, pk

    return None, False, None

# ------------------------------------------------------------------------------
# RENDER CHAT
# ------------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

api_key = get_api_key()
prompt = st.chat_input("Posez votre question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    det, needs_wa, store_pass = deterministic_router(prompt)

    if det is not None:
        with st.chat_message("assistant"):
            st.markdown(det)
        st.session_state.messages.append({"role": "assistant", "content": det})

        if store_pass:
            st.session_state.last_pass = store_pass

        if needs_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])

    else:
        # fallback Gemini contrôlé
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
                        txt, needs_wa2 = call_gemini(api_key, st.session_state.messages, prompt)
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