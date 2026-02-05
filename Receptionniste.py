import streamlit as st
import os
import datetime

# ==============================================================================
# 1. SÉCURITÉ & INITIALISATION
# ==============================================================================
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR CRITIQUE : Le module 'google.generativeai' n'est pas installé.")
    st.info("Veuillez créer un fichier 'requirements.txt' et y ajouter : google-generativeai")
    st.stop()

# ==============================================================================
# 2. LA BIBLE DU STUDIO SVB - VERSION "LOURDE" (BASE DE DONNÉES COMPLÈTE)
# ==============================================================================
# Cette section est volontairement très longue pour "forcer" l'IA à lire
# les réponses exactes plutôt que de les deviner.

INFO_STUDIO = """
********************************************************************************
CHAPITRE 1 : L'IDENTITÉ & L'EXPERIENCE CLIENT (PREMIUM)
********************************************************************************
NOM OFFICIEL : SVB (Santez-Vous Bien).
SLOGAN : "Le bien-être au quotidien".
PHILOSOPHIE : Studio Premium, "Cocon Sportif", Bienveillance, Suivi personnalisé.

CONTACTS & RÉSEAUX :
- Téléphone Responsable (Laura) : 07 44 91 91 55 (WhatsApp recommandé).
- Email : hello@studiosvb.fr
- Instagram : @svb.officiel
- Réservations : Application membre uniquement (ou lien Calendly pour essai).

LE SERVICE "HÔTEL" (DOUCHES & CONFORT) :
C'est un point clé de la vente.
- Est-ce qu'il y a des douches ? OUI, dans les deux studios.
- Dois-je apporter ma serviette ? NON, les serviettes de bain sont fournies.
- Dois-je apporter mon gel douche ? NON, produits de toilette (shampoing, gel douche) fournis.
- Dois-je apporter mon sèche-cheveux ? NON, disponible sur place.
-> Argument commercial : "Vous venez les mains libres, vous repartez frais et dispo."

********************************************************************************
CHAPITRE 2 : NOS DEUX ADRESSES (NE PAS CONFONDRE LES COURS)
********************************************************************************

📍 STUDIO A : "LAVANDIÈRES" (L'ESPACE ZEN)
- Adresse : 40 Cours des Lavandières, 93400 Saint-Ouen.
- Ambiance : Calme, concentration, Pilates technique.
- ACTIVITÉS DISPENSÉES ICI :
  1. Pilates Reformer (Machine avec chariot et ressorts).
  2. Pilates Crossformer (Machine cardio).
  3. Yoga Vinyasa (Dynamique).
  4. Hatha Flow (Douceur).
  5. Classic Pilates (Tapis).
  6. Power Pilates (Tapis intense).
  7. Core & Stretch (Renfo + Souplesse).
- RÈGLE SPÉCIALE LAVANDIÈRES : Chaussettes antidérapantes OBLIGATOIRES (Sécurité machine).

📍 STUDIO B : "DOCKS" (L'ESPACE INTENSITÉ)
- Adresse : 6 Mail André Breton, 93400 Saint-Ouen.
- Ambiance : Énergique, Musique, Sol.
- ACTIVITÉS DISPENSÉES ICI :
  1. Cross Training (Circuit training).
  2. Cross Core (Abdos).
  3. Cross Body (Full body).
  4. Cross Rox (Style Hyrox).
  5. Cross Yoga (Attention : le Cross Yoga est aux Docks, pas aux Lavandières !).
  6. Boxe (Technique & Cardio).
  7. Afrodanc'All (Danse).
  8. Kids (Yoga & Training enfants).

********************************************************************************
CHAPITRE 3 : RÈGLEMENT INTÉRIEUR DÉTAILLÉ (PROCÉDURES)
********************************************************************************

🛑 PROCÉDURE 1 : LE RETARD
- Règle : Tolérance de 5 minutes maximum.
- Action : Passé ce délai, la porte est fermée à clé.
- Motif : Sécurité, respect du groupe, échauffement manqué.
- Conséquence : Séance décomptée ("No Show").

🛑 PROCÉDURE 2 : L'ANNULATION
- Cours Collectifs (Small Group) : Annulation gratuite jusqu'à 1 HEURE avant le début.
- Coaching Privé / Duo : Annulation gratuite jusqu'à 24 HEURES avant.
- Si annulation tardive : Le crédit est perdu. Pas de remboursement.

🛑 PROCÉDURE 3 : LA SUSPENSION D'ABONNEMENT (PAUSE)
Cette règle dépend de l'abonnement du client.
- CAS A (Client avec option "SVB BOOST") : Suspension libre, immédiate, sans justificatif, sans préavis.
- CAS B (Client STANDARD sans option) : Suspension possible UNIQUEMENT si :
  1. L'absence est supérieure à 10 jours.
  2. Le client respecte un PRÉAVIS D'UN MOIS.

🛑 PROCÉDURE 4 : L'AJOUT DE SÉANCE (HORS FORFAIT)
- Question : "J'ai un forfait 4 séances, je veux en faire une 5ème."
- Réponse : "C'est possible."
- Tarif : 30€ la séance supplémentaire (Prix à l'unité).
- Méthode : Contacter l'accueil pour l'ajouter manuellement.

🛑 PROCÉDURE 5 : LE CUMUL D'ABONNEMENTS
- Question : "Je veux faire du Reformer (Machine) et de la Boxe (Sol)."
- Problème : Ces cours ne sont pas dans le même pass de base.
- Solution : "Souscrivez à DEUX abonnements (Un Pass Reformer + Un Pass Focus). Les prélèvements se cumulent et vous avez accès aux deux plannings."

********************************************************************************
CHAPITRE 4 : LA GRILLE TARIFAIRE MILLIMÉTRÉE (ENGAGEMENT 3 MOIS)
********************************************************************************
INFO : Frais de dossier à l'inscription = 49€ (OFFERTS si Option Boost).

💎 L'OPTION "SVB BOOST" (INDISPENSABLE)
- Prix : +9,90€ / mois.
- Avantages : 
  1. Frais de dossier offerts (49€ économisés tout de suite).
  2. Suspension facile.
  3. 1 Invité par mois offert.

⭐️ OFFRE DÉCOUVERTE
- Nom : "New Pass Starter".
- Prix : 99,90€.
- Contenu : 5 sessions au choix (Machine, Sol, Yoga...).
- Validité : 1 mois. Sans engagement.

--- ABONNEMENTS MENSUELS DÉTAILLÉS ---

🟢 PASS CROSS (Lieu : Docks - Sol Intense)
(Inclus : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga).
- 2 sessions par mois : 30,30€
- 4 sessions par mois : 60,30€
- 6 sessions par mois : 90,30€
- 8 sessions par mois : 116,30€
- 10 sessions par mois : 145,30€
- 12 sessions par mois : 168,30€

🟡 PASS FOCUS (Lieu : Mixte - Technique & Arts)
(Inclus aux Docks : Boxe, Afrodanc'All).
(Inclus aux Lavandières : Yoga Vinyasa, Hatha, Pilates Tapis).
- 2 sessions par mois : 36,30€
- 4 sessions par mois : 72,30€
- 6 sessions par mois : 105,30€
- 8 sessions par mois : 136,30€
- 10 sessions par mois : 165,30€
- 12 sessions par mois : 192,30€

🟤 PASS REFORMER (Lieu : Lavandières - Machine Zen)
(Inclus : Pilates Reformer uniquement).
- 2 sessions par mois : 70,30€
- 4 sessions par mois : 136,30€
- 6 sessions par mois : 198,30€
- 8 sessions par mois : 256,30€
- 10 sessions par mois : 310,30€
- 12 sessions par mois : 360,30€

🟠 PASS CROSSFORMER (Lieu : Lavandières - Machine Cardio)
(Inclus : Pilates Crossformer uniquement).
- 2 sessions par mois : 78,30€
- 4 sessions par mois : 152,30€
- 6 sessions par mois : 222,30€
- 8 sessions par mois : 288,30€
- 10 sessions par mois : 350,30€
- 12 sessions par mois : 408,30€

🔵 PASS FULL (Le Combo Sol : Cross + Focus)
(Pour ceux qui veulent faire Cross Training ET Boxe/Yoga).
- 2 sessions par mois : 40,30€
- 4 sessions par mois : 80,30€
- 6 sessions par mois : 115,30€
- 8 sessions par mois : 150,30€
- 10 sessions par mois : 180,30€
- 12 sessions par mois : 210,30€

🟣 PASS FULL FORMER (Le Combo Machines : Reformer + Crossformer)
(Pour ceux qui veulent toutes les machines).
- 2 sessions par mois : 74,30€
- 4 sessions par mois : 144,30€
- 6 sessions par mois : 210,30€
- 8 sessions par mois : 272,30€
- 10 sessions par mois : 330,30€
- 12 sessions par mois : 384,30€

👶 PASS KIDS (Enfants)
- 2 sessions : 35,30€
- 4 sessions : 65,30€
- Session supplémentaire : 18,30€
"""

# ==============================================================================
# 3. MOTEUR ET INTERFACE (STREAMLIT)
# ==============================================================================

st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# CSS POUR LE DESIGN ET LE BOUTON WHATSAPP
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Bouton WhatsApp Vert */
.stButton button {
    background-color: #25D366 !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 15px !important;
    font-size: 16px !important;
    width: 100% !important;
}
.stButton button:hover {
    background-color: #128C7E !important;
    color: white !important;
}

/* Bulles de chat */
.stChatMessage {
    padding: 15px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# GESTION CLÉ API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# INITIALISATION MÉMOIRE
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais tout le studio : les douches (tout est fourni !), les tarifs détaillés, et les règles de suspension. Comment puis-je vous aider ?"}
    ]

# TITRE
st.markdown("<h2 style='text-align: center; color: #EBC6A6; font-family: sans-serif;'>🧡 Studio Santez-Vous Bien</h2>", unsafe_allow_html=True)

# AFFICHAGE CONVERSATION
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ZONE DE SAISIE ET TRAITEMENT
if prompt := st.chat_input("Votre question (Prix, Douche, Planning...)..."):
    
    # 1. AFFICHER MESSAGE UTILISATEUR
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. IA RÉFLÉCHIT
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- CONTEXTE HISTORIQUE (MÉMOIRE COURT TERME) ---
            # On envoie les 15 derniers messages pour une mémoire solide
            history_context = ""
            for msg in st.session_state.messages[-15:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # --- SYSTEM PROMPT (CERVEAU) ---
            system_prompt = f"""
            Tu es Sarah, l'assistante experte et chaleureuse du studio SVB.
            
            TA BIBLE EST CI-DESSOUS. TU DOIS T'Y RÉFÉRER STRICTEMENT.
            NE PAS INVENTER. NE PAS SUPPOSER. LIRE ET RÉPONDRE.
            
            {INFO_STUDIO}
            
            CONTEXTE DE LA DISCUSSION :
            {history_context}
            
            TES DIRECTIVES :
            1. **DOUCHES & CONFORT** : Rappelle systématiquement que "Tout est fourni" (Serviette, Gel douche...). C'est un argument luxe.
            2. **TARIFS** : Donne le prix EXACT correspondant au nombre de séances demandé (ex: 8 sessions Reformer = 256,30€).
            3. **AJOUT DE SÉANCE** : Confirme que c'est possible à 30€ l'unité.
            4. **SUSPENSION** : Demande toujours si le client a le BOOST. 
               - Si oui : Suspension immédiate. 
               - Si non : Préavis 1 mois + 10 jours d'absence.
            5. **CUMUL** : Confirme qu'on peut prendre 2 abonnements (ex: Reformer + Focus).
            6. **TON** : Professionnel, Premium, Concis. Pas de "Bonjour" répétitif.
            7. **HUMAIN** : Si le client s'énerve ou demande Laura -> Finis par [HUMAN_ALERT].
            
            Réponds au CLIENT :
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah consulte les registres..."):
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
        st.warning("Clé API manquante. Vérifiez les secrets.")
