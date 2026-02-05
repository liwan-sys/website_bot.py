import streamlit as st
import google.generativeai as genai

# ==============================================================================
# 📚 BIBLE DU STUDIO SVB - VERSION INTÉGRALE & DÉTAILLÉE
# ==============================================================================
# Cette section contient toutes les connaissances du studio.
# Plus il y a de texte ici, moins l'IA improvise.

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
PARTIE 4 : GRILLE TARIFAIRE MILLIMÉTRÉE (AUCUNE ERREUR TOLÉRÉE)
################################################################################

🚨 RÈGLE D'OR : IL EXISTE DES PASS "MONO-ACTIVITÉ" ET DES PASS "COMBO".

⭐️ OFFRE DE BIENVENUE (POUR DÉMARRER)
Nom : "NEW PASS STARTER"
Prix : 99,90€
Ce qu'on a : 5 sessions au choix (Reformer, Cross, Yoga...).
Durée validité : 1 mois date à date.
Engagement : ZÉRO.
Cible : Idéal pour tester le studio avant de s'abonner.

🚀 OPTION VIP : "SVB BOOST"
Prix : +9,90€ par mois (s'ajoute à l'abonnement).
Pourquoi la prendre ?
1. Elle annule les FRAIS DE DOSSIER de 49€ (donc rentabilisée en 5 mois).
2. Elle permet de SUSPENDRE l'abonnement (vacances, déplacements).
3. Elle offre 1 INVITATION par mois pour un ami.
4. Elle réduit l'engagement (2 mois coaching / 3 mois small group).

--- LES ABONNEMENTS MENSUELS (ENGAGEMENT 3 MOIS) ---

🟢 LE "PASS CROSS" (ACCÈS EXCLUSIF COURS "CROSS" AUX DOCKS)
Inclus : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga.
EXCLU : Boxe, Vinyasa, Reformer.
- 2 sessions/mois : 30,30€
- 4 sessions/mois : 60,30€
- 6 sessions/mois : 90,30€
- 8 sessions/mois : 116,30€
- 10 sessions/mois : 145,30€
- 12 sessions/mois : 168,30€

🟡 LE "PASS FOCUS" (ACCÈS TECHNIQUE & ARTS)
Inclus : Boxe, Afrodanc'All, Yoga Vinyasa, Hatha, Classic Pilates, Power Pilates.
- 2 sessions/mois : 36,30€
- 4 sessions/mois : 72,30€
- 6 sessions/mois : 105,30€
- 8 sessions/mois : 136,30€
- 10 sessions/mois : 165,30€
- 12 sessions/mois : 192,30€

🟤 LE "PASS REFORMER" (ACCÈS MACHINE REFORMER)
Inclus : Uniquement les cours de Reformer.
- 2 sessions/mois : 70,30€
- 4 sessions/mois : 136,30€
- 6 sessions/mois : 198,30€
- 8 sessions/mois : 256,30€
- 10 sessions/mois : 310,30€
- 12 sessions/mois : 360,30€

🟠 LE "PASS CROSSFORMER" (ACCÈS MACHINE CROSSFORMER)
Inclus : Uniquement les cours de Crossformer.
- 2 sessions/mois : 78,30€
- 4 sessions/mois : 152,30€
- 6 sessions/mois : 222,30€
- 8 sessions/mois : 288,30€
- 10 sessions/mois : 350,30€
- 12 sessions/mois : 408,30€

🔵 LE "PASS FULL" (LE COMBO SOL TOTAL)
Inclus : Tout le PASS CROSS + Tout le PASS FOCUS.
(C'est l'abonnement pour ceux qui veulent mixer Cardio et Yoga/Boxe).
- 2 sessions/mois : 40,30€
- 4 sessions/mois : 80,30€
- 6 sessions/mois : 115,30€
- 8 sessions/mois : 150,30€
- 10 sessions/mois : 180,30€
- 12 sessions/mois : 210,30€

🟣 LE "PASS FULL FORMER" (LE COMBO MACHINES TOTAL)
Inclus : Reformer + Crossformer.
- 2 sessions/mois : 74,30€
- 4 sessions/mois : 144,30€
- 6 sessions/mois : 210,30€
- 8 sessions/mois : 272,30€
- 10 sessions/mois : 330,30€
- 12 sessions/mois : 384,30€

👶 PASS KIDS (YOGA & TRAINING ENFANTS)
Engagement 4 mois. Hors vacances scolaires été.
- 2 sessions/mois : 35,30€
- 4 sessions/mois : 65,30€
- Session supp : 18,30€

################################################################################
PARTIE 5 : RÈGLEMENT & LOGISTIQUE (POUR ÉVITER LES PROBLÈMES)
################################################################################

1. RETARDS :
   - Tolérance zéro après 5 minutes. La porte est fermée pour ne pas déranger le cours et pour l'échauffement (sécurité).
   
2. ANNULATION (TRES IMPORTANT) :
   - Cours collectifs (Small Group) : Annulable jusqu'à 1H avant le début.
   - Coaching Privé : Annulable jusqu'à 24H avant.
   - Si on annule trop tard ? La séance est décomptée. Pas de remboursement.

3. CHAUSSETTES :
   - Elles sont OBLIGATOIRES pour les cours sur Machines (Lavandières) pour l'hygiène et la sécurité (Grips).
   - On en vend sur place : 10€ la paire (Marque SVB, top qualité).
   - On en prête en dépannage : 3€ la location. (Attention, si non rendue = 10€ facturés).

4. VALIDITÉ DES CRÉDITS :
   - Les séances d'un mois doivent être utilisées DANS LE MOIS.
   - Elles ne se reportent pas sur le mois suivant (sauf cas médical ou Option Boost). "Use it or lose it".

5. INSCRIPTION :
   - Frais de dossier à l'entrée : 49€ (une seule fois).
   - Astuce : Ils sont offerts si on prend l'option Boost.

################################################################################
PARTIE 6 : FAQ & SCRIPT DE VENTE (RÉPONSES TOUTES FAITES)
################################################################################

Q: "Je suis débutant, j'ai peur de ne pas suivre."
R: "Aucune inquiétude ! Nous sommes spécialisés dans le Small Group (petits effectifs). Le coach a l'œil sur tout le monde et adapte les exercices. Pour commencer en douceur, le Pilates Reformer ou le Hatha Flow sont parfaits."

Q: "C'est cher par rapport à Basic Fit..."
R: "C'est normal, nous ne sommes pas une salle de sport en accès libre. C'est du semi-privé avec un coach expert qui vous corrige à chaque mouvement. C'est comme un coaching personnel, mais partagé à plusieurs, donc plus accessible."

Q: "Je suis enceinte, je peux venir ?"
R: "Félicitations ! Oui, jusqu'à un certain stade et avec accord médical. Le Pilates Reformer prénatal ou le Yoga doux sont recommandés. Évitez le Cross Training intense."

Q: "Est-ce que je peux payer à la séance ?"
R: "Oui, la séance à l'unité est à 30€. Mais si vous comptez venir régulièrement, nos pass démarrent à 30€ pour 2 séances, c'est beaucoup plus avantageux !"

Q: "Il y a des douches ?"
R: "Aux Docks oui. Aux Lavandières (à confirmer selon studio), c'est un espace plus intime, privilégiez d'arriver en tenue si possible."
"""

# ==============================================================================
# ⚙️ LE CERVEAU DE L'APPLICATION (CODE PYTHON ROBUSTE)
# ==============================================================================

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# --- STYLISATION CSS (PREMIUM) ---
st.markdown("""
<style>
/* Masquer les éléments parasites de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Style du chat */
.stChatInputContainer {
    padding-bottom: 20px;
}

/* Style du bouton WhatsApp (Vert Officiel) */
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
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# --- GESTION DE LA CLÉ API SECRÈTE ---
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ ERREUR TECHNIQUE : La clé API est introuvable. Contactez l'administrateur.")

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if "messages" not in st.session_state:
    # Message d'accueil unique (ne sera plus répété)
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah, votre assistante. Je connais par cœur les plannings, les tarifs et le fonctionnement du studio. Comment puis-je vous renseigner aujourd'hui ?"}
    ]

# --- AFFICHAGE DU LOGO/TITRE ---
st.markdown("<h2 style='text-align: center; color: #EBC6A6; font-family: sans-serif; margin-bottom: 20px;'>🧡 Studio Santez-Vous Bien</h2>", unsafe_allow_html=True)

# --- AFFICHAGE DE L'HISTORIQUE DE CONVERSATION ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MOTEUR DE RÉPONSE (CHAT) ---
if prompt := st.chat_input("Posez votre question ici (Prix, Planning, Activité...)..."):
    
    # 1. On affiche le message de l'utilisateur tout de suite
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. L'IA réfléchit et répond
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- LE SYSTEM PROMPT (LES INSTRUCTIONS AU CERVEAU) ---
            # C'est ici qu'on dit à l'IA comment se comporter avec la Bible de données.
            system_prompt = f"""
            TU ES : Sarah, l'assistante virtuelle du studio SVB.
            TA MISSION : Renseigner les futurs membres avec précision, élégance et chaleur.
            
            TA BASE DE CONNAISSANCES (LA BIBLE) :
            {INFO_STUDIO}
            
            TES RÈGLES DE COMPORTEMENT (STRICTES) :
            1. **ZÉRO HALLUCINATION** : Ne donne JAMAIS un prix qui n'est pas dans la liste. Si tu ne trouves pas, dis que tu ne sais pas et renvoie vers Laura.
            2. **MAPPING INTELLIGENT** :
               - Si le client parle de "Boxe", tu DOIS parler du "PASS FOCUS".
               - Si le client parle de "Cross Training", tu DOIS parler du "PASS CROSS".
               - Si le client parle de "Reformer", tu DOIS parler du "PASS REFORMER".
               - Si le client veut TOUT faire, propose le "PASS FULL".
            3. **TON DE VOIX** : Tu es "Sarah". Tu es douce, bienveillante, encourageante (Esprit "Cocon"). Pas de langage robotique. Pas de "Bonjour" à chaque début de phrase.
            4. **CONCISION** : Fais des réponses courtes et aérées. Pas de pavés de texte illisibles. Utilise des puces (•) pour les listes.
            5. **DÉTECTION D'HUMAIN** : Si la question est trop complexe, si le client s'énerve, ou demande explicitement "Laura" / "Téléphone" / "Parler à quelqu'un" -> Finis ta réponse par le code secret : [HUMAN_ALERT].
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah consulte les infos..."):
                    # On envoie le contexte complet à l'IA
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # --- GESTION DU BOUTON WHATSAPP (CODE SECRET) ---
                    show_whatsapp_button = False
                    if "[HUMAN_ALERT]" in text_response:
                        show_whatsapp_button = True
                        # On nettoie le texte pour que le client ne voie pas le code
                        text_response = text_response.replace("[HUMAN_ALERT]", "")
                    
                    # Affichage de la réponse
                    st.markdown(text_response)
                    st.session_state.messages.append({"role": "assistant", "content": text_response})
                    
                    # Affichage du bouton SI le code a été détecté
                    if show_whatsapp_button:
                        st.markdown("---")
                        st.markdown("**Besoin d'une réponse plus personnalisée ?**")
                        st.link_button("📞 Parler directement à Laura (WhatsApp)", "https://wa.me/33744919155")
                        
        except Exception as e:
            st.error(f"Oups, une petite erreur technique. Réessayez ! (Erreur: {e})")
    else:
        st.warning("⚠️ Clé API manquante. Ajoutez-la dans les Secrets Streamlit.")
