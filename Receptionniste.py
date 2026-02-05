import streamlit as st
import google.generativeai as genai

# ==========================================
# 🧠 ZONE MÉMOIRE DU STUDIO
# ==========================================
INFO_STUDIO = """
=== 1. L'UNIVERS SVB (SANTEZ-VOUS BIEN) ===
NOM : SVB (Santez-Vous Bien).
PHILOSOPHIE : "Investissez en vous-même".
AMBIANCE : "Cocon Sportif". Pêche, Sauge, Bienveillance.
CONTACT HUMAIN (LAURA) : WhatsApp au 07 44 91 91 55.

=== 2. LES DISCIPLINES ===
- REFORMER : Pilates sur machine. Allonge et renforce.
- CROSSFORMER : Cardio + Pilates intense sur machine.
- PASS CROSS : Training au sol fonctionnel.
- YOGA : Vinyasa/Hatha.

=== 3. TARIFS & OFFRES ===
- OFFRE STAR : "New Pass Starter" à 99,90€ (5 séances, 1 mois).
- ABONNEMENTS (Eng 3 mois) :
  * Reformer 1x : 136,30€/mois.
  * Crossformer 2x : 288,30€/mois.
  * Pass Cross 1x : 60,30€/mois.

=== 4. RÈGLES ===
- CHAUSSETTES : Antidérapantes OBLIGATOIRES.
- RETARD : Refusé après 5 min.
"""

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# Style CSS pour cacher les menus et styliser le bouton WhatsApp
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

# Initialisation Historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je peux vous renseigner sur le planning, les tarifs ou nos machines. Comment puis-je vous aider ?"}
    ]

# Titre
st.markdown("<h3 style='text-align: center; color: #EBC6A6;'>🧡 Bienvenue au Studio SVB</h3>", unsafe_allow_html=True)

# Affichage des messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 💬 TRAITEMENT DU MESSAGE
# ==========================================
if prompt := st.chat_input("Votre question..."):
    
    # 1. Afficher message client
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Réponse de Sarah
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- CERVEAU AVEC DÉTECTEUR D'HUMAIN ---
            system_prompt = f"""
            Tu es Sarah, hôte d'accueil SVB.
            MÉMOIRE : {INFO_STUDIO}
            
            RÈGLES SPÉCIALES :
            1. Si l'utilisateur demande à parler à un "humain", "quelqu'un", "Laura", "téléphone" ou s'il est énervé :
               -> Réponds une phrase rassurante.
               -> AJOUTE À LA FIN DE TA PHRASE CE CODE EXACTEMENT : [HUMAN_ALERT]
            
            2. Sinon, réponds normalement avec les infos du studio, poliment et doucement.
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah réfléchit..."):
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # DÉTECTION DU CODE SECRET
                    show_whatsapp_button = False
                    if "[HUMAN_ALERT]" in text_response:
                        show_whatsapp_button = True
                        text_response = text_response.replace("[HUMAN_ALERT]", "") # On enlève le code pour que le client ne le voie pas
                    
                    # Affichage du texte
                    st.markdown(text_response)
                    st.session_state.messages.append({"role": "assistant", "content": text_response})
                    
                    # Affichage du Bouton SI nécessaire
                    if show_whatsapp_button:
                        st.markdown("---")
                        st.link_button("📞 Parler à Laura (WhatsApp)", "https://wa.me/33744919155")
                        
        except:
            st.error("Oups, je reviens vite !")
    else:
        st.warning("Clé API manquante.")
