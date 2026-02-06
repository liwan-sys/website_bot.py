import streamlit as st
import google.generativeai as genai
import os

st.title("TEST CLÉ API")

# 1. On essaie de lire la clé
cle = None
try:
    cle = st.secrets["GOOGLE_API_KEY"]
    st.success(f"✅ Clé trouvée dans secrets.toml (début : {cle[:5]}...)")
except:
    st.error("❌ Clé INTROUVABLE dans secrets.toml")

# 2. Si on a une clé, on essaie de parler à Google
if cle:
    try:
        genai.configure(api_key=cle)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Dis bonjour")
        st.success(f"✅ Google a répondu : {response.text}")
    except Exception as e:
        st.error(f"❌ Erreur de connexion Google : {e}")
