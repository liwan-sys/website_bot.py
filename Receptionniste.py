import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. CONFIGURATION & STYLE
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
# 2. LE CERVEAU (MANUEL DU STUDIO)
# ==============================================================================

SYSTEM_INSTRUCTIONS = """
TU ES SARAH, LA MANAGER VIRTUELLE DU STUDIO DE SPORT "SVB" (SANTEZ-VOUS BIEN).
Ton rôle est d'accueillir, renseigner, vendre et rassurer. Tu es chaleureuse, pro et tu utilises des emojis.

--- RÈGLES D'INTELLIGENCE ---
1. COMPRÉHENSION : Tu dois comprendre les fautes ("pialte" = Pilates, "pric" = Prix).
2. DÉDUCTION : "Mal de dos" -> Reformer. "Transpirer" -> Boxe.
3. PRÉCISION : Utilise uniquement la grille tarifaire ci-dessous.

--- 💰 LA GRILLE TARIFAIRE (BIBLE DES PRIX) ---
A L'UNITÉ :
- Training (Sol/Boxe/Yoga) : 30€
- Machine (Reformer/Crossformer) : 50€
- SÉANCE D'ESSAI : 30€ (15€ remboursés si achat pass).

OFFRES DÉMARRAGE :
- STARTER : 99,90€ (5 sessions, 1 mois).
- OPTION BOOST : 9,90€/mois.

ABONNEMENTS (PASS) :
1. PASS FOCUS (Pilates Sol/Yoga) : 4 sess=72,30€ | 8 sess=136,30€
2. PASS REFORMER (Machine Zen) : 4 sess=136,30€ | 8 sess=256,30€
3. PASS CROSSFORMER (Machine Cardio) : 4 sess=152,30€ | 8 sess=288,30€
4. PASS CROSS (Boxe/Training) : 4 sess=60,30€ | 8 sess=116,30€
5. PASS KIDS : 2 sess=35,30€ | 4 sess=65,30€

--- 📅 LE PLANNING TYPE ---
LUNDI : Docks (Training 12h/19h) | Lavandières (Reformer 12h/19h)
MARDI : Docks (Cross 12h/20h) | Lavandières (Hatha 7h30, Reformer 13h)
MERCREDI : Docks (Kids 16h, Boxe 20h) | Lavandières (Reformer 12h/19h)
JEUDI : Docks (Boxe 13h, Afro 19h) | Lavandières (Pilates 7h, Yoga 12h)
VENDREDI : Docks (Cross 19h) | Lavandières (Reformer 12h)
SAMEDI : Docks (Kids 9h30) | Lavandières (Reformer 9h/10h)
DIMANCHE : Docks (Yoga 11h30) | Lavandières (Reformer 10h)

--- 🛡️ FAQ ---
- RETARD : "Tolérance 5 min max."
- TENUE : "Baskets aux Docks. Chaussettes antidérapantes aux Lavandières."
- PARKING : "Lavandières = En face. Docks = Mairie."
"""

# ==============================================================================
# 3. LE MOTEUR IA (CONNEXION INTELLIGENTE)
# ==============================================================================

def get_smart_model(api_key):
    """Essaie de trouver un modèle qui marche sur ton ordinateur."""
    genai.configure(api_key=api_key)
    
    # Liste des modèles à tester par ordre de préférence
    candidates = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
    
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            # Petit test silencieux pour voir si ça marche
            # (On ne fait pas d'appel réseau ici pour aller vite, on instancie juste)
            return model
        except:
            continue
    
    # Si tout rate, on tente le flash par défaut
    return genai.GenerativeModel("gemini-1.5-flash")

def get_ai_response(user_message, history):
    # 1. Clé API
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "⚠️ Erreur : Clé API introuvable dans secrets.toml."

    # 2. Chargement du modèle (Fonction Robuste)
    try:
        model = get_smart_model(api_key)
    except Exception as e:
        return f"Erreur chargement modèle : {e}"

    # 3. Chat
    try:
        # On triche un peu pour gemini-pro : on met le système dans le 1er message
        full_context = SYSTEM_INSTRUCTIONS + "\n\nDISCUSSION EN COURS :\n"
        
        # On ajoute l'historique
        for msg in history:
            role = "CLIENT" if msg["role"] == "user" else "SARAH"
            full_context += f"{role}: {msg['content']}\n"
        
        full_context += f"CLIENT: {user_message}\nSARAH:"

        response = model.generate_content(full_context)
        return response.text
    except Exception as e:
        return f"Oups, erreur de connexion ({e}). As-tu fait la mise à jour 'pip install --upgrade google-generativeai' ?"

# ==============================================================================
# 4. INTERFACE
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello ! Je suis Sarah. Pose-moi tes questions sur le planning ou les prix ! 🙂"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sarah réfléchit..."):
            ai_reply = get_ai_response(prompt, st.session_state.messages[:-1])
            st.markdown(ai_reply)
            
            if "whatsapp" in ai_reply.lower():
                st.link_button("📞 Contacter l'équipe", "https://wa.me/33744919155")

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})