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
# 2. DESIGN & IDENTITÉ VISUELLE (CONFORME AU SITE WEB)
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡", layout="centered")

st.markdown("""
<style>
    /* POLICES : Dancing Script (Titre) & Lato (Texte) comme sur le site */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

    /* FOND DÉGRADÉ VERT SAUGE / CRÈME */
    .stApp {
        background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
        font-family: 'Lato', sans-serif;
        color: #4A4A4A;
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* TITRE */
    h1 {
        font-family: 'Dancing Script', cursive;
        color: #8FB592;
        text-align: center;
        font-size: 3.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #EBC6A6;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* BULLES DE CHAT */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border: 1px solid #EBC6A6;
        border-radius: 15px;
        padding: 15px;
        color: #1f1f1f !important; /* Force le noir pour lisibilité */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .stChatMessage p, .stChatMessage li {
        color: #1f1f1f !important;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* BOUTON WHATSAPP */
    .stButton button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        border: none;
        border-radius: 50px;
        padding: 12px 25px;
        font-weight: bold;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(37, 211, 102, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LA BIBLE DU STUDIO - VERSION "ANALYSE SITE WEB"
# ==============================================================================

INFO_STUDIO = """
********************************************************************************
SECTION A : L'IDENTITÉ & LES SERVICES (DATA SITE WEB)
********************************************************************************
NOM : SVB (Santez-Vous Bien).
CONTACT : WhatsApp uniquement (07 44 91 91 55).
POSITIONNEMENT : Studio Premium, "Lieu de vie", Semi-Privé.

💎 LE SERVICE PREMIUM ("COMME À L'HÔTEL") :
C'est un argument fort du site.
- DOUCHES : Oui, disponibles dans les 2 studios (Lavandières & Docks).
- TOUT INCLUS : Serviettes de bain, Gel douche, Shampoing, Sèche-cheveux, Déodorant.
- PHRASE CLÉ : "Venez les mains vides, repartez frais et dispo."

********************************************************************************
SECTION B : LES DEUX STUDIOS (DISTINCTION CLAIRE)
********************************************************************************
📍 STUDIO 1 : "COURS DES LAVANDIÈRES" (L'ESPACE ZEN)
- Adresse : 40 Cours des Lavandières, 93400 Saint-Ouen.
- Ambiance : Feutrée, Apaisante, Cocon.
- Activités : 
  * Pilates Reformer (Machine)
  * Pilates Crossformer (Machine)
  * Yoga (Vinyasa, Hatha)
  * Pilates Tapis.
- Équipement : Chaussettes antidérapantes OBLIGATOIRES.

📍 STUDIO 2 : "PARC DES DOCKS" (L'ESPACE ÉNERGIE)
- Adresse : 6 Mail André Breton, 93400 Saint-Ouen.
- Ambiance : Moderne, Dynamique.
- Activités : 
  * Cross Training (HIIT)
  * Boxe & Cardio
  * Danse (Afrodanc'All)
  * Yoga Kids / Training Kids.
- Note : Situé à 5 min à pied du premier studio.

********************************************************************************
SECTION C : RÈGLEMENT & GESTION DES MEMBRES
********************************************************************************

🛑 1. PRIX À L'UNITÉ (LA RÈGLE SUBTILE DU SITE)
- PRIX PUBLIC (Non-Membre) :
  * Séance Reformer / Crossformer = 50€ (Affiché sur le site).
  * Séance Cross / Focus = 30€.
- PRIX MEMBRE (Ajout sur forfait) :
  * Tarif unique privilège = 30€ (Quelle que soit l'activité).

🛑 2. MODIFICATION D'ABONNEMENT
- UPGRADE (Monter en gamme) : Possible tout de suite.
- DOWNGRADE (Baisser en gamme) : INTERDIT pendant les 3 mois d'engagement.

🛑 3. SUSPENSION (PAUSE)
- OPTION BOOST : Suspension immédiate et illimitée.
- STANDARD (Sans Boost) : Préavis 1 mois + Absence > 10 jours requise.

🛑 4. RETARD & ANNULATION
- Retard : Tolérance 0 après 5 minutes (Porte fermée).
- Annulation : 1h avant (Collectif) / 24h avant (Privé).

🛑 5. CUMUL (STRATÉGIE COMMERCIALE)
- "Je veux faire Reformer + Boxe" -> Proposer 2 abonnements (Pass Reformer + Pass Focus). C'est la meilleure flexibilité.

********************************************************************************
SECTION D : GRILLE TARIFAIRE (ENGAGEMENT 3 MOIS)
********************************************************************************
Frais de dossier : 49€ (OFFERTS avec Option Boost).

🔥 L'OFFRE STAR DU SITE : "NEW PASS STARTER"
- Prix : 99,90€ (Paiement unique).
- Contenu : 5 sessions au choix (Machine, Sol, Yoga...).
- Validité : 1 mois. Sans engagement.

🚀 OPTION BOOST : +9,90€/mois (Frais offerts, Suspension libre, 1 Invité/mois).

--- ABONNEMENTS MENSUELS ---

🟢 PASS CROSS (Docks - Sol Intense)
(Cross Training, Cross Core, Body, Rox, Yoga).
- 2 sessions : 30,30€ | 4 sessions : 60,30€
- 6 sessions : 90,30€ | 8 sessions : 116,30€
- 10 sessions : 145,30€ | 12 sessions : 168,30€

🟡 PASS FOCUS (Mixte - Technique)
(Boxe, Danse, Yoga, Pilates Tapis).
- 2 sessions : 36,30€ | 4 sessions : 72,30€
- 6 sessions : 105,30€ | 8 sessions : 136,30€
- 10 sessions : 165,30€ | 12 sessions : 192,30€

🟤 PASS REFORMER (Lavandières - Machine Zen)
(Pilates Reformer).
- 2 sessions : 70,30€ | 4 sessions : 136,30€
- 6 sessions : 198,30€ | 8 sessions : 256,30€
- 10 sessions : 310,30€ | 12 sessions : 360,30€

🟠 PASS CROSSFORMER (Lavandières - Machine Cardio)
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
SECTION E : FAQ & SCÉNARIOS
********************************************************************************
- "C'EST QUOI LE CROSSFORMER ?" : "C'est du Pilates sur machine, mais en version cardio et intense. On transpire !"
- "JE SUIS DÉBUTANT" : "Nos cours sont en 'Small Group' (petit comité). Le coach s'adapte à vous."
- "REPORT DE SÉANCE ?" : "Non, les séances ne se reportent pas d'un mois à l'autre."
"""

# ==============================================================================
# 4. LE CERVEAU DE SARAH (LOGIQUE)
# ==============================================================================

api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Message d'accueil aligné avec le site
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je peux vous guider sur nos offres (Starter, Abonnements), nos plannings ou nos services. Par quoi commençons-nous ?"}
    ]

# TITRE
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>VOTRE ASSISTANTE SVB 24/7</div>", unsafe_allow_html=True)

# HISTORIQUE
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ZONE DE SAISIE
if prompt := st.chat_input("Votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Contexte
            history_context = ""
            for msg in st.session_state.messages[-15:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # Instructions Système
            system_prompt = f"""
            Tu es Sarah, l'assistante du studio SVB.
            
            TA BIBLE (DONNÉES SITE WEB) : 
            {INFO_STUDIO}
            
            HISTORIQUE :
            {history_context}
            
            CONSIGNES STRICTES :
            1. **PRIX UNITAIRE** : Attention à la nuance !
               - Si on demande le prix public d'une séance machine : 50€.
               - Si c'est un membre qui veut ajouter une séance : 30€.
            2. **NEUTRE & PRO** : Tu parles au nom de "L'équipe". Pas de noms propres.
            3. **CONFORT** : Rappelle que TOUT est fourni (Serviettes, Gel douche...). C'est un point fort du site.
            4. **SUSPENSION & RÈGLES** : Applique strictement les règles de la Bible.
            5. **HUMAIN** : Si besoin d'escalade -> [HUMAN_ALERT].
            
            Réponds au CLIENT :
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah consulte..."):
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
                        st.link_button("📞 Contacter l'équipe (WhatsApp)", "https://wa.me/33744919155")
        except:
            st.error("Erreur technique.")
    else:
        st.warning("Clé API manquante.")
