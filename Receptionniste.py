import streamlit as st
import os

# --- 1. GESTION DES ERREURS D'IMPORTATION (POUR ÉVITER L'ÉCRAN ROUGE) ---
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR : Le module 'google.generativeai' manque.")
    st.info("Ajoutez 'google-generativeai' dans votre fichier requirements.txt")
    st.stop()

# ==============================================================================
# 📚 BIBLE DU STUDIO SVB - VERSION "ENCYCLOPÉDIE TOTALE"
# ==============================================================================
# Ici, on met TOUT. Chaque détail compte pour que l'IA ne se trompe jamais.

INFO_STUDIO = """
################################################################################
PARTIE 1 : L'IDENTITÉ & L'ESPRIT SVB
################################################################################
NOM OFFICIEL : SVB (Santez-Vous Bien).
SLOGAN : "Le bien-être au quotidien".
POSITIONNEMENT : Studio Premium, "Cocon Sportif". On est loin des usines à sport. Ici, c'est bienveillance, suivi personnalisé et esthétisme.
COULEURS & AMBIANCE : Tons Pêche, Sauge, Crème. Lumière douce. Matériel haut de gamme.

CONTACTS CLÉS :
- Responsable : Laura.
- Téléphone Urgence/Commercial : 07 44 91 91 55 (WhatsApp privilégié).
- Email : hello@studiosvb.fr
- Instagram : @svb.officiel

################################################################################
PARTIE 2 : LES DEUX STUDIOS (NE JAMAIS SE TROMPER D'ADRESSE)
################################################################################

📍 STUDIO A : "COURS LAVANDIÈRES" (L'Espace Zen & Machines)
ADRESSE : 40 Cours des Lavandières, 93400 Saint-Ouen.
AMBIANCE : Calme, concentration, Pilates technique.
ÉQUIPEMENTS : Reformers (Machines avec chariot), Crossformers, Tapis de Yoga épais.
VESTIAIRES : Disponibles (pas de douches aux Lavandières, point à vérifier).
COURS DISPENSÉS ICI :
1. Pilates Reformer (Tous niveaux).
2. Pilates Crossformer (Cardio sur machine).
3. Classic Pilates (Matwork technique).
4. Power Pilates (Matwork intense).
5. Core & Stretch (Renforcement + Souplesse).
6. Yoga Vinyasa (Dynamique).
7. Hatha Flow (Fluide).

📍 STUDIO B : "PARC DES DOCKS" (L'Espace Intensité & Coaching)
ADRESSE : 6 Mail André Breton, 93400 Saint-Ouen.
AMBIANCE : Énergique, Musique, Sol, Sacs de frappe.
COURS DISPENSÉS ICI :
1. Cross Training (Circuit training fonctionnel).
2. Cross Core (Focus abdos/gainage).
3. Cross Body (Renforcement global).
4. Cross Rox (Haute intensité).
5. Cross Yoga (Mélange Yoga/Renfo - Attention c'est bien aux Docks !).
6. Boxe (Technique & Cardio).
7. Afrodanc'All (Danse cardio).
8. Yoga Kids & Training Kids (Pour les enfants).

################################################################################
PARTIE 3 : LE DICTIONNAIRE DES COURS (POUR QUE SARAH SACHE EXPLIQUER)
################################################################################

--- LES COURS SUR MACHINES (LAVANDIÈRES) ---
- "REFORMER" : Le Pilates traditionnel sur machine. On utilise la résistance des ressorts pour affiner la silhouette et corriger la posture sans gonfler. Idéal mal de dos.
- "CROSSFORMER" : Une exclusivité SVB. C'est du Pilates sur machine mais rythmé, plus cardio. On transpire davantage, on sculpte plus vite.

--- LES COURS AU SOL (DOCKS) ---
- "CROSS TRAINING" : Entraînement en circuit (HIIT). On enchaîne des ateliers (Kettlebells, Poids de corps, Cordes). On brûle un max de calories.
- "BOXE" : On apprend les mouvements de boxe anglaise/thaï, on tape dans les sacs. C'est un défouloir total. (Nécessite le Pass Focus).
- "AFRODANC'ALL" : Cours de danse sur des rythmes afro. C'est cardio mais très fun. On lâche prise.

--- LE YOGA & BIEN-ÊTRE ---
- "VINYASA" : Yoga dynamique, on enchaîne les postures.
- "HATHA FLOW" : Plus lent, on tient les postures plus longtemps.

################################################################################
PARTIE 4 : RÈGLES COMMERCIALES INTELLIGENTES (CUMUL & MIX)
################################################################################

🚨 RÈGLE D'OR N°1 : LE CUMUL EST POSSIBLE !
Si un client veut faire deux activités incompatibles (ex: Reformer + Boxe), ne dis JAMAIS que c'est impossible.
SOLUTION : "Prenez deux abonnements (ex: Pass Reformer + Pass Focus). Les prélèvements se cumulent simplement."

🚨 RÈGLE D'OR N°2 : LES COMBOS EXISTANTS
Vérifie toujours si un "Pass Full" existe avant de proposer deux abonnements séparés.
- Cross Training + Boxe ? -> C'est le PASS FULL.
- Reformer + Crossformer ? -> C'est le PASS FULL FORMER.

################################################################################
PARTIE 5 : GRILLE TARIFAIRE MILLIMÉTRÉE (PRIX EXACTS 2024/2025)
################################################################################

⭐️ OFFRE DE BIENVENUE (POUR DÉMARRER)
Nom : "NEW PASS STARTER"
Prix : 99,90€
Ce qu'on a : 5 sessions au choix (Reformer, Cross, Yoga...).
Durée validité : 1 mois date à date.
Engagement : ZÉRO.

🚀 OPTION VIP : "SVB BOOST"
Prix : +9,90€ par mois (s'ajoute à l'abonnement).
Avantages :
1. FRAIS DE DOSSIER OFFERTS (Économie de 49€).
2. SUSPENSION possible.
3. 1 INVITATION par mois pour un ami.

--- LES ABONNEMENTS MENSUELS (ENGAGEMENT 3 MOIS) ---

🟢 LE "PASS CROSS" (ACCÈS EXCLUSIF COURS "CROSS" AUX DOCKS)
Inclus : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga.
EXCLU : Boxe, Vinyasa, Reformer.
- 2 sessions/mois : 30,30€
- 4 sessions/mois : 60,30€
- 6 sessions/mois : 90,30€
- 8 sessions/mois : 116,30€
- 12 sessions/mois : 168,30€

🟡 LE "PASS FOCUS" (ACCÈS TECHNIQUE & ARTS)
Inclus : Boxe, Afrodanc'All, Yoga Vinyasa, Hatha, Classic Pilates, Power Pilates.
- 2 sessions/mois : 36,30€
- 4 sessions/mois : 72,30€
- 6 sessions/mois : 105,30€
- 8 sessions/mois : 136,30€
- 12 sessions/mois : 192,30€

🟤 LE "PASS REFORMER" (ACCÈS MACHINE REFORMER)
Inclus : Uniquement les cours de Reformer.
- 2 sessions/mois : 70,30€
- 4 sessions/mois : 136,30€
- 6 sessions/mois : 198,30€
- 8 sessions/mois : 256,30€
- 12 sessions/mois : 360,30€

🟠 LE "PASS CROSSFORMER" (ACCÈS MACHINE CROSSFORMER)
Inclus : Uniquement les cours de Crossformer.
- 2 sessions/mois : 78,30€
- 4 sessions/mois : 152,30€
- 8 sessions/mois : 288,30€
- 12 sessions/mois : 408,30€

🔵 LE "PASS FULL" (LE COMBO SOL TOTAL)
Inclus : Tout le PASS CROSS + Tout le PASS FOCUS.
(C'est l'abonnement pour ceux qui veulent mixer Cardio et Yoga/Boxe).
- 2 sessions/mois : 40,30€
- 4 sessions/mois : 80,30€
- 6 sessions/mois : 115,30€
- 8 sessions/mois : 150,30€
- 12 sessions/mois : 210,30€

🟣 LE "PASS FULL FORMER" (LE COMBO MACHINES TOTAL)
Inclus : Reformer + Crossformer.
- 2 sessions/mois : 74,30€
- 4 sessions/mois : 144,30€
- 8 sessions/mois : 272,30€
- 12 sessions/mois : 384,30€

👶 PASS KIDS (YOGA & TRAINING ENFANTS)
Engagement 4 mois. Hors vacances scolaires été.
- 2 sessions/mois : 35,30€
- 4 sessions/mois : 65,30€

################################################################################
PARTIE 6 : RÈGLEMENT & LOGISTIQUE (POUR ÉVITER LES PROBLÈMES)
################################################################################

1. RETARDS :
   - Tolérance zéro après 5 minutes. La porte est fermée (sécurité).
   
2. ANNULATION (TRES IMPORTANT) :
   - Cours collectifs (Small Group) : Annulable jusqu'à 1H avant le début.
   - Coaching Privé : Annulable jusqu'à 24H avant.
   - Si on annule trop tard ? La séance est décomptée. Pas de remboursement.

3. CHAUSSETTES :
   - Elles sont OBLIGATOIRES pour les cours sur Machines (Lavandières).
   - On en vend sur place : 10€ la paire.
   - On en prête en dépannage : 3€ la location. (Attention, si non rendue = 10€ facturés).

4. INSCRIPTION :
   - Frais de dossier à l'entrée : 49€ (une seule fois).
   - Astuce : Ils sont offerts si on prend l'option Boost.
"""

# ==============================================================================
# ⚙️ LE MOTEUR TECHNIQUE (INTERFACE & IA)
# ==============================================================================

st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# CSS : Style Premium + Bouton WhatsApp Vert
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stChatInputContainer {padding-bottom: 20px;}
.stButton button {
    background-color: #25D366;
    color: white;
    font-size: 16px;
    font-weight: 600;
    border-radius: 12px;
    padding: 12px 24px;
    border: none;
    width: 100%;
    transition: all 0.3s ease;
}
.stButton button:hover {
    background-color: #128C7E;
    color: white;
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# Récupération Clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Initialisation Historique (Message d'accueil unique)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais tout le studio sur le bout des doigts (Tarifs, Plannings, Combos, Règles). Comment puis-je vous aider ?"}
    ]

# Titre
st.markdown("<h2 style='text-align: center; color: #EBC6A6; font-family: sans-serif; margin-bottom: 20px;'>🧡 Studio Santez-Vous Bien</h2>", unsafe_allow_html=True)

# Affichage Conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Votre question..."):
    
    # 1. On sauvegarde et affiche le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- CRÉATION DE L'HISTORIQUE (MÉMOIRE COURT TERME) ---
            # On envoie les 8 derniers échanges pour qu'elle suive la conversation
            history_context = ""
            for msg in st.session_state.messages[-8:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # --- LE CERVEAU INTELLIGENT ---
            system_prompt = f"""
            Tu es Sarah, experte du studio SVB.
            
            TA BIBLE DE RÉFÉRENCE (Respecte-la à la lettre) : 
            {INFO_STUDIO}
            
            CONVERSATION EN COURS :
            {history_context}
            
            TES MISSIONS :
            1. **GÉRER LE CUMUL** : Si le client veut des activités incompatibles (ex: Reformer + Boxe), propose de prendre **2 abonnements** (ou un Pass Full si applicable). Dis que c'est tout à fait possible.
            2. **PRÉCISION** : Utilise les prix exacts de la Bible.
            3. **MAPPING** : Boxe = Pass Focus. Reformer = Pass Reformer. Cross Training = Pass Cross.
            4. **TON** : Direct, chaleureux, expert. NE RÉPÈTE PAS "BONJOUR" (Tu l'as déjà dit au début).
            5. **HUMAIN** : Si la demande est complexe, technique, ou si le client demande "Laura" -> Ajoute le code [HUMAN_ALERT] à la fin.
            
            Réponds maintenant au CLIENT :
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah réfléchit..."):
                    # On envoie le tout
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # Détection bouton
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
            st.error(f"Une erreur technique est survenue : {e}")
    else:
        st.warning("⚠️ Clé API manquante. Vérifiez les 'Secrets' dans Streamlit.")
