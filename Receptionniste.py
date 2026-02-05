import streamlit as st
import google.generativeai as genai

# --- IMPORTATION MÉMOIRE ---
try:
    from knowledge import INFO_STUDIO
except ImportError:
    INFO_STUDIO = "Erreur : Mémoire introuvable."

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# Masquer le menu Streamlit (Effet Site Web)
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- CLÉ API (SECRETS) ---
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# --- INTERFACE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah, l'assistante du studio. Je peux vous renseigner sur nos cours (Pilates, Yoga...), nos tarifs ou le planning. Comment puis-je vous aider ?"}
    ]

st.markdown("<h3 style='text-align: center; color: #EBC6A6;'>🧡 Bienvenue au Studio SVB</h3>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # FILTRE DE SÉCURITÉ (IMPORTANT)
            system_prompt = f"""
            Tu es Sarah, assistante d'accueil du studio SVB.
            INFO STUDIO : {INFO_STUDIO}
            
            CONSIGNES :
            - Tu es POLIE, DOUCE et BIENVEILLANTE (DA "Cocon").
            - Tu réponds aux questions clients (Prix, Horaires, Tenue).
            - INTERDIT : Ne parle JAMAIS de stratégie, de closing, de scripts de vente ou de fonctionnement interne.
            - Finis par une question ouverte.
            """
            
            with st.chat_message("assistant"):
                response = model.generate_content([system_prompt, prompt])
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error("Je reviens dans un instant !")
    else:
        st.info("L'assistante démarre...")
