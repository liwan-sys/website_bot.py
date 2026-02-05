import streamlit as st
import google.generativeai as genai

# ==========================================
# 🧠 LA BIBLE DU STUDIO
# ==========================================
INFO_STUDIO = """
=== 1. CONCEPTS & LIEUX ===
NOM : SVB (Santez-Vous Bien).
AMBIANCE : "Le bien-être au quotidien". Cocon, Premium.
CONTACT : 07 44 91 91 55 | hello@studiosvb.fr
RÉSERVATION : Sur l'appli membre ou Calendly pour l'essai.

📍 LIEU 1 : "COURS LAVANDIÈRES" (40 Cours des Lavandières, St Ouen)
- C'est le studio des MACHINES (Reformer, Crossformer) et du YOGA.

📍 LIEU 2 : "PARC DES DOCKS" (6 Mail André Breton, St Ouen)
- C'est le studio du SOL (Cross Training, Boxe, Kids) et du COACHING.

=== 2. DICTIONNAIRE : ACTIVITÉ vs ABONNEMENT ===
🔴 "CROSS TRAINING" = Le SPORT (Intensité, cardio, au sol).
🔴 "PASS CROSS" = L'ABONNEMENT (La formule pour accéder au Cross Training).

=== 3. LES TARIFS & ABONNEMENTS (PRÉCIS) ===

⭐️ OFFRE DÉCOUVERTE
- "NEW PASS STARTER" : 99,90€ (5 sessions, 1 mois). Sans engagement.

🚀 OPTION "SVB BOOST" (+9,90€/mois)
- Avantages : FRAIS D'INSCRIPTION OFFERTS (au lieu de 49€) + 1 invité gratuit/mois + Suspension possible.

🎫 PASS MENSUELS (Engagement 3 mois)
1. PASS CROSS (Accès Training Sol)
   - 1x/sem (4 sess) : 60,30€
   - 2x/sem (8 sess) : 116,30€

2. PASS REFORMER (Accès Machine Reformer)
   - 1x/sem (4 sess) : 136,30€
   - 2x/sem (8 sess) : 256,30€

3. PASS CROSSFORMER (Accès Machine Intense)
   - 2x/sem (8 sess) : 288,30€

👶 PASS KIDS (Hors été)
- 2 sessions : 35,30€ | 4 sessions : 65,30€

=== 4. RÈGLEMENT ===
- ANNULATION : 1H avant (Small Group) / 24H avant (Privé).
- RETARD : +5 min = Refusé.
- CHAUSSETTES : Obligatoires aux Lavandières.
"""

# ==========================================
# ⚙️ MOTEUR TECHNIQUE
# ==========================================
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

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
    border: none;
}
.stButton button:hover {
    background-color: #1ebc57;
    color: white;
}
</style>
""", unsafe_allow_html=True)

api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Message d'accueil (Le SEUL moment où elle dit Bonjour)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais tout sur nos plannings, tarifs et règles. Comment puis-je vous aider ?"}
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
            
            # --- CERVEAU (RÈGLE "PAS DE BONJOUR" AJOUTÉE) ---
            system_prompt = f"""
            Tu es Sarah, l'hôte d'accueil de SVB.
            DONNÉES : {INFO_STUDIO}
            
            CONSIGNES STRICTES :
            1. ⛔️ NE DIS PLUS "Bonjour", "Ravi de vous revoir" ou "Bienvenue" à chaque réponse. Entre directement dans le sujet. Sois directe et fluide.
            2. Distingue bien SPORT (Activité) et ABONNEMENT (Prix).
            3. Si on demande à parler à un humain/Laura -> Code [HUMAN_ALERT].
            4. Ton : Chaleureux mais concis.
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah..."):
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
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
            st.error("Petit bug, réessayez !")
    else:
        st.warning("Clé API manquante.")
