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

    /* BULLES DE CHAT (FORCE COULEUR NOIRE) */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #EBC6A6;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #1f1f1f !important;
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage div {
        color: #1f1f1f !important;
    }

    /* BOUTON WHATSAPP */
    .stButton button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 12px;
        font-weight: bold;
        width: 100%;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LA BIBLE SVB - VERSION "ENCYCLOPÉDIE DÉTAILLÉE"
# ==============================================================================

INFO_STUDIO = """
================================================================================
CHAPITRE 1 : FICHES D'IDENTITÉ ET CONTACTS
================================================================================
NOM DE L'ENTREPRISE : SVB (Santez-Vous Bien).
SLOGAN : "Le bien-être au quotidien".
TYPE D'ÉTABLISSEMENT : Studio de coaching sportif Premium et Bien-être.
DIFFÉRENCE MAJEURE : Ce n'est pas une salle en libre service. C'est du "Small Group" (petits groupes coachés) ou du "Private Coaching".

CONTACTS & RÉSEAUX :
- Canal prioritaire : WhatsApp au 07 44 91 91 55.
- Email : hello@studiosvb.fr
- Instagram : @studiosvb (pour voir l'ambiance).
- Réservation : Uniquement via l'application membre (BSport/Deciplus) ou le site web.

LE SERVICE "HÔTEL" (ARGUMENTAIRE DE VENTE) :
Nous fournissons un service tout inclus pour faciliter la vie des membres actifs.
- Douches : OUI, présentes dans les deux studios.
- Serviettes : FOURNIES (propres et pliées).
- Produits : Gel douche, Shampoing, Après-shampoing, Déodorant, Sèche-cheveux, Lisseur.
- Conclusion : "Vous pouvez venir les mains vides avant ou après le travail."

================================================================================
CHAPITRE 2 : LES LIEUX (NE JAMAIS CONFONDRE)
================================================================================
Attention : Les deux studios sont à 5 minutes à pied l'un de l'autre, mais il ne faut pas se tromper d'adresse pour le cours.

📍 ADRESSE A : STUDIO "LAVANDIÈRES"
- Adresse exacte : 40 Cours des Lavandières, 93400 Saint-Ouen.
- Ambiance : Zen, Cocooning, Bois clair, Calme.
- ACTIVITÉS SPÉCIFIQUES :
  1. Pilates Reformer (Sur machine avec chariot).
  2. Pilates Crossformer (Sur machine, version cardio).
  3. Yoga Vinyasa (Dynamique).
  4. Hatha Flow (Doux).
  5. Pilates Tapis (Matwork).
- CODE VESTIMENTAIRE : Chaussettes antidérapantes OBLIGATOIRES (Vente 10€ sur place).

📍 ADRESSE B : STUDIO "DOCKS"
- Adresse exacte : 6 Mail André Breton, 93400 Saint-Ouen.
- Ambiance : Industrielle chic, Néons, Musique rythmée, Énergie.
- ACTIVITÉS SPÉCIFIQUES :
  1. Cross Training (HIIT, Kettlebells, Cordes).
  2. Boxe (Sacs de frappe, gants).
  3. Afrodanc'All (Danse cardio).
  4. Yoga Kids & Training Kids (Enfants).
  5. Cross Yoga (Mélange renforcement et yoga).
- CODE VESTIMENTAIRE : Baskets propres obligatoires (sauf pour Yoga/Danse pieds nus).

================================================================================
CHAPITRE 3 : RÈGLEMENT INTÉRIEUR & PROCÉDURES STRICTES
================================================================================

--- RÈGLE DU PRIX À L'UNITÉ (TRES IMPORTANT) ---
Il y a deux tarifs à l'unité selon qui demande :
1. LE PRIX PUBLIC (Non-adhérent / Site Web) :
   - Pour une séance sur Machine (Reformer/Crossformer) : 50€.
   - Pour une séance au Sol (Cross/Boxe) : 30€.
2. LE PRIX MEMBRE (Adhérent SVB) :
   - Si un membre a terminé son forfait et veut ajouter une séance : Tarif unique de 30€ (même pour les machines).
   - C'est un avantage fidélité.

--- RÈGLE DE MODIFICATION D'ABONNEMENT ---
1. UPGRADE (Monter en gamme) :
   - Exemple : Passer de 4 sessions à 8 sessions.
   - Autorisation : OUI, immédiat.
2. DOWNGRADE (Baisser en gamme) :
   - Exemple : Passer de 8 sessions à 4 sessions.
   - Autorisation : NON, interdit durant la période d'engagement de 3 mois.
   - Après les 3 mois : Possible avec 1 mois de préavis.

--- RÈGLE DE SUSPENSION (VACANCES/MALADIE) ---
1. CAS "OPTION BOOST" :
   - Suspension libre, quand on veut, pour la durée qu'on veut.
2. CAS "STANDARD" (SANS BOOST) :
   - Suspension possible UNIQUEMENT SI : Absence > 10 jours ET Préavis d'un mois.
   - Sinon, l'abonnement continue.

--- RÈGLE D'ANNULATION & RETARD ---
1. RETARD :
   - Tolérance : 5 minutes maximum.
   - Action : Porte fermée à clé. Accès refusé. Séance perdue.
2. ANNULATION :
   - Cours Collectif : Annulation gratuite jusqu'à 1H avant.
   - Coaching Privé : Annulation gratuite jusqu'à 24H avant.
   - Si annulation tardive : Crédit perdu ("Late Cancel").

================================================================================
CHAPITRE 4 : GRILLE TARIFAIRE DÉTAILLÉE (ABONNEMENTS 3 MOIS)
================================================================================
FRAIS DE DOSSIER : 49€ (OFFERTS SI OPTION BOOST).

🔥 OFFRE DÉCOUVERTE : "NEW PASS STARTER"
- Prix : 99,90€ (Paiement en une fois).
- Ce que ça contient : 5 sessions au choix sur tout le planning.
- Durée : Valable 1 mois.
- Engagement : Aucun.

🚀 OPTION VIP : "SVB BOOST" (+9,90€/mois)
- Avantage 1 : Frais de dossier 49€ offerts.
- Avantage 2 : Suspension illimitée.
- Avantage 3 : 1 Invitation "Guest" par mois pour un ami.

--- DÉTAIL DES PASS MENSUELS (PRIX EXACTS) ---

🟢 PASS CROSS (Accès Docks - Sol Intense)
Donne accès à : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga.
- 2 sessions par mois : 30,30€
- 4 sessions par mois : 60,30€
- 6 sessions par mois : 90,30€
- 8 sessions par mois : 116,30€
- 10 sessions par mois : 145,30€
- 12 sessions par mois : 168,30€

🟡 PASS FOCUS (Accès Mixte - Technique)
Donne accès à : Boxe, Danse, Yoga Vinyasa, Hatha, Pilates Tapis.
- 2 sessions par mois : 36,30€
- 4 sessions par mois : 72,30€
- 6 sessions par mois : 105,30€
- 8 sessions par mois : 136,30€
- 10 sessions par mois : 165,30€
- 12 sessions par mois : 192,30€

🟤 PASS REFORMER (Accès Lavandières - Machine Zen)
Donne accès à : Pilates Reformer uniquement.
- 2 sessions par mois : 70,30€
- 4 sessions par mois : 136,30€
- 6 sessions par mois : 198,30€
- 8 sessions par mois : 256,30€
- 10 sessions par mois : 310,30€
- 12 sessions par mois : 360,30€

🟠 PASS CROSSFORMER (Accès Lavandières - Machine Cardio)
Donne accès à : Pilates Crossformer uniquement.
- 2 sessions par mois : 78,30€
- 4 sessions par mois : 152,30€
- 6 sessions par mois : 222,30€
- 8 sessions par mois : 288,30€
- 10 sessions par mois : 350,30€
- 12 sessions par mois : 408,30€

🔵 PASS FULL (Le Combo Sol)
Combine tous les cours du Pass Cross + Pass Focus.
- 2 sessions par mois : 40,30€
- 4 sessions par mois : 80,30€
- 6 sessions par mois : 115,30€
- 8 sessions par mois : 150,30€
- 10 sessions par mois : 180,30€
- 12 sessions par mois : 210,30€

🟣 PASS FULL FORMER (Le Combo Machines)
Combine Reformer + Crossformer.
- 2 sessions par mois : 74,30€
- 4 sessions par mois : 144,30€
- 6 sessions par mois : 210,30€
- 8 sessions par mois : 272,30€
- 10 sessions par mois : 330,30€
- 12 sessions par mois : 384,30€

👶 PASS KIDS (Enfants - Mercredi/Samedi)
- 2 sessions par mois : 35,30€
- 4 sessions par mois : 65,30€

================================================================================
CHAPITRE 5 : SCRIPTS DE RÉPONSE (FAQ INTELLIGENTE)
================================================================================

SITUATION : "C'EST CHER"
Réponse : "Je comprends votre remarque. Cependant, comparez ce qui est comparable : nous ne sommes pas une salle en accès libre (type Basic Fit). Nous sommes un studio de coaching en petit groupe (Semi-privé). Vous avez un coach expert qui vous corrige, un programme sur mesure, et un service tout inclus (serviettes, produits). À 15-20€ la séance avec ce niveau de service, nous sommes en réalité très compétitifs par rapport à un coach privé (80€/heure)."

SITUATION : "JE VEUX MIXER REFORMER ET BOXE"
Réponse : "Excellente idée ! Ces deux activités sont complémentaires. Comme elles font partie de catégories différentes (Machine vs Sol), la solution est simple : vous prenez deux petits abonnements (ex: Pass Reformer 4 sessions + Pass Focus 4 sessions). Vous aurez ainsi accès aux deux plannings en toute liberté."

SITUATION : "JE SUIS ENCEINTE"
Réponse : "Félicitations ! Oui, vous pouvez pratiquer chez nous. Nous recommandons vivement le Pilates Reformer (excellent pour le dos et le maintien) et le Yoga Doux. Par contre, dès le début de la grossesse, nous arrêtons les cours à impact (Boxe, Cross Training, Crossformer) pour votre sécurité."
"""

# ==============================================================================
# 4. LE CERVEAU DE SARAH (CONFIGURATION IA)
# ==============================================================================

api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Initialisation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis Sarah, l'assistante virtuelle SVB 🧡. Je connais tout le studio : les tarifs, les plannings, les services confort et les règles. Comment puis-je vous aider ?"}
    ]

# Affichage Titre
st.markdown("<h1>Sarah</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>VOTRE ASSISTANTE SVB</div>", unsafe_allow_html=True)

# Affichage Historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Votre question (Prix, Douche, Planning, Annulation...)..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Mémoire (Context Window)
            history_context = ""
            for msg in st.session_state.messages[-15:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # INSTRUCTIONS SYSTÈME RENFORCÉES
            system_prompt = f"""
            Tu es Sarah, l'assistante experte et dévouée du studio SVB.
            
            TA BIBLE D'INFORMATION (SOURCE DE VÉRITÉ) : 
            {INFO_STUDIO}
            
            HISTORIQUE DE CONVERSATION :
            {history_context}
            
            TES RÈGLES DE COMPORTEMENT :
            1. **PRIX UNITAIRE (ATTENTION)** : 
               - Si on demande le prix public d'une séance machine : 50€.
               - Si c'est un MEMBRE qui veut ajouter une séance : 30€.
            2. **TON NEUTRE** : Tu parles au nom de "L'équipe". Pas de noms propres (Shanaël, Laura...).
            3. **SERVICE CONFORT** : Rappelle systématiquement que TOUT est fourni (Serviettes, Produits...).
            4. **RÈGLES FINANCIÈRES** : 
               - UPGRADE = OUI. 
               - DOWNGRADE = NON (pendant les 3 mois d'engagement).
            5. **SUSPENSION** : Vérifie si le client a l'option BOOST.
            6. **HUMAIN** : Si besoin d'escalade -> Ajoute [HUMAN_ALERT] à la fin.
            
            Réponds au CLIENT maintenant :
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
        except Exception as e:
            st.error(f"Erreur technique : {e}")
    else:
        st.warning("Clé API manquante.")
