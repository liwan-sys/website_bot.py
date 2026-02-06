import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. CONFIGURATION FORCEE (MODE CLAIR OBLIGATOIRE)
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# CSS "NUCLÉAIRE" POUR FORCER L'AFFICHAGE
st.markdown("""
<style>
    /* 1. On force le fond de TOUTE l'application en BLANC */
    .stApp {
        background-color: #ffffff !important;
    }

    /* 2. On force TOUS les textes de base en NOIR */
    p, div, label, h1, h2, h3, li, span {
        color: #000000 !important;
    }

    /* 3. Le Titre en Orange */
    h1 {
        color: #E68D65 !important;
        text-align: center;
        font-family: sans-serif;
    }

    /* 4. Les Bulles de Chat (Assistant) */
    .stChatMessage {
        background-color: #f0f2f6 !important;
        border: 1px solid #d5d5d5 !important;
        color: #000000 !important;
        border-radius: 10px !important;
    }

    /* 5. Les Bulles de Chat (Utilisateur) - Un peu plus foncé pour distinguer */
    div[data-testid="stChatMessage"] {
        background-color: #e3e3e3 !important;
        color: #000000 !important;
    }

    /* 6. La zone de saisie (Chat Input) - CRITIQUE */
    .stChatInputContainer {
        background-color: #ffffff !important;
    }
    div[data-testid="stChatInput"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    /* Le texte qu'on tape dans la barre */
    textarea {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* 7. Bouton WhatsApp */
    .whatsapp-btn {
        background-color: #25D366 !important;
        color: white !important;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        display: inline-block;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LA BIBLE DU STUDIO (DONNÉES)
# ==============================================================================
INFO_STUDIO = """
CONTEXTE : Tu es Sarah, l'assistante virtuelle du studio de sport "SVB" (Santez-Vous Bien).
TON RÔLE : Répondre aux clients avec précision, chaleur et professionnalisme.
INTERDICTION : Ne jamais inventer une information.

--- 1. IDENTITÉ & CONTACT ---
Nom : SVB (Santez-Vous Bien).
Contact Humain (Laura) : 07 44 91 91 55 (WhatsApp).
Email : hello@studiosvb.fr

--- 2. LES ADRESSES ---
LIEU A : "LAVANDIÈRES" (40 Cours des Lavandières, St Ouen).
-> Activités : Pilates Reformer, Crossformer, Yoga, Pilates Tapis.
-> Règle : Chaussettes antidérapantes OBLIGATOIRES.

LIEU B : "DOCKS" (6 Mail André Breton, St Ouen).
-> Activités : Cross Training, Boxe, Danse, Yoga Kids.

--- 3. CONFORT ---
Douches : OUI, disponibles partout.
Service : Tout est fourni (Serviettes, Gel douche, Shampoing).
Le client vient les mains libres.

--- 4. TARIFS (ENGAGEMENT 3 MOIS) ---
Frais de dossier : 49€ (OFFERTS si Option Boost).
OPTION "BOOST" (+9,90€/mois) : Frais offerts, Suspension libre, 1 invité.

PASS CROSS (Docks) : 2 sess: 30,30€ | 4 sess: 60,30€ | 8 sess: 116,30€
PASS FOCUS (Mixte) : 2 sess: 36,30€ | 4 sess: 72,30€ | 8 sess: 136,30€
PASS REFORMER (Lavandières) : 2 sess: 70,30€ | 4 sess: 136,30€ | 8 sess: 256,30€
PASS CROSSFORMER (Lavandières) : 2 sess: 78,30€ | 4 sess: 152,30€ | 8 sess: 288,30€
PASS FULL (Combo Sol) : 2 sess: 40,30€ | 4 sess: 80,30€ | 8 sess: 150,30€
PASS FULL FORMER (Combo Machines) : 2 sess: 74,30€ | 4 sess: 144,30€ | 8 sess: 272,30€

OFFRE STARTER : 99,90€ (5 sessions, 1 mois, sans engagement).
PRIX UNITAIRE : 30€ (Training) / 50€ (Machine).
AJOUT SÉANCE ABONNÉ : 30€.

--- 5. RÈGLES ---
RETARD : 5 min max.
ANNULATION : 1h avant (collectif) / 24h avant (privé).
SUSPENSION : Avec Boost = Immédiate. Sans Boost = Préavis 1 mois + 10j absence.
MODIFICATION : Upgrade = Oui. Downgrade = Non (pendant 3 mois).
"""

# ==============================================================================
# 3. MOTEUR IA
# ==============================================================================

# Clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.warning("⚠️ Clé API introuvable.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialisation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis Sarah. Je connais tout sur le studio SVB (Tarifs, Planning, Règles). Comment puis-je t'aider ?"}
    ]

# Affichage Titre
st.title("🧡 Studio SVB")

# Affichage Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Saisie
if prompt := st.chat_input("Pose ta question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse IA
    history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
    full_prompt = f"{INFO_STUDIO}\n\nHISTORIQUE:\n{history_context}\n\nQUESTION: {prompt}\n\nRéponds court et précis. Si besoin aide humaine -> [HUMAN_ALERT]."

    with st.chat_message("assistant"):
        with st.spinner("..."):
            try:
                response = model.generate_content(full_prompt)
                text_response = response.text
                
                show_wa = False
                if "[HUMAN_ALERT]" in text_response:
                    show_wa = True
                    text_response = text_response.replace("[HUMAN_ALERT]", "")
                
                st.markdown(text_response)
                st.session_state.messages.append({"role": "assistant", "content": text_response})
                
                if show_wa:
                    st.markdown("---")
                    st.markdown(f'<a href="https://wa.me/33744919155" target="_blank" class="whatsapp-btn">📞 WhatsApp Laura</a>', unsafe_allow_html=True)
            except:
                st.error("Erreur de connexion.")
