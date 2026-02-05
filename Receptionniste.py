import streamlit as st
import os

# ==============================================================================
# 1. SÉCURITÉ : VÉRIFICATION DU MODULE IA
# ==============================================================================
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR CRITIQUE : Le module 'google.generativeai' n'est pas installé.")
    st.stop()

# ==============================================================================
# 2. CONFIGURATION VISUELLE (DA DU SITE WEB)
# ==============================================================================

st.set_page_config(
    page_title="Sarah - Assistante SVB",
    page_icon="🧡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# INJECTION DU CSS (LE MAQUILLAGE DE SARAH)
st.markdown("""
<style>
    /* IMPORT DES POLICES GOOGLE (Pour le style manuscrit et le texte propre) */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lato:wght@400;700&display=swap');

    /* 1. FOND DE L'APPLICATION (DÉGRADÉ DOUX SAUGE/CRÈME) */
    .stApp {
        background: linear-gradient(180deg, #F9F7F2 0%, #E6F0E6 100%);
        font-family: 'Lato', sans-serif;
        color: #4A4A4A;
    }

    /* 2. CACHER LES ÉLÉMENTS PARASITES DE STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 3. STYLE DU TITRE "SARAH" */
    h1 {
        font-family: 'Dancing Script', cursive;
        color: #8FB592; /* Vert Sauge du logo */
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
        margin-top: -10px;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* 4. STYLE DES BULLES DE CHAT */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #EBC6A6; /* Bordure Pêche fine */
        border-radius: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Avatar de l'assistant */
    .stChatMessage .stAvatar {
        background-color: #EBC6A6 !important; /* Fond Pêche pour l'avatar */
    }

    /* 5. STYLE DE LA ZONE DE SAISIE */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 2px solid #8FB592 !important; /* Bordure verte */
    }

    /* 6. STYLE DES BOUTONS (WHATSAPP) */
    .stButton button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3) !important;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LA BIBLE DU STUDIO SVB (CONTENU INCHANGÉ)
# ==============================================================================
INFO_STUDIO = """
********************************************************************************
SECTION A : L'EXPÉRIENCE PREMIUM (DOUCHES & CONFORT)
********************************************************************************
NOM : SVB (Santez-Vous Bien).
CONTACT : 07 44 91 91 55 (WhatsApp).
PHILOSOPHIE : "Le bien-être au quotidien". Service tout inclus type "Hôtel".

IMPORTANT - LES DOUCHES ET LE CONFORT :
Contrairement aux salles classiques, le client n'a besoin de RIEN apporter.
1. STUDIO LAVANDIÈRES : 1 Douche disponible.
2. STUDIO DOCKS : 1 Douche disponible.
3. LE SERVICE PREMIUM : "Tout est déjà disponible sur place".
   - Serviettes de bain fournies.
   - Gel douche / Shampoing fournis.
   - Produits de soin fournis.
   - Sèche-cheveux disponible.
   -> Argument clé : "Venez les mains libres, vous repartez frais et dispo."

********************************************************************************
SECTION B : LOCALISATION EXACTE (NE PAS SE TROMPER)
********************************************************************************

📍 STUDIO A : "LAVANDIÈRES" (L'ESPACE ZEN)
- Adresse : 40 Cours des Lavandières, 93400 Saint-Ouen.
- C'est ici pour : 
  * Pilates Reformer (Machine).
  * Pilates Crossformer (Machine).
  * Yoga Vinyasa & Hatha.
  * Pilates Tapis (Classic, Power, Core).
- Règle : Chaussettes antidérapantes OBLIGATOIRES.

📍 STUDIO B : "DOCKS" (L'ESPACE INTENSITÉ)
- Adresse : 6 Mail André Breton, 93400 Saint-Ouen.
- C'est ici pour : 
  * Cross Training (Cardio).
  * Boxe & Danse (Afrodanc'All).
  * Yoga Kids / Training Kids.
  * Cross Yoga (Mélange yoga/renfo).

********************************************************************************
SECTION C : RÈGLEMENT INTÉRIEUR & SCÉNARIOS COMPLEXES
********************************************************************************

🛑 SCÉNARIO 1 : "JE VEUX UNE SÉANCE EN PLUS DE MON FORFAIT"
- Le client a un forfait 4 sessions mais veut en faire 5 ce mois-ci.
- RÉPONSE : "C'est possible ! Pas besoin de changer d'abonnement. Nous ajoutons la séance manuellement."
- PRIX : 30€ la séance à l'unité.

🛑 SCÉNARIO 2 : "JE VEUX FAIRE DU REFORMER ET DE LA BOXE"
- Ces deux activités ne sont pas dans le même pass standard.
- RÉPONSE : "Prenez deux abonnements (Un Pass Reformer + Un Pass Focus). Les prélèvements s'additionnent et vous profitez de tout !"
- Alternative : Le PASS FULL (si c'est Cross Training + Boxe).

🛑 SCÉNARIO 3 : "JE VEUX SUSPENDRE MON ABONNEMENT"
- CAS 1 (CLIENT BOOST) : Suspension immédiate, sans justificatif, sans préavis.
- CAS 2 (CLIENT STANDARD) : Suspension possible UNIQUEMENT SI absence > 10 jours ET Préavis d'un mois.

🛑 SCÉNARIO 4 : "ANNULATION & RETARD"
- Retard : Tolérance 5 minutes. Au-delà, porte fermée (sécurité).
- Annulation Cours Collectif : Possible jusqu'à 1H avant.
- Annulation Coaching Privé : Possible jusqu'à 24H avant.
- Si délai dépassé : Crédit perdu ("Use it or lose it").

🛑 SCÉNARIO 5 : "JE VEUX CHANGER DE FORMULE (PLUS OU MOINS DE SÉANCES)" -> RÈGLE STRICTE
- CAS A : UPGRADE (Augmenter son forfait)
  -> Exemple : Passer de 4 à 8 séances.
  -> RÉPONSE : "C'est possible IMMÉDIATEMENT, même pendant la période d'engagement."
- CAS B : DOWNGRADE (Baisser son forfait)
  -> Exemple : Passer de 4 à 2 séances.
  -> RÉPONSE : 
     1. PENDANT L'ENGAGEMENT (les 3 premiers mois) : ⛔️ IMPOSSIBLE. On ne peut pas baisser son abonnement tant que l'engagement n'est pas terminé.
     2. APRÈS L'ENGAGEMENT : Possible avec un préavis d'un mois.

********************************************************************************
SECTION D : GRILLE TARIFAIRE DÉTAILLÉE (ENGAGEMENT 3 MOIS)
********************************************************************************
Frais de dossier : 49€ (OFFERTS si Option Boost).

⭐️ OFFRE DÉCOUVERTE "NEW PASS STARTER"
- Prix : 99,90€.
- Inclus : 5 sessions au choix (Machine, Sol, Yoga...).
- Validité : 1 mois. Sans engagement.

🚀 OPTION "SVB BOOST" (+9,90€/MOIS)
- Avantages : Frais de dossier offerts + Suspension flexible + 1 Invité/mois.

--- DÉTAIL DES PASS MENSUELS ---

🟢 PASS CROSS (Sol Intense - Docks)
Inclus : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga.
- 2 sessions/mois : 30,30€
- 4 sessions/mois : 60,30€
- 6 sessions/mois : 90,30€
- 8 sessions/mois : 116,30€
- 10 sessions/mois : 145,30€
- 12 sessions/mois : 168,30€

🟡 PASS FOCUS (Technique & Arts - Mixte)
Inclus : Boxe, Afrodanc'All, Yoga, Pilates Tapis.
- 2 sessions/mois : 36,30€
- 4 sessions/mois : 72,30€
- 6 sessions/mois : 105,30€
- 8 sessions/mois : 136,30€
- 10 sessions/mois : 165,30€
- 12 sessions/mois : 192,30€

🟤 PASS REFORMER (Machine Zen - Lavandières)
Inclus : Pilates Reformer.
- 2 sessions/mois : 70,30€
- 4 sessions/mois : 136,30€
- 6 sessions/mois : 198,30€
- 8 sessions/mois : 256,30€
- 10 sessions/mois : 310,30€
- 12 sessions/mois : 360,30€

🟠 PASS CROSSFORMER (Machine Cardio - Lavandières)
Inclus : Pilates Crossformer.
- 2 sessions/mois : 78,30€
- 4 sessions/mois : 152,30€
- 6 sessions/mois : 222,30€
- 8 sessions/mois : 288,30€
- 10 sessions/mois : 350,30€
- 12 sessions/mois : 408,30€

🔵 PASS FULL (Combo Sol : Cross + Focus)
Inclus : Tout le Cross Training + Tout le Focus (Boxe/Yoga).
- 2 sessions/mois : 40,30€
- 4 sessions/mois : 80,30€
- 6 sessions/mois : 115,30€
- 8 sessions/mois : 150,30€
- 10 sessions/mois : 180,30€
- 12 sessions/mois : 210,30€

🟣 PASS FULL FORMER (Combo Machines)
Inclus : Reformer + Crossformer.
- 2 sessions/mois : 74,30€
- 4 sessions/mois : 144,30€
- 6 sessions/mois : 210,30€
- 8 sessions/mois : 272,30€
- 10 sessions/mois : 330,30€
- 12 sessions/mois : 384,30€

👶 PASS KIDS (Yoga & Training Enfants)
- 2 sessions : 35,30€
- 4 sessions : 65,30€
- Session sup : 18,30€

********************************************************************************
SECTION E : FAQ (QUESTIONS FRÉQUENTES)
********************************************************************************
Q: "Je suis débutant..."
R: "Aucun souci, c'est du Small Group (petits effectifs). Le coach adapte tout."

Q: "C'est cher..."
R: "C'est du semi-privé avec service tout inclus (douches, produits, coach expert)."

Q: "Je suis enceinte..."
R: "Privilégiez le Reformer ou le Yoga (avec avis médical). Évitez la Boxe/Cross."
"""

# ==============================================================================
# 4. MOTEUR D'INTELLIGENCE
# ==============================================================================

# Gestion de la clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Historique de conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais tout sur le studio : tarifs, plannings, et nos services premium (douches, confort...). Comment puis-je vous aider ?"}
    ]

# AFFICHAGE TITRE STYLISÉ
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>VOTRE ASSISTANTE SVB 24/7</div>", unsafe_allow_html=True)

# Affichage des bulles
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Votre question..."):
    # Sauvegarde message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Appel IA
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # CRÉATION DU CONTEXTE (MÉMOIRE)
            history_context = ""
            for msg in st.session_state.messages[-15:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # INSTRUCTIONS STRICTES AU CERVEAU
            system_prompt = f"""
            Tu es Sarah, l'experte du studio SVB.
            
            TA BIBLE ABSOLUE (NE RIEN INVENTER) : 
            {INFO_STUDIO}
            
            HISTORIQUE DE LA DISCUSSION :
            {history_context}
            
            TES RÈGLES DE RÉPONSE :
            1. **DOUCHES & CONFORT** : Rappelle que TOUT est fourni (Serviettes, Gel douche, Shampoing).
            2. **MODIFICATION ABONNEMENT** : 
               - **UPGRADE** (Augmenter) : POSSIBLE tout de suite.
               - **DOWNGRADE** (Baisser) : **INTERDIT** pendant la période d'engagement (3 mois).
            3. **AJOUT SÉANCE** : Possible hors forfait (30€).
            4. **SUSPENSION** : Vérifie l'option BOOST (Sans préavis) vs STANDARD (1 mois préavis + 10j absence).
            5. **CUMUL** : Possible de prendre 2 abonnements.
            6. **TON** : Professionnel, Premium, Concis. Pas de "Bonjour" répétitif.
            7. **HUMAIN** : Si le client s'énerve ou demande Laura -> Finis par [HUMAN_ALERT].
            
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
                        st.link_button("📞 Parler à Laura (WhatsApp)", "https://wa.me/33744919155")
        except Exception as e:
            st.error(f"Erreur technique : {e}")
    else:
        st.warning("Clé API manquante.")
