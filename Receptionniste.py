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
    /* IMPORT POLICES */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

    /* FOND DÉGRADÉ (SAUGE / CRÈME) */
    .stApp {
        background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
        font-family: 'Lato', sans-serif;
        color: #4A4A4A;
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* TITRE SARAH */
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
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* BULLES DE CHAT (LISIBILITÉ MAXIMALE) */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #EBC6A6;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #1f1f1f !important; /* NOIR FORCÉ */
    }
    
    .stChatMessage p, .stChatMessage li {
        color: #1f1f1f !important; /* NOIR FORCÉ */
        line-height: 1.6;
    }

    /* BOUTON WHATSAPP */
    .stButton button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 12px 25px;
        font-weight: bold;
        width: 100%;
        text-transform: uppercase;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LA BIBLE SVB - VERSION "EXPERTE VENTE & ARGUMENTATION"
# ==============================================================================

INFO_STUDIO = """
********************************************************************************
CHAPITRE 1 : IDENTITÉ & POSITIONNEMENT
********************************************************************************
NOM : SVB (Santez-Vous Bien).
CONTACT : WhatsApp uniquement (07 44 91 91 55).
POSITIONNEMENT : Studio Premium, Semi-Privé.

LE SERVICE "ALL INCLUSIVE" (ARGUMENT LUXE) :
- Douches : Disponibles aux 2 studios.
- Fourni : Serviettes, Gel douche, Shampoing, Sèche-cheveux, Déodorant.
- Phrase type : "Venez les mains vides, on s'occupe de tout."

********************************************************************************
CHAPITRE 2 : STRATÉGIE TARIFAIRE & ARGUMENTAIRE DE VENTE (CRUCIAL)
********************************************************************************

🚨 RÈGLE D'OR : NE JAMAIS DONNER LE PRIX À L'UNITÉ SEUL.
Le prix à l'unité (50€) est fait pour être dissuasif et vendre l'abonnement.

SCÉNARIO : "Quel est le prix d'une séance ?"
1. D'ABORD, donner le prix public : "La séance à la carte est à 50€."
2. ENSUITE, casser ce prix : "Cependant, ce n'est pas l'option que je vous conseille."
3. ARGUMENTER avec l'abonnement : "En prenant un abonnement (même petit), le prix de la séance chute immédiatement (environ 35€/séance). C'est bien plus rentable."
4. RAPPELER l'avantage membre : "Et une fois abonné(e), si vous voulez rajouter des séances, elles ne sont qu'à 30€ !"

TABLEAU COMPARATIF (POUR TES CALCULS MENTAUX) :
- Séance Machine à l'unité (Non membre) : 50€ (CHER ❌)
- Séance Machine dans un Pass Reformer 2 : revient à 35€ (RENTABLE ✅)
- Séance Machine ajoutée par un Membre : 30€ (TRÈS RENTABLE ⭐️)

********************************************************************************
CHAPITRE 3 : LES DEUX STUDIOS
********************************************************************************
📍 STUDIO "LAVANDIÈRES" (ZEN)
- 40 Cours des Lavandières.
- Activités : Pilates Reformer, Crossformer, Yoga, Tapis.
- Chaussettes antidérapantes obligatoires.

📍 STUDIO "DOCKS" (ÉNERGIE)
- 6 Mail André Breton.
- Activités : Cross Training, Boxe, Danse, Yoga Kids.
- Situé à 5 min à pied.

********************************************************************************
CHAPITRE 4 : RÈGLEMENT INTÉRIEUR STRICT
********************************************************************************
1. AJOUT DE SÉANCE HORS FORFAIT
- Possible pour tout abonné. Tarif unique : 30€.

2. MODIFICATION D'ABONNEMENT
- UPGRADE (Monter) : Possible TOUT DE SUITE.
- DOWNGRADE (Baisser) : INTERDIT pendant les 3 mois d'engagement.

3. SUSPENSION
- Option BOOST : Immédiat, sans motif.
- Standard : Préavis 1 mois + Absence > 10 jours.

4. ANNULATION
- 1h avant (Collectif) / 24h avant (Privé). Sinon perdu.

********************************************************************************
CHAPITRE 5 : GRILLE TARIFAIRE (ENGAGEMENT 3 MOIS)
********************************************************************************
Frais de dossier : 49€ (OFFERTS avec Option Boost).

⭐️ OFFRE DÉCOUVERTE "NEW PASS STARTER" : 99,90€ (5 sessions, 1 mois).
-> Soit 19,98€ la séance ! (L'offre la plus attractive pour commencer).

🚀 OPTION BOOST : +9,90€/mois (Frais offerts, Suspension libre, 1 Invité).

--- DÉTAIL DES PASS MENSUELS ---

🟢 PASS CROSS (Docks - Sol Intense)
(Cross Training, Cross Core, Body, Rox, Yoga).
- 2 sessions : 30,30€ (soit 15€/s)
- 4 sessions : 60,30€
- 6 sessions : 90,30€
- 8 sessions : 116,30€
- 10 sessions : 145,30€
- 12 sessions : 168,30€

🟡 PASS FOCUS (Mixte - Technique)
(Boxe, Danse, Yoga, Pilates Tapis).
- 2 sessions : 36,30€ (soit 18€/s)
- 4 sessions : 72,30€
- 6 sessions : 105,30€
- 8 sessions : 136,30€
- 10 sessions : 165,30€
- 12 sessions : 192,30€

🟤 PASS REFORMER (Lavandières - Machine Zen)
(Pilates Reformer).
- 2 sessions : 70,30€ (soit 35€/s -> Compare ça aux 50€ à l'unité !)
- 4 sessions : 136,30€
- 6 sessions : 198,30€
- 8 sessions : 256,30€
- 10 sessions : 310,30€
- 12 sessions : 360,30€

🟠 PASS CROSSFORMER (Lavandières - Machine Cardio)
(Pilates Crossformer).
- 2 sessions : 78,30€
- 4 sessions : 152,30€
- 6 sessions : 222,30€
- 8 sessions : 288,30€
- 10 sessions : 350,30€
- 12 sessions : 408,30€

🔵 PASS FULL (Combo Sol : Cross + Focus)
- 2 sessions : 40,30€
- 4 sessions : 80,30€
- 6 sessions : 115,30€
- 8 sessions : 150,30€
- 10 sessions : 180,30€
- 12 sessions : 210,30€

🟣 PASS FULL FORMER (Combo Machines)
- 2 sessions : 74,30€
- 4 sessions : 144,30€
- 6 sessions : 210,30€
- 8 sessions : 272,30€
- 10 sessions : 330,30€
- 12 sessions : 384,30€

👶 PASS KIDS
- 2 sessions : 35,30€ | 4 sessions : 65,30€

********************************************************************************
CHAPITRE 6 : FAQ & RÉPONSES AUX OBJECTIONS
********************************************************************************
- "C'EST QUOI LE CROSSFORMER ?" : "C'est du Pilates sur machine, mais cardio et intense. On transpire !"
- "JE SUIS DÉBUTANT" : "Pas de souci, c'est du Small Group. Le coach s'adapte."
- "REPORT ?" : "Non, pas de report (Use it or lose it)."
- "ENCEINTE ?" : "Reformer ou Yoga OK. Pas de Boxe/Cross."
"""

# ==============================================================================
# 4. LE CERVEAU DE SARAH (CONFIGURATION IA DE VENTE)
# ==============================================================================

api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Message d'accueil engageant
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je suis là pour vous aider à trouver la meilleure formule pour vous (Tarifs, Planning, Infos). Dites-moi ce que vous recherchez !"}
    ]

# Affichage Titre
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>VOTRE ASSISTANTE SVB</div>", unsafe_allow_html=True)

# Affichage Historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Posez votre question..."):
    
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

            # INSTRUCTIONS SYSTÈME "COMMERCIALE"
            system_prompt = f"""
            Tu es Sarah, l'assistante commerciale du studio SVB.
            
            TA BIBLE (SOURCE DE VÉRITÉ) : 
            {INFO_STUDIO}
            
            HISTORIQUE :
            {history_context}
            
            TES MISSIONS PRIORITAIRES :
            1. **TECHNIQUE DE VENTE (PRIX UNITAIRE)** : 
               - Si on demande le prix d'une séance (50€), tu DOIS immédiatement dire que c'est le tarif public "à la carte" et qu'il est bien plus avantageux de s'abonner (ça revient à ~35€).
               - Précise que pour les membres, l'ajout est à 30€.
            2. **TON NEUTRE & PRO** : Tu parles au nom de "L'équipe". Pas de noms propres.
            3. **SERVICE CONFORT** : Rappelle que TOUT est fourni (Serviettes, Gel douche...). C'est un argument pour justifier le prix.
            4. **RÈGLES** : Upgrade = OUI / Downgrade = NON (pendant engagement).
            5. **HUMAIN** : Si besoin -> [HUMAN_ALERT].
            
            Réponds au CLIENT avec ces arguments :
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
                        st.link_button("📞 Contacter l'équipe (WhatsApp)", "https://wa.me/33744919155")
        except:
            st.error("Erreur technique.")
    else:
        st.warning("Clé API manquante.")
