import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. CONFIGURATION DU DESIGN PREMIUM
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

# CSS DESIGN "COCON" (LISIBLE & BEAU)
st.markdown("""
<style>
    /* 1. FOND GÉNÉRAL (Crème très léger pour la douceur) */
    .stApp {
        background-color: #FDFBF7 !important;
        color: #4A4A4A !important; /* Texte gris foncé doux, pas noir brut */
    }

    /* 2. TITRE (Police élégante et couleur Pêche) */
    h1 {
        color: #E68D65 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
        text-align: center;
        margin-bottom: 30px;
    }

    /* 3. BULLES ASSISTANT (Sarah) - Vert Sauge très doux */
    .stChatMessage {
        background-color: #E8F3E8 !important; /* Vert très pâle */
        border: none !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        color: #2E4033 !important; /* Texte vert foncé lisible */
    }

    /* 4. BULLES UTILISATEUR (Client) - Blanc Pur */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        color: #4A4A4A !important;
    }

    /* 5. ZONE DE SAISIE (Moderne) */
    .stChatInputContainer {
        background-color: transparent !important;
    }
    div[data-testid="stChatInput"] {
        border-radius: 30px !important;
        border: 1px solid #E68D65 !important; /* Bordure orange douce */
        background-color: #FFFFFF !important;
    }

    /* 6. BOUTON WHATSAPP (Vert Officiel mais arrondi) */
    .whatsapp-btn {
        background-color: #25D366 !important;
        color: white !important;
        padding: 12px 25px;
        text-decoration: none;
        border-radius: 50px;
        display: inline-block;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.2);
        transition: transform 0.2s;
        text-align: center;
        margin-top: 10px;
    }
    .whatsapp-btn:hover {
        transform: scale(1.05);
    }
    
    /* 7. ENLEVER LE MENU STREAMLIT (Plus pro) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BIBLE DU STUDIO
# ==============================================================================
INFO_STUDIO = """
CONTEXTE : Tu es Sarah, l'assistante virtuelle du studio "SVB" (Santez-Vous Bien).
TON STYLE : Doux, bienveillant, précis, "Cocon".
INTERDICTION : Ne jamais inventer une information.

--- 1. IDENTITÉ ---
Nom : SVB (Santez-Vous Bien).
Contact : Laura (07 44 91 91 55 - WhatsApp).
Mail : hello@studiosvb.fr

--- 2. ADRESSES ---
LIEU A : "LAVANDIÈRES" (40 Cours des Lavandières).
-> Zen & Machines (Reformer, Yoga, Tapis).
-> Chaussettes obligatoires.

LIEU B : "DOCKS" (6 Mail André Breton).
-> Énergie & Sol (Cross Training, Boxe, Danse).

--- 3. CONFORT ---
Douches : OUI partout.
Service : Tout fourni (Serviettes, Gel douche, Shampoing). Venez léger.

--- 4. TARIFS (ENGAGEMENT 3 MOIS) ---
Frais dossier : 49€ (OFFERTS avec Boost).
OPTION BOOST (+9,90€/mois) : Frais offerts, Suspension libre, Invité.

PASS CROSS (Docks) : 2 sess: 30,30€ | 4 sess: 60,30€ | 8 sess: 116,30€
PASS FOCUS (Mixte) : 2 sess: 36,30€ | 4 sess: 72,30€ | 8 sess: 136,30€
PASS REFORMER (Lavandières) : 2 sess: 70,30€ | 4 sess: 136,30€ | 8 sess: 256,30€
PASS FULL (Sol) : 2 sess: 40,30€ | 4 sess: 80,30€ | 8 sess: 150,30€
PASS FULL FORMER (Machines) : 2 sess: 74,30€ | 4 sess: 144,30€ | 8 sess: 272,30€

OFFRE STARTER : 99,90€ (5 sessions, 1 mois, sans engagement).
UNITÉ : 30€ (Training) / 50€ (Machine).
AJOUT SÉANCE ABONNÉ : 30€.

--- 5. RÈGLES ---
RETARD : 5 min max.
ANNULATION : 1h avant (collectif).
SUSPENSION : Avec Boost = Immédiate. Sans Boost = Préavis 1 mois + 10j absence.
MODIFICATION : Upgrade = Oui. Downgrade = Non (pendant 3 mois).
"""

# ==============================================================================
# 3. MOTEUR IA
# ==============================================================================

api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Clé API manquante.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais tout sur le studio (Tarifs, Planning, Confort). Comment puis-je t'aider ?"}
    ]

# TITRE
st.markdown("<h1>🧡 Studio Santez-Vous Bien</h1>", unsafe_allow_html=True)

# HISTORIQUE
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# SAISIE
if prompt := st.chat_input("Pose ta question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
    full_prompt = f"{INFO_STUDIO}\n\nHISTORIQUE:\n{history_context}\n\nQUESTION: {prompt}\n\nCONSIGNE: Réponds court, chaleureux, précis. Si besoin aide -> [HUMAN_ALERT]."

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
                    st.markdown(f'<a href="https://wa.me/33744919155" target="_blank" class="whatsapp-btn">📞 Parler à Laura sur WhatsApp</a>', unsafe_allow_html=True)
            except:
                st.error("Oups, petit souci de connexion.")
