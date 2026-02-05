import streamlit as st
import google.generativeai as genai

# ==========================================
# 🧠 ZONE MÉMOIRE (PRÉCISION CHIRURGICALE)
# ==========================================
INFO_STUDIO = """
=== 1. L'UNIVERS SVB ===
NOM : SVB (Santez-Vous Bien).
CONTACT HUMAIN : Laura (WhatsApp 07 44 91 91 55).
AMBIANCE : "Cocon Sportif". Bienveillance, Premium, Douceur.

=== 2. DÉFINITIONS EXACTES (NE PAS CONFONDRE) ===
- "REFORMER" : C'est une MACHINE (Pilates sur chariot).
- "CROSSFORMER" : C'est une MACHINE (Cardio + Pilates intense).
- "TRAINING SOL" : C'est l'ACTIVITÉ sportive (Cross Training, Hyrox, au sol sans machine).
- "PASS CROSS" : C'est un ABONNEMENT (une formule tarifaire) qui donne accès aux cours de Training Sol. Ce n'est pas le nom du sport.

=== 3. LES OFFRES & TARIFS ===
--- OFFRE DÉCOUVERTE ---
- "New Pass Starter" : 99,90€ (5 séances, valable 1 mois). Sans engagement.

--- LES ABONNEMENTS (Engagement 3 mois) ---
1. L'Abonnement "PASS CROSS" (Accès Training Sol uniquement) :
   - Formule 1x/semaine : 60,30€/mois.
   - Formule 2x/semaine : 116,30€/mois.

2. L'Abonnement "REFORMER" (Accès Machine Reformer) :
   - Formule 1x/semaine : 136,30€/mois.
   - Formule 2x/semaine : 256,30€/mois.

3. L'Abonnement "CROSSFORMER" (Accès Machine Intense) :
   - Formule 2x/semaine : 288,30€/mois.

=== 4. RÈGLES IMPORTANTES ===
- CHAUSSETTES : Antidérapantes OBLIGATOIRES sur machines (Vente 10€).
- RETARD : Refusé après 5 min (Sécurité).
"""

# ==========================================
# ⚙️ MOTEUR TECHNIQUE
# ==========================================
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# Style (Bouton WhatsApp Vert)
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stButton button {
    background-color: #25D366;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# Clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je peux vous renseigner sur nos abonnements, nos machines ou le planning. Comment puis-je vous aider ?"}
    ]

# Titre
st.markdown("<h3 style='text-align: center; color: #EBC6A6;'>🧡 Bienvenue au Studio SVB</h3>", unsafe_allow_html=True)

# Affichage Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Votre question..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- CERVEAU AVEC CORRECTION LEXICALE ---
            system_prompt = f"""
            Tu es Sarah, hôte d'accueil SVB.
            MÉMOIRE STRICTE : {INFO_STUDIO}
            
            CONSIGNES DE RÉPONSE :
            1. FAIS LA DISTINCTION : Si on te demande "C'est quoi le Pass Cross ?", tu réponds que c'est un ABONNEMENT (une formule), pas un sport.
            2. Si le client veut parler à un humain/Laura/Téléphone : Ajoute le code [HUMAN_ALERT].
            3. Ton : Professionnel, Précis mais Doux ("Cocon").
            4. Ne donne que les infos présentes dans la mémoire.
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah vérifie..."):
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # Gestion du bouton humain
                    show_whatsapp_button = False
                    if "[HUMAN_ALERT]" in text_response:
                        show_whatsapp_button = True
                        text_response = text_response.replace("[HUMAN_ALERT]", "")
                    
                    st.markdown(text_response)
                    st.session_state.messages.append({"role": "assistant", "content": text_response})
                    
                    if show_whatsapp_button:
                        st.markdown("---")
                        st.link_button("📞 Parler à Laura (WhatsApp)", "https://wa.me/33744919155")
        except:
            st.error("Petit bug technique, réessayez !")
    else:
        st.warning("Clé API manquante.")

