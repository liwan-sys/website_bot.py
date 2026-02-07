# ==============================================================================
# receptionniste.py — SARAH SVB (RÔLE + LOGIQUE + MÉMOIRE)
# ==============================================================================

import re
import streamlit as st

from knowledge import CONTACT, STUDIOS, PRICING, PLANNING, DEFINITIONS, PASS_ACCESS, FAQ

# ---------------- UI ----------------
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%); }
#MainMenu, footer, header {visibility:hidden;}
.stChatMessage { background:#fff !important; border:1px solid #EBC6A6; border-radius:15px; padding:14px; }
.stChatMessage * { color:#000 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;color:#8FB592;margin-bottom:0;'>Sarah</h2>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:#EBC6A6;font-weight:700;margin-bottom:18px;'>SVB • Santez-Vous-Bien</div>", unsafe_allow_html=True)

# ---------------- Helpers ----------------
DAY_ORDER = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]

def norm(t: str) -> str:
    t = (t or "").lower().strip()
    for a,b in [("é","e"),("è","e"),("ê","e"),("à","a"),("ù","u"),("ç","c"),("’","'")]:
        t = t.replace(a,b)
    return t

def eur(x: float) -> str:
    return f"{x:,.2f}€".replace(",", " ").replace(".", ",")

def extract_sessions(t: str):
    m = re.search(r"\b(2|4|6|8|10|12)\b", t)
    return int(m.group(1)) if m else None

def extract_day(t: str):
    for d in DAY_ORDER:
        if d in t:
            return d
    return None

def match_course(t: str):
    # tolérance fautes
    aliases = {
        "pilate reformer": "reformer",
        "pilates reformer": "reformer",
        "reformer": "reformer",
        "crossformer": "crossformer",
        "cross former": "crossformer",
        "boxe": "boxe",
        "afrodance": "afrodance",
        "vinyasa": "yoga vinyasa",
        "yoga vinyasa": "yoga vinyasa",
        "hatha": "hatha flow",
        "hatha flow": "hatha flow",
        "classic pilates": "classic pilates",
        "power pilates": "power pilates",
        "core and stretch": "core & stretch",
        "core & stretch": "core & stretch",
        "stretch": "core & stretch",
        "cross training": "cross training",
        "cross core": "cross core",
        "cross body": "cross body",
        "cross rox": "cross rox",
        "cross yoga": "cross yoga",
        "yoga kids": "yoga kids",
        "training kids": "training kids",
    }
    for k in sorted(aliases.keys(), key=len, reverse=True):
        if k in t:
            return aliases[k]
    return None

def course_default_studio(course: str):
    if course in ("reformer","crossformer","yoga vinyasa","hatha flow","classic pilates","power pilates","core & stretch"):
        return "lavandieres"
    if course in ("boxe","afrodance","cross training","cross core","cross body","cross rox","cross yoga","yoga kids","training kids"):
        return "docks"
    return None

def passes_that_include(course: str):
    out = []
    for p, courses in PASS_ACCESS.items():
        if course in courses:
            out.append(p)
    return out

# ---------------- Mémoire (slots + pending) ----------------
def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"assistant","content":"Salut 🙂 Tu veux un **prix**, un **planning** ou une **explication de cours** ?"}]
    if "slots" not in st.session_state:
        st.session_state.slots = {"course": None, "sessions": None, "intent": None}
    if "pending" not in st.session_state:
        st.session_state.pending = None  # ex: {"need":"sessions","for":"price"}

ensure_state()

# ---------------- Cerveau déterministe (réflexion) ----------------
def answer_definition(course: str):
    if course in DEFINITIONS:
        return DEFINITIONS[course]
    if course == "yoga vinyasa":
        return "Le **Yoga Vinyasa** = flow dynamique, respiration, mobilité."
    if course == "hatha flow":
        return "Le **Hatha Flow** = yoga plus doux/contrôlé, top pour commencer."
    if course in ("classic pilates","power pilates"):
        return "Cours de Pilates au sol : gainage + posture + mobilité (version plus dynamique pour Power)."
    if course.startswith("cross"):
        return "Cours training intensité (cardio + renfo) avec des variantes selon la séance."
    return "Tu parles de quel cours exactement ? (Reformer, Crossformer, Boxe, Cross Training…)"

def answer_price_for_course(course: str, sessions: int = None):
    # Unité claire + abonnement si pertinent
    if course in ("reformer","crossformer"):
        unit = eur(PRICING["unit_machine"])
    else:
        unit = eur(PRICING["unit_training"])

    # Si pas de sessions => on répond utile + question
    if not sessions:
        included = passes_that_include(course)
        if included:
            pass_names = ", ".join([p.replace("_"," ").title() for p in included])
            return (
                f"Pour **{course.title()}** :\n"
                f"- À l’unité : **{unit}**\n"
                f"- En abonnement : via **{pass_names}**.\n\n"
                f"Tu veux **4 / 8 / 12** séances par mois ?"
            )
        return f"Pour **{course.title()}** : à l’unité c’est **{unit}**. Tu cherches plutôt à l’unité ou en abonnement ?"

    # On propose le(s) bon(s) pass
    included = passes_that_include(course)
    if not included:
        return f"Je n’ai pas trouvé le pass associé à **{course}**. Tu peux m’écrire sur WhatsApp et on te confirme 🙂"

    # Pour une demande “Boxe 4” -> Focus 4 ou Full 4
    lines = [f"Pour **{course.title()} — {sessions} séances/mois** :"]
    for p in included:
        if p not in PRICING["passes"]:
            continue
        table = PRICING["passes"][p]
        if sessions in table:
            total = table[sessions]
            lines.append(f"- **Pass {p.replace('_',' ').title()}** : **{eur(total)}** (≈ {eur(total/sessions)} / séance)")
    if len(lines) == 1:
        return "Tu veux quel pass exactement ? (Focus / Full / Cross / Reformer / Crossformer)"

    # Ajoute explication (évite erreurs Focus vs Cross)
    if course in ("cross training","cross core","cross body","cross rox","cross yoga"):
        lines.append("📌 Ces cours sont côté **Docks** → plutôt **Pass Cross** ou **Pass Full**.")
    if course in ("boxe","afrodance","yoga vinyasa","hatha flow","classic pilates","power pilates","core & stretch"):
        lines.append("📌 Ces cours sont côté **Focus** → **Pass Focus** ou **Pass Full**.")

    return "\n".join(lines)

def answer_planning(course: str = None, day: str = None, studio: str = None):
    if course and not studio:
        studio = course_default_studio(course)

    if studio and studio not in PLANNING:
        return "Tu parles de quel studio : **Docks** ou **Lavandières** ?"

    if not studio:
        return "Tu veux le planning de quel studio : **Docks** ou **Lavandières** ?"

    if day:
        slots = PLANNING[studio].get(day, [])
        if not slots:
            return f"Je ne vois rien le **{day}** à **{STUDIOS[studio]['label']}**."
        return f"🗓️ **{day.capitalize()} — {STUDIOS[studio]['label']}** :\n- " + "\n- ".join(slots)

    # si cours sans jour => filtre simple
    if course:
        found = []
        for d in DAY_ORDER:
            for item in PLANNING[studio].get(d, []):
                if norm(course) in norm(item):
                    found.append((d, item))
        if not found:
            return f"Je ne vois pas **{course.title()}** sur le planning {STUDIOS[studio]['label']}."
        lines = [f"Voilà **{course.title()}** à **{STUDIOS[studio]['label']}** :"]
        for d, it in found:
            lines.append(f"- **{d.capitalize()}** : {it}")
        return "\n".join(lines)

    return f"Tu veux quel jour ? (lundi…dimanche) — pour **{STUDIOS[studio]['label']}**"

def router(user_text: str):
    t = norm(user_text)
    slots = st.session_state.slots

    # 0) si l’utilisateur répond juste un nombre (ex: "4") et qu’on attendait ça
    n = extract_sessions(t)
    if n and st.session_state.pending and st.session_state.pending.get("need") == "sessions":
        slots["sessions"] = n
        st.session_state.pending = None
        # on répond tout de suite sur le contexte précédent
        if slots["intent"] == "price" and slots["course"]:
            return answer_price_for_course(slots["course"], slots["sessions"]), False

    # 1) FAQ rapides
    if any(w in t for w in ["tenue","chaussette","chaussure","basket"]):
        return FAQ["tenue"], False
    if "retard" in t:
        return FAQ["retard"], False
    if any(w in t for w in ["annuler","annulation"]):
        return FAQ["annulation"], False

    # 2) définition
    if any(w in t for w in ["c'est quoi","c quoi","definition","explique"]):
        course = match_course(t)
        if course:
            slots["course"] = course
            slots["intent"] = "definition"
            return answer_definition(course), False
        return "Tu veux la définition de quel cours ? (Reformer, Crossformer, Boxe…)", False

    # 3) planning
    if any(w in t for w in ["planning","horaire","horaires","quel jour","quand","a quelle heure","à quelle heure"]):
        course = match_course(t)
        day = extract_day(t)
        if course:
            slots["course"] = course
            slots["intent"] = "planning"
            return answer_planning(course=course, day=day), False
        return "Tu veux le planning de quel cours ? (Reformer, Boxe, Cross Training…)", False

    # 4) prix
    if any(w in t for w in ["prix","tarif","combien","coute","coûte"]):
        course = match_course(t)
        sessions = extract_sessions(t)

        slots["intent"] = "price"
        if course:
            slots["course"] = course
        if sessions:
            slots["sessions"] = sessions

        # si on a le cours -> répond utile
        if slots["course"]:
            if not slots["sessions"] and slots["course"] in ("boxe","afrodance","yoga vinyasa","hatha flow","classic pilates","power pilates","core & stretch",
                                                            "cross training","cross core","cross body","cross rox","cross yoga"):
                st.session_state.pending = {"need":"sessions","for":"price"}
                return answer_price_for_course(slots["course"], None), False

            return answer_price_for_course(slots["course"], slots["sessions"]), False

        return "Tu parles de quel cours ? (Reformer, Crossformer, Boxe…)", False

    # 5) si l’utilisateur dit juste "prix" après contexte
    if t in ("prix","tarif"):
        slots["intent"] = "price"
        if slots["course"]:
            if not slots["sessions"]:
                st.session_state.pending = {"need":"sessions","for":"price"}
                return answer_price_for_course(slots["course"], None), False
            return answer_price_for_course(slots["course"], slots["sessions"]), False
        return "Le prix de quel cours ? 🙂", False

    # fallback
    return "Tu veux plutôt un **prix**, un **planning**, ou une **explication** ? 🙂", False

# ---------------- UI loop ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Pose ta question…")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    resp, show_wa = router(prompt)

    st.session_state.messages.append({"role":"assistant","content":resp})
    with st.chat_message("assistant"):
        st.markdown(resp)
        if show_wa:
            st.markdown("---")
            st.link_button(CONTACT["whatsapp_label"], CONTACT["whatsapp_url"])
