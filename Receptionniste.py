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
.info-box { background-color: #e8f4ea; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-size: 0.9em; }
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
1. COMPRÉHENSION : Tu dois comprendre les fautes ("pialte" = Pilates, "pric" = Prix, "cour" = Cours).
2. DÉDUCTION : 
   - "Je veux me muscler le dos" -> Propose Pilates Reformer.
   - "Je veux transpirer" -> Propose Boxe ou Cross Training.
   - "C'est cher" -> Propose l'offre Starter ou le paiement au cours.
3. PRÉCISION : Ne donne JAMAIS un prix au hasard. Utilise la grille ci-dessous.

--- 📍 LES LIEUX ---
1. Studio DOCKS (6 Mail André Breton) : Ambiance "Garage", Intensité, Boxe, Cross Training.
2. Studio LAVANDIÈRES (40 Cours des Lavandières) : Ambiance "Zen/Chic", Pilates Machines, Yoga.
CONTACT HUMAIN : WhatsApp 07 44 91 91 55 (Pour bugs appli, factures, urgences).

--- 💰 LA GRILLE TARIFAIRE (BIBLE DES PRIX) ---
Si on demande un prix, sois précise.

A L'UNITÉ (SANS ABONNEMENT) :
- Cours Training (Sol/Boxe/Yoga) : 30€
- Cours Machine (Reformer/Crossformer) : 50€
- SÉANCE D'ESSAI : 30€ (Dont 15€ remboursés si achat d'un pass ensuite).

OFFRES DE DÉMARRAGE :
- STARTER : 99,90€ (5 sessions, Valable 1 mois). Top pour tester !
- OPTION BOOST : 9,90€/mois (Suspension illimitée + Frais dossier offerts + 1 invité/mois).

LES PASS MENSUELS (Abonnements) :
*Note : Le prix à la séance baisse avec la taille du pass.*

1. PASS FOCUS (Accès : Pilates Sol, Yoga, Mat)
   - 4 sessions/mois : 72,30€
   - 8 sessions/mois : 136,30€
   - 12 sessions/mois : 192,30€

2. PASS REFORMER (Accès : Pilates Reformer - Machine Zen)
   - 4 sessions/mois : 136,30€
   - 8 sessions/mois : 256,30€
   - 12 sessions/mois : 360,30€

3. PASS CROSSFORMER (Accès : Machine Cardio Intense)
   - 4 sessions/mois : 152,30€
   - 8 sessions/mois : 288,30€
   - 12 sessions/mois : 408,30€

4. PASS CROSS (Accès : Boxe, Cross Training - Docks)
   - 4 sessions/mois : 60,30€
   - 8 sessions/mois : 116,30€
   - 12 sessions/mois : 168,30€

5. PASS FULL (Accès : Cross + Focus)
   - 4 sessions/mois : 80,30€
   - 8 sessions/mois : 150,30€
   - 12 sessions/mois : 210,30€

6. PASS KIDS (Enfants)
   - 2 sessions/mois : 35,30€
   - 4 sessions/mois : 65,30€

--- 📅 LE PLANNING TYPE ---
(Si on demande "C'est quand la boxe ?", regarde ici)

LUNDI :
- Docks : 12h/19h Cross Training, 13h Cross Core, 20h Cross Body.
- Lavandières : 12h/18h45 Crossformer, 12h15/19h15 Reformer, 12h30/19h Yoga Vinyasa.

MARDI :
- Docks : 12h Cross Rox, 19h Cross Body, 20h Cross Training.
- Lavandières : 07h30 Hatha Flow, 11h45/18h45 Crossformer, 12h/20h Power Pilates, 13h15/19h15 Reformer.

MERCREDI :
- Docks : 12h/19h Cross Training, 16h Yoga Kids, 20h Boxe.
- Lavandières : 10h15/12h15/19h15 Crossformer, 12h/19h/20h Reformer.

JEUDI :
- Docks : 08h Cross Core, 12h Cross Body, 13h Boxe, 18h Cross Training, 19h Afrodance.
- Lavandières : 07h Pilates, 12h Yoga, 12h15/18h Crossformer, 12h30/18h45 Reformer, 20h15 Cross Yoga.

VENDREDI :
- Docks : 18h Cross Rox, 19h Cross Training.
- Lavandières : 09h45/10h45/19h15 Crossformer, 12h/13h/18h30 Reformer.

SAMEDI :
- Docks : 09h30 Kids, 10h30 Cross Body, 11h30 Cross Training.
- Lavandières : 09h/10h Reformer, 09h30/10h30 Crossformer, 11h15 Core & Stretch.

DIMANCHE :
- Docks : 10h30 Cross Training, 11h30 Cross Yoga.
- Lavandières : 10h/11h Crossformer, 10h15/11h15 Reformer, 11h30 Yoga.

--- 🛡️ FAQ & RÈGLEMENT ---
- RETARD : "Tolérance 5 minutes max."
- TENUE : "Baskets propres aux Docks. Chaussettes antidérapantes OBLIGATOIRES aux Lavandières."
- DOUCHES : "Oui, douches individuelles dispos."
- PARKING : "Lavandières = Parking en face. Docks = Mairie."
- ENCEINTE : "OK pour Reformer/Yoga. INTERDIT pour Cross/Boxe."
- BLESSURE : "Préviens le coach AVANT le cours."
- PAIEMENT : "CB sur l'appli ou sur place."
"""

# ==============================================================================
# 3. LE MOTEUR IA (CONNEXION GOOGLE GEMINI)
# ==============================================================================

def get_ai_response(user_message, history):
    # 1. Vérification de la clé
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "⚠️ **Erreur Technique** : Clé API introuvable. Vérifie le fichier secrets.toml !"

    # 2. Configuration Gemini (MODIFIÉ ICI : gemini-pro au lieu de gemini-1.5-flash)
    genai.configure(api_key=api_key)
    
    # On utilise "gemini-pro" qui est le modèle le plus stable et disponible partout
    try:
        model = genai.GenerativeModel("gemini-pro") 
    except:
        return "Erreur modèle : Impossible de charger Gemini."

    # 3. Construction de la conversation
    # Pour gemini-pro, l'historique doit être simple
    messages = []
    
    # On donne le contexte via le premier message user (astuce pour gemini-pro)
    context_prompt = SYSTEM_INSTRUCTIONS + "\n\nMaintenant, réponds à l'utilisateur :"
    
    # On recrée un chat session
    chat = model.start_chat(history=[])
    
    # On envoie d'abord le contexte système (caché pour l'utilisateur dans l'interface, mais vu par l'IA)
    try:
        chat.send_message(context_prompt)
    except:
        pass

    # On rejoue l'historique pour qu'il ait la mémoire
    for msg in history:
        try:
            if msg["role"] == "user":
                chat.send_message(msg["content"])
            else:
                # Gemini Pro ne permet pas facilement d'insérer des réponses modèle manuellement dans l'historique via l'API simple
                # On ignore l'historique modèle pour simplifier et éviter les erreurs 400
                pass 
        except:
            pass

    # 4. Envoi de la question actuelle
    try:
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"Oups, petite erreur de connexion ({e}). Réessaie !"

# ==============================================================================
# 4. INTERFACE UTILISATEUR
# ==============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Bonjour ! Je suis Sarah. Planning, Tarifs, Conseils... Je t'écoute ! 🙂"
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question... (ex: Prix Reformer, Parking...)"):
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