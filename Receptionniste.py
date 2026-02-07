import streamlit as st
import google.generativeai as genai
import os

# ON IMPORTE TES DONNÉES DEPUIS L'AUTRE FICHIER
# (Assure-toi que donnees_studio.py est bien dans le même dossier !)
try:
    from donnees_studio import CONTEXTE_COMPLET
except ImportError:
    st.error("⚠️ Je ne trouve pas le fichier 'donnees_studio.py'. Vérifie qu'il est bien créé à côté de ce fichier.")
    st.stop()

# ==============================================================================
# 1. CONFIGURATION
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
# 2. INTELLIGENCE ARTIFICIELLE
# ==============================================================================

def get_smart_model(api_key):
    """Trouve le meilleur modèle disponible sur ton ordi."""
    genai.configure(api_key=api_key)
    # On teste les modèles du plus récent au plus vieux
    candidates = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            return model
        except:
            continue
    return genai.GenerativeModel("gemini-pro") # Fallback

def ask_sarah(user_message, history):
    # 1. Récupération Clé API
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "⚠️ Erreur : Clé API introuvable dans .streamlit/secrets.toml"

    # 2. Chargement du Cerveau
    try:
        model = get_smart_model(api_key)
    except Exception as e:
        return f"Erreur technique : {e}"

    # 3. Construction du contexte pour l'IA
    # On lui donne TOUT le contenu de donnees_studio.py
    full_prompt = CONTEXTE_COMPLET + "\n\n--- CONVERSATION ---\n"
    
    for msg in history:
        role = "CLIENT" if msg["role"] == "user" else "SARAH"
        full_prompt += f"{role}: {msg['content']}\n"
    
    full_prompt += f"CLIENT: {user_message}\nSARAH:"

    # 4. Génération
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Désolée, je réfléchis trop... (Erreur: {e})"

# ==============================================================================
# 3. INTERFACE DE CHAT
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
            
            # Petit bouton WhatsApp intelligent
            if "whatsapp" in ai_reply.lower() or "équipe" in ai_reply.lower():
                st.link_button("📞 Contacter l'équipe", "https://wa.me/33744919155")

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})