import streamlit as st
import os

# ==============================================================================
# 1. SÉCURITÉ & DÉPENDANCES
# ==============================================================================
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR : Le module 'google.generativeai' est manquant.")
    st.stop()

# ==============================================================================
# 2. DESIGN & IDENTITÉ VISUELLE (DA SITE WEB)
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

st.markdown("""
<style>
    /* IMPORT POLICES (Style Manuscrit + Texte Pro) */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

    /* FOND DÉGRADÉ (SAUGE / CRÈME) */
    .stApp {
        background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
        font-family: 'Lato', sans-serif;
        color: #4A4A4A;
    }
    
    /* MASQUER LES ÉLÉMENTS STREAMLIT */
    #MainMenu, footer, header {visibility: hidden;}

    /* TITRE SARAH STYLISÉ */
    h1 {
        font-family: 'Dancing Script', cursive;
        color: #8FB592; /* Vert Sauge */
        text-align: center;
        font-size: 3.5rem !important;
        margin-bottom: 0px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #EBC6A6; /* Pêche */
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* BULLES DE CHAT ÉLÉGANTES */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9);
        border: 1px solid #EBC6A6;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* BOUTON WHATSAPP */
    .stButton button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px;
        font-weight: bold;
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LA BIBLE SVB - VERSION FUSION (INTELLIGENTE & NEUTRE)
# ==============================================================================

INFO_STUDIO = """
********************************************************************************
SECTION A : L'EXPÉRIENCE STUDIO (SERVICE TOUT INCLUS)
********************************************************************************
NOM : SVB (Santez-Vous Bien).
CONTACT : WhatsApp uniquement (07 44 91 91 55).
POSITIONNEMENT : Studio Premium, Semi-Privé, Suivi personnalisé.

LE SERVICE CONFORT "HÔTEL" :
Argument clé : "Le client vient les mains vides."
- Douches : Disponibles dans les 2 studios.
- Fourni sur place : Serviettes de bain, Gel douche, Shampoing, Sèche-cheveux.

********************************************************************************
SECTION B : LES DEUX ADRESSES (NE PAS SE TROMPER)
********************************************************************************
📍 STUDIO "LAVANDIÈRES" (40 Cours des Lavandières)
- Ambiance : Zen, Concentration.
- Activités : Pilates Reformer (Machine), Crossformer (Machine), Yoga, Pilates Tapis.
- Obligation : Chaussettes antidérapantes.

📍 STUDIO "DOCKS" (6 Mail André Breton)
- Ambiance : Intensité, Énergie.
- Activités : Cross Training, Boxe, Danse (Afrodanc'All), Yoga Kids, Cross Yoga.
- Note : Situé à 5 min à pied du premier studio.

********************************************************************************
SECTION C : RÈGLEMENT INTÉRIEUR & GESTION (STRICT)
********************************************************************************

🛑 1. AJOUT DE SÉANCE HORS FORFAIT
- Règle : Possible pour tout abonné.
- Tarif : 30€ la séance à l'unité.

🛑 2. MODIFICATION D'ABONNEMENT (RÈGLE FINANCIÈRE)
- UPGRADE (Passer à un forfait supérieur) : Possible IMMÉDIATEMENT.
- DOWNGRADE (Passer à un forfait inférieur) : STRICTEMENT INTERDIT pendant les 3 mois d'engagement. Possible après (préavis 1 mois).

🛑 3. SUSPENSION (PAUSE VACANCES)
- Si Option BOOST : Suspension immédiate et libre.
- Si Standard : Suspension possible UNIQUEMENT si absence > 10 jours ET Préavis d'un mois.

🛑 4. RETARD & ANNULATION
- Retard : Refusé après 5 min (Porte fermée).
- Annulation : 1h avant (Collectif) / 24h avant (Privé). Sinon perdu.

🛑 5. CUMUL
- Possible de cumuler 2 abonnements (ex: Reformer + Boxe).

********************************************************************************
SECTION D : GRILLE TARIFAIRE DÉTAILLÉE (ENGAGEMENT 3 MOIS)
********************************************************************************
Frais de dossier : 49€ (OFFERTS avec Option Boost).

⭐️ OFFRE DÉCOUVERTE "NEW PASS STARTER" : 99,90€ (5 sessions, 1 mois).
🚀 OPTION BOOST : +9,90€/mois (Frais offerts, Suspension libre, 1 Invité).

--- TARIFS MENSUELS ---

🟢 PASS CROSS (Sol Intense - Docks)
(Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga).
- 2 sessions : 30,30€ | 4 sessions : 60,30€
- 6 sessions : 90,30€ | 8 sessions : 116,30€
- 10 sessions : 145,30€ | 12 sessions : 168,30€

🟡 PASS FOCUS (Technique & Arts - Mixte)
(Boxe, Danse, Yoga, Pilates Tapis).
- 2 sessions : 36,30€ | 4 sessions : 72,30€
- 6 sessions : 105,30€ | 8 sessions : 136,30€
- 10 sessions : 165,30€ | 12 sessions : 192,30€

🟤 PASS REFORMER (Machine Zen - Lavandières)
(Pilates Reformer).
- 2 sessions : 70,30€ | 4 sessions : 136,30€
- 6 sessions : 198,30€ | 8 sessions : 256,30€
- 10 sessions : 310,30€ | 12 sessions : 360,30€

🟠 PASS CROSSFORMER (Machine Cardio - Lavandières)
(Pilates Crossformer).
- 2 sessions : 78,30€ | 4 sessions : 152,30€
- 6 sessions : 222,30€ | 8 sessions : 288,30€
- 10 sessions : 350,30€ | 12 sessions : 408,30€

🔵 PASS FULL (Combo Sol : Cross + Focus)
- 2 sessions : 40,30€ | 4 sessions : 80,30€
- 6 sessions : 115,30€ | 8 sessions : 150,30€
- 10 sessions : 180,30€ | 12 sessions : 210,30€

🟣 PASS FULL FORMER (Combo Machines)
- 2 sessions : 74,30€ | 4 sessions : 144,30€
- 6 sessions : 210,30€ | 8 sessions : 272,30€
- 10 sessions : 330,30€ | 12 sessions : 384,30€

👶 PASS KIDS
- 2 sessions : 35,30€ | 4 sessions : 65,30€

********************************************************************************
SECTION E : RÉPONSES AUX CAS PARTICULIERS
********************************************************************************
- ENCEINTE : Conseiller Reformer (avec avis médical) ou Yoga Doux. Déconseiller Boxe/Cross.
- DÉBUTANT : Rassurer sur le "Small Group" (Le coach adapte tout).
- REPORT : Pas de report de séances sur le mois suivant (Use it or lose it).
"""

# ==============================================================================
# 4. LE CERVEAU DE SARAH
# ==============================================================================

api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Message d'accueil (Neutre et Pro)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour, je suis Sarah, l'assistante virtuelle SVB. Je peux vous renseigner sur les tarifs, les plannings et le fonctionnement du studio. Quelle est votre question ?"}
    ]

# Affichage Titre
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>VOTRE ASSISTANTE SVB</div>", unsafe_allow_html=True)

# Affichage Historique
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
            
            # Mémoire
            history_context = ""
            for msg in st.session_state.messages[-15:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # Instructions Système (Cerveau)
            system_prompt = f"""
            Tu es Sarah, l'assistante experte du studio SVB.
            
            TA BIBLE (NE RIEN INVENTER) : 
            {INFO_STUDIO}
            
            HISTORIQUE :
            {history_context}
            
            CONSIGNES STRICTES :
            1. **NEUTRE & PRO** : Pas de "Cocon", pas de "Shanaël", pas de "Laura". Tu parles au nom de "L'équipe".
            2. **CONFORT** : Rappelle que TOUT est fourni (Serviettes, Gel douche...).
            3. **RÈGLES FINANCIÈRES** : 
               - UPGRADE = OUI. 
               - DOWNGRADE = NON (pendant les 3 mois d'engagement).
            4. **SUSPENSION** : Vérifie l'option BOOST (Sans préavis) vs STANDARD (1 mois préavis).
            5. **PRIX** : Utilise les montants exacts.
            6. **HUMAIN** : Si besoin d'escalade -> [HUMAN_ALERT].
            
            Réponds au CLIENT :
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah réfléchit..."):
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
                        st.link_button("📞 Contacter l'accueil (WhatsApp)", "https://wa.me/33744919155")
        except:
            st.error("Erreur technique.")
    else:
        st.warning("Clé API manquante.")
