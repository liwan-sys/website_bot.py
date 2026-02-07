import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES (CERVEAU)
# ==============================================================================
try:
    # On essaie d'importer le fichier que tu as créé à l'étape 1
    from donnees_studio import CONTEXTE_COMPLET
except ImportError:
    # Si ça rate, on met un message d'erreur clair
    st.error("⚠️ ERREUR : Le fichier 'donnees_studio.py' est introuvable !")
    st.warning("Assure-toi d'avoir créé le fichier 'donnees_studio.py' dans le même dossier que celui-ci.")
    st.stop()

# ==============================================================================
# 2. CONFIGURATION & STYLE
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡")

st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #000000; font-family: sans-serif; }
.stChatMessage { background-color: #f0f2f6; border-radius: 15px; padding: 15px; color: #000000; }
h1 { color: #8FB592; text-align: center; font-family: cursive; }
</style>
""", unsafe_allow_html=True)

st.title("Sarah - SVB 🧡")

# ==============================================================================
# 3. INTELLIGENCE ARTIFICIELLE (MODE COMPATIBLE)
# ==============================================================================

def ask_sarah(user_message, history):
    # 1. Récupération Clé API
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "⚠️ Erreur : Je ne trouve pas la clé API dans le dossier .streamlit/secrets.toml"

    # 2. Configuration & Connexion
    genai.configure(api_key=api_key)
    
    try:
        # ICI : ON FORCE LE MODÈLE "gemini-pro" (LE PLUS STABLE)
        # On n'utilise pas "flash" pour éviter ton erreur 404
        model = genai.GenerativeModel("gemini-pro")
        
        # 3. Construction du message pour l'IA
        # On combine tes données (donnees_studio) + la conversation
        full_prompt = CONTEXTE_COMPLET + "\n\n--- HISTORIQUE DE CONVERSATION ---\n"
        
        # On ajoute l'historique pour qu'elle ait de la mémoire
        for msg in history:
            role = "CLIENT" if msg["role"] == "user" else "SARAH"
            full_prompt += f"{role}: {msg['content']}\n"
        
        # On ajoute la question actuelle
        full_prompt += f"CLIENT: {user_message}\nSARAH:"

        # 4. Envoi
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        return f"Oups, petite erreur technique : {e}"

# ==============================================================================
# 4. INTERFACE DE CHAT
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Bonjour ! Je suis Sarah. Planning, Tarifs, Conseils... Je t'écoute ! 🙂"
    }]

# Afficher l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Zone de saisie
if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sarah réfléchit..."):
            ai_reply = ask_sarah(prompt, st.session_state.messages[:-1])
            st.markdown(ai_reply)
            
            # Bouton WhatsApp intelligent
            if "whatsapp" in ai_reply.lower() or "équipe" in ai_reply.lower():
                st.link_button("📞 Contacter l'équipe", "https://wa.me/33744919155")

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})