import streamlit as st
import os
import datetime

# ==============================================================================
# 🛡️ SÉCURITÉ & INSTALLATION
# ==============================================================================
# Vérification de la présence du module Google Generative AI
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR CRITIQUE : Le module 'google.generativeai' n'est pas installé.")
    st.warning("Veuillez créer un fichier 'requirements.txt' contenant la ligne : google-generativeai")
    st.stop()

# ==============================================================================
# 📚 LA GRANDE ENCYCLOPÉDIE DU STUDIO SVB (BASE DE DONNÉES)
# ==============================================================================
# Cette section contient TOUT LE SAVOIR du studio. 
# Elle est conçue pour couvrir 100% des questions clients.

INFO_STUDIO = """
********************************************************************************
CHAPITRE 1 : L'IDENTITÉ DU STUDIO (L'ADN SVB)
********************************************************************************
NOM COMMERCIAL : SVB (Santez-Vous Bien).
PHILOSOPHIE : "Le bien-être au quotidien". 
POSITIONNEMENT : Nous sommes un studio Premium, "Cocon Sportif". 
CE QUE NOUS NE SOMMES PAS : Une salle de sport classique "usine" (type Basic Fit). Ici, c'est du Small Group, du suivi, de l'humain.

COORDONNÉES OFFICIELLES :
- Téléphone (WhatsApp privilégié) : 07 44 91 91 55 (Demander Laura).
- Email : hello@studiosvb.fr
- Instagram : @svb.officiel

********************************************************************************
CHAPITRE 2 : NOS DEUX ADRESSES (NE PAS CONFONDRE)
********************************************************************************
Il est crucial de bien orienter le client selon son cours.

📍 ADRESSE 1 : "LES LAVANDIÈRES" (L'ESPACE ZEN & MACHINES)
- Adresse exacte : 40 Cours des Lavandières, 93400 Saint-Ouen.
- Ambiance : Calme, concentration, technique, douceur.
- Équipements : Machines Pilates (Reformers, Crossformers), Tapis épais.
- Vestiaires : Oui, disponibles pour se changer.
- COURS DISPENSÉS ICI :
  1. Pilates Reformer (Sur machine avec chariot).
  2. Pilates Crossformer (Cardio sur machine).
  3. Classic Pilates (Au sol, technique).
  4. Power Pilates (Au sol, intense).
  5. Core & Stretch (Mélange renforcement et souplesse).
  6. Yoga Vinyasa (Dynamique).
  7. Hatha Flow (Fluide).

📍 ADRESSE 2 : "LES DOCKS" (L'ESPACE INTENSITÉ & SOL)
- Adresse exacte : 6 Mail André Breton, 93400 Saint-Ouen.
- Ambiance : Énergique, musique, dynamique.
- Équipements : Sacs de frappe, Kettlebells, TRX, Espace sol.
- Douches : Oui, disponibles.
- COURS DISPENSÉS ICI :
  1. Cross Training (Circuit training haute intensité).
  2. Cross Core (Focus abdominaux et gainage).
  3. Cross Body (Renforcement musculaire global).
  4. Cross Rox (Mélange course et renfo - style Hyrox).
  5. Cross Yoga (Mélange Yoga et Renforcement - Attention, c'est aux Docks !).
  6. Boxe (Technique pieds-poings et cardio).
  7. Afrodanc'All (Danse cardio sur rythmes afro).
  8. Yoga Kids & Training Kids (Mercredi/Samedi).

********************************************************************************
CHAPITRE 3 : RÈGLEMENT INTÉRIEUR & PROCÉDURES (STRICT)
********************************************************************************

🛑 RÈGLE N°1 : LA PONCTUALITÉ (SÉCURITÉ)
- La porte est fermée à clé 5 minutes après le début du cours.
- Pourquoi ? Pour la sécurité des affaires, pour ne pas déranger le groupe, et parce que l'échauffement est obligatoire.
- Conséquence : Si retard > 5 min, l'accès est refusé et la séance est décomptée.

🛑 RÈGLE N°2 : L'ANNULATION (RESPECT)
- Cours collectifs (Small Group) : Annulation gratuite jusqu'à 1 HEURE avant.
- Coaching Privé / Duo : Annulation gratuite jusqu'à 24 HEURES avant.
- Si le client annule après ce délai : Le crédit est perdu ("Late Cancel").
- Si le client ne vient pas sans prévenir : Le crédit est perdu ("No Show").

🛑 RÈGLE N°3 : LES CHAUSSETTES (HYGIÈNE)
- Aux Lavandières (Machines), les chaussettes antidérapantes sont OBLIGATOIRES.
- Si le client n'en a pas :
  * Achat définitif : 10€ la paire (Marque SVB).
  * Location (Prêt) : 3€ la paire. (Attention : Si non rendue à la fin, facturation de 10€).

🛑 RÈGLE N°4 : LA SUSPENSION D'ABONNEMENT (PAUSE)
SCÉNARIO A : Client avec OPTION BOOST (+9,90€/mois).
-> Droit à la suspension SANS PRÉAVIS. On met en pause quand on veut.
SCÉNARIO B : Client STANDARD (Sans option).
-> Droit à la suspension UNIQUEMENT SI : 
   1. L'absence dure plus de 10 jours.
   2. Le client prévient 1 MOIS à l'avance (Préavis).

🛑 RÈGLE N°5 : L'AJOUT DE SÉANCE (HORS FORFAIT)
- Un client abonné (ex: Pass 4 sessions) peut-il faire une 5ème séance ?
- OUI. Il n'est pas bloqué.
- Procédure : Contacter l'accueil.
- Tarif : Prix de la séance à l'unité (30€).

********************************************************************************
CHAPITRE 4 : ANALYSE DÉTAILLÉE DES PRIX (TARIFS 2025)
********************************************************************************
Tous les abonnements mensuels ont un ENGAGEMENT INITIAL DE 3 MOIS.
Frais de dossier à l'inscription : 49€ (OFFERTS si Option Boost).

💎 L'OPTION VIP : "SVB BOOST"
- Prix : +9,90€ / mois.
- Pourquoi la vendre ?
  1. Elle rembourse immédiatement les frais de dossier (49€ d'économie).
  2. Elle permet de suspendre l'abonnement en cas de vacances (sans préavis).
  3. Elle offre 1 séance "Invité" par mois pour venir avec un ami.
  4. Elle réduit l'engagement (2 mois coach / 3 mois small group).

--- CATÉGORIE 1 : LE "PASS CROSS" (SOL INTENSE - DOCKS) ---
Valable pour : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga.
(Exclut : Boxe, Reformer, Vinyasa).
-> 2 SESSIONS / MOIS : 30,30€ (Soit 15,15€ la séance).
-> 4 SESSIONS / MOIS : 60,30€ (Soit 15,07€ la séance).
-> 6 SESSIONS / MOIS : 90,30€ (Soit 15,05€ la séance).
-> 8 SESSIONS / MOIS : 116,30€ (Soit 14,53€ la séance).
-> 10 SESSIONS / MOIS : 145,30€ (Soit 14,53€ la séance).
-> 12 SESSIONS / MOIS : 168,30€ (Soit 14,02€ la séance).

--- CATÉGORIE 2 : LE "PASS FOCUS" (TECHNIQUE & ARTS - MIXTE) ---
Valable pour : BOXE (Docks), AFRODANC'ALL (Docks), YOGA (Lavandières), PILATES TAPIS (Lavandières).
-> 2 SESSIONS / MOIS : 36,30€ (Soit 18,15€ la séance).
-> 4 SESSIONS / MOIS : 72,30€ (Soit 18,07€ la séance).
-> 6 SESSIONS / MOIS : 105,30€ (Soit 17,55€ la séance).
-> 8 SESSIONS / MOIS : 136,30€ (Soit 17,03€ la séance).
-> 10 SESSIONS / MOIS : 165,30€ (Soit 16,53€ la séance).
-> 12 SESSIONS / MOIS : 192,30€ (Soit 16,02€ la séance).

--- CATÉGORIE 3 : LE "PASS REFORMER" (MACHINE ZEN - LAVANDIÈRES) ---
Valable pour : Pilates Reformer uniquement.
-> 2 SESSIONS / MOIS : 70,30€ (Soit 35,15€ la séance).
-> 4 SESSIONS / MOIS : 136,30€ (Soit 34,07€ la séance).
-> 6 SESSIONS / MOIS : 198,30€ (Soit 33,05€ la séance).
-> 8 SESSIONS / MOIS : 256,30€ (Soit 32,03€ la séance).
-> 10 SESSIONS / MOIS : 310,30€ (Soit 31,03€ la séance).
-> 12 SESSIONS / MOIS : 360,30€ (Soit 30,02€ la séance).

--- CATÉGORIE 4 : LE "PASS CROSSFORMER" (MACHINE CARDIO - LAVANDIÈRES) ---
Valable pour : Pilates Crossformer uniquement.
-> 2 SESSIONS / MOIS : 78,30€.
-> 4 SESSIONS / MOIS : 152,30€.
-> 6 SESSIONS / MOIS : 222,30€.
-> 8 SESSIONS / MOIS : 288,30€.
-> 10 SESSIONS / MOIS : 350,30€.
-> 12 SESSIONS / MOIS : 408,30€.

--- CATÉGORIE 5 : LE "PASS FULL" (COMBO SOL : CROSS + FOCUS) ---
Le choix idéal pour mixer Cardio (Cross) et Technique (Boxe/Yoga).
-> 2 SESSIONS / MOIS : 40,30€.
-> 4 SESSIONS / MOIS : 80,30€.
-> 6 SESSIONS / MOIS : 115,30€.
-> 8 SESSIONS / MOIS : 150,30€.
-> 10 SESSIONS / MOIS : 180,30€.
-> 12 SESSIONS / MOIS : 210,30€.

--- CATÉGORIE 6 : LE "PASS FULL FORMER" (COMBO MACHINES) ---
Le choix idéal pour mixer Reformer et Crossformer.
-> 2 SESSIONS / MOIS : 74,30€.
-> 4 SESSIONS / MOIS : 144,30€.
-> 6 SESSIONS / MOIS : 210,30€.
-> 8 SESSIONS / MOIS : 272,30€.
-> 10 SESSIONS / MOIS : 330,30€.
-> 12 SESSIONS / MOIS : 384,30€.

--- OFFRES SPÉCIALES ---
⭐️ NEW PASS STARTER (DÉCOUVERTE)
- Prix : 99,90€.
- Contenu : 5 sessions au choix (Machine, Sol, Yoga...).
- Validité : 1 mois.
- Engagement : Aucun.
- Condition : Réservé aux nouveaux membres, une seule fois.

👶 PASS KIDS (ENFANTS)
- Activités : Yoga Kids, Training Kids.
- Engagement : 4 mois.
- Prix : 35,30€ (2 sessions) ou 65,30€ (4 sessions).

********************************************************************************
CHAPITRE 5 : FAQ & GESTION DES OBJECTIONS (INTELLIGENCE SOCIALE)
********************************************************************************

Q : "Je veux faire du Reformer ET de la Boxe, ça existe ?"
R : "Il n'y a pas de pass combiné unique pour ça, MAIS la solution est très simple : Vous prenez deux abonnements (Un Pass Reformer + Un Pass Focus). Les mensualités s'additionnent et vous avez accès aux deux plannings. C'est très fréquent chez nos membres !"

Q : "J'ai peur de m'engager sur 3 mois..."
R : "C'est pour cela que notre offre 'New Pass Starter' existe ! 5 séances sans aucun engagement pour tester l'ambiance et les cours. C'est l'idéal pour commencer."

Q : "Pourquoi c'est plus cher qu'une salle classique ?"
R : "Parce que chez SVB, vous n'êtes pas un numéro. Ce sont des cours en 'Small Group' (petits effectifs). Le coach vous connaît, vous corrige, adapte les exercices. C'est du semi-privé, ce qui garantit des résultats et une sécurité que vous n'aurez jamais dans une grande salle."

Q : "Je suis enceinte."
R : "Félicitations ! Nous avons des cours adaptés. Le Pilates Reformer (avec accord médical) est excellent, tout comme le Yoga Prénatal. Évitez les cours à impacts comme le Cross Training ou la Boxe."

Q : "Est-ce que je peux reporter mes séances non utilisées sur le mois suivant ?"
R : "Non, les abonnements fonctionnent au mois (système 'Use it or Lose it'). Cela vous motive à venir régulièrement ! En cas de pépin de santé majeur (sur justificatif), nous regardons cela avec bienveillance."
"""

# ==============================================================================
# ⚙️ CONFIGURATION DE L'INTERFACE UTILISATEUR (STREAMLIT)
# ==============================================================================

st.set_page_config(
    page_title="Accueil SVB",
    page_icon="🧡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- STYLES CSS PERSONNALISÉS (DESIGN PREMIUM) ---
st.markdown("""
<style>
    /* Suppression des éléments parasites */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style du conteneur de chat */
    .stChatFloatingInputContainer {
        bottom: 20px;
        background-color: transparent;
    }

    /* Style des bulles de chat */
    .stChatMessage {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    
    /* Style du bouton WhatsApp */
    .whatsapp-btn {
        display: inline-block;
        background-color: #25D366;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        font-weight: bold;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
        width: 100%;
        margin-top: 10px;
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
        color: white;
        text-decoration: none;
    }
    
    /* Titre principal */
    h1 {
        color: #EBC6A6;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🧠 LOGIQUE DE L'ASSISTANTE (SARAH)
# ==============================================================================

# Récupération de la clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    pass # Permet de ne pas crasher en local si pas de secrets.toml

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah, votre assistante dédiée. Je connais tout sur le studio : les plannings, les tarifs détaillés, les règles de suspension et les astuces pour combiner les cours. Comment puis-je vous aider aujourd'hui ?"
        }
    ]

# Affichage du logo et titre
st.markdown("<h1>🧡 Studio Santez-Vous Bien</h1>", unsafe_allow_html=True)

# Affichage des messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- TRAITEMENT DE LA QUESTION UTILISATEUR ---
if prompt := st.chat_input("Votre question (ex: Prix Pass Cross, Suspension, Boxe...)..."):
    
    # 1. Sauvegarde et affichage immédiat de la question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Appel à l'Intelligence Artificielle
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- CRÉATION DE LA MÉMOIRE CONTEXTUELLE ---
            # On fournit les 10 derniers échanges pour que Sarah suive le fil de la discussion
            history_context = ""
            for msg in st.session_state.messages[-10:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # --- LE SYSTEM PROMPT (LE CERVEAU) ---
            # C'est ici que l'IA reçoit ses instructions de comportement
            system_prompt = f"""
            TU ES : Sarah, l'assistante virtuelle experte et chaleureuse du Studio SVB.
            
            TA SOURCE DE VÉRITÉ ABSOLUE (LA BIBLE) :
            {INFO_STUDIO}
            
            LE CONTEXTE DE LA DISCUSSION :
            {history_context}
            
            TES RÈGLES D'OR À RESPECTER IMPÉRATIVEMENT :
            1. **PRÉCISION TARIFAIRE** : Ne donne jamais une estimation. Utilise les prix exacts de la Bible (ex: 30,30€ et pas 30€).
            2. **GESTION DU CUMUL** : Si le client veut des activités incompatibles (ex: Boxe + Reformer), ne dis pas "c'est impossible". Propose de prendre **DEUX ABONNEMENTS**. C'est la procédure standard.
            3. **AJOUT DE SÉANCE** : Confirme que c'est possible d'ajouter une séance hors forfait pour 30€.
            4. **SUSPENSION** : Vérifie toujours si le client a l'option BOOST.
               - AVEC Boost = Facile, sans préavis.
               - SANS Boost = Préavis 1 mois + Absence > 10 jours.
            5. **TON DE VOIX** : Tu es une experte bienveillante ("Cocon"). Tu es directe mais polie. NE RÉPÈTE PAS "BONJOUR" si la conversation est déjà engagée.
            6. **APPEL À L'HUMAIN** : Si la demande est trop complexe, conflictuelle, ou si le client demande explicitement "Laura" ou "téléphone" -> Termine ta réponse par le code secret : [HUMAN_ALERT].
            
            Réponds maintenant au CLIENT de manière fluide et structurée (utilise des puces • si nécessaire) :
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah consulte le registre..."):
                    # Génération de la réponse
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # Détection du besoin d'escalade humaine
                    show_whatsapp_button = False
                    if "[HUMAN_ALERT]" in text_response:
                        show_whatsapp_button = True
                        text_response = text_response.replace("[HUMAN_ALERT]", "")
                    
                    # Affichage de la réponse IA
                    st.markdown(text_response)
                    st.session_state.messages.append({"role": "assistant", "content": text_response})
                    
                    # Affichage du bouton WhatsApp si nécessaire
                    if show_whatsapp_button:
                        st.markdown("---")
                        st.markdown("""
                            <a href="https://wa.me/33744919155" target="_blank">
                                <button class="whatsapp-btn">📞 Parler directement à Laura (WhatsApp)</button>
                            </a>
                        """, unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Une erreur technique est survenue : {e}")
            st.info("Conseil : Vérifiez votre connexion internet ou la validité de la clé API.")
    else:
        st.warning("⚠️ Clé API manquante. Veuillez configurer les 'Secrets' dans Streamlit.")

# ==============================================================================
# FIN DU CODE
# ==============================================================================
