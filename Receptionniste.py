import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES (CERVEAU)
# ==============================================================================
try:
    from donnees_studio import CONTEXTE_COMPLET
except ImportError:
    st.error("⚠️ ERREUR : Le fichier 'donnees_studio.py' est introuvable !")
    st.stop()

# ==============================================================================
# 2. CONFIGURATION & STYLE (CORRECTION COULEURS)
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡")

st.markdown("""
<style>
/* 1. Fond de l'application en BLANC */
.stApp {
    background-color: #ffffff;
    color: #000000;
}

/* 2. Bulles de chat en GRIS CLAIR */
div[data-testid="stChatMessage"] {
    background-color: #f0f2f6;
    border-radius: 15px;
    padding: 15px;
    border: 1px solid #e0e0e0;
}

/* 3. FORCE LE TEXTE EN NOIR (TRES IMPORTANT) */
div[data-testid="stChatMessage"] * {
    color: #000000 !important;
    font-family: sans-serif;
}

/* 4. Titre */
h1 {
    color: #8FB592 !important;
    text-align: center;
    font-family: cursive;
}
</style>
""", unsafe_allow_html=True)

st.title("Sarah - SVB 🧡")

# ==============================================================================
# 3. INTELLIGENCE ARTIFICIELLE (GEMINI PRO)
# ==============================================================================

def ask_sarah(user_message, history):
    # Clé API
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "⚠️ Erreur : Clé API introuvable."

    # Connexion
    genai.configure(api_key=api_key)
    
    try:
        # On utilise le modèle STANDARD (gemini-pro)
        model = genai.GenerativeModel("gemini-pro")
        
        # Contexte
        full_prompt = CONTEXTE_COMPLET + "\n\n--- CONVERSATION ---\n"
        
        for msg in history:
            role = "CLIENT" if msg["role"] == "user" else "SARAH"
            full_prompt += f"{role}: {msg['content']}\n"
        
        full_prompt += f"CLIENT: {user_message}\nSARAH:"

        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        return f"Oups, erreur technique : {e}"

# ==============================================================================
# 4. INTERFACE DE CHAT
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Bonjour ! Je suis Sarah. Planning, Tarifs, Conseils... Je t'écoute ! 🙂"
    }]

# AFFICHER L'HISTORIQUE
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ZONE DE SAISIE
if prompt := st.chat_input("Pose ta question..."):
    # Message Utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse IA
    with st.chat_message("assistant"):
        with st.spinner("Sarah réfléchit..."):
            ai_reply = ask_sarah(prompt, st.session_state.messages[:-1])
            st.markdown(ai_reply)
            
            if "whatsapp" in ai_reply.lower():
                st.link_button("📞 Contacter l'équipe", "https://wa.me/33744919155")

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})