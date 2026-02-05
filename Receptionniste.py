import streamlit as st
import google.generativeai as genai

# ==========================================
# 🧠 LA BIBLE DU STUDIO (DONNÉES DES IMAGES)
# ==========================================
INFO_STUDIO = """
=== 1. CONCEPTS & LIEUX (NE PAS CONFONDRE) ===
NOM : SVB (Santez-Vous Bien).
AMBIANCE : "Le bien-être au quotidien". Cocon, Premium.
CONTACT : 07 44 91 91 55 | hello@studiosvb.fr
RÉSERVATION : Sur l'appli membre ou Calendly pour l'essai.

📍 LIEU 1 : "COURS LAVANDIÈRES" (40 Cours des Lavandières, St Ouen)
- C'est le studio des MACHINES et du bien-être DOUX.
- Activités ici : Pilates Reformer, Pilates Crossformer, Yoga (Vinyasa, Hatha), Classic Pilates, Power Pilates, Core & Stretch.

📍 LIEU 2 : "PARC DES DOCKS" (6 Mail André Breton, St Ouen)
- C'est le studio du SOL, du CARDIO et du COACHING.
- Activités ici : Cross Training, Cross Core, Cross Body, Cross Rox, Boxe, Afrodanc'All, Yoga Kids, Training Kids.

=== 2. DICTIONNAIRE : ACTIVITÉ vs ABONNEMENT (TRES IMPORTANT) ===
🔴 Si le client demande "C'est quoi le CROSS TRAINING ?" -> Décris le SPORT (Intensité, cardio, au sol, aux Docks).
🔴 Si le client demande "C'est quoi le PASS CROSS ?" -> Décris l'ABONNEMENT (C'est la formule de paiement pour accéder au Cross Training).

=== 3. LES TARIFS & ABONNEMENTS (PRÉCIS) ===

⭐️ OFFRE DÉCOUVERTE (Pour tester)
- "NEW PASS STARTER" : 99,90€
- Contenu : 5 sessions au choix (valable 1 mois).
- Engagement : AUCUN.
- Pas de tacite reconduction.

🚀 OPTION "SVB BOOST" (Le Bonus Premium)
- Prix : +9,90€/mois en plus de l'abonnement.
- Avantages : FRAIS D'INSCRIPTION OFFERTS (au lieu de 49€) + 1 invité gratuit/mois + Suspension possible sans préavis + Engagement réduit (2 mois coaching / 3 mois small group).

🎫 LES PASS MENSUELS "SMALL GROUP" (Engagement 3 mois min.)
(Frais de dossier 49€ sauf si Option Boost)

1. PASS CROSS (Accès : Cross Training, Body, Rox, Core, Boxe...)
   - 2 sessions/mois : 30,30€
   - 4 sessions/mois (1x/sem) : 60,30€
   - 8 sessions/mois (2x/sem) : 116,30€
   - 12 sessions/mois : 168,30€

2. PASS REFORMER (Accès : Reformer, Classic Pilates, Yoga...)
   - 2 sessions/mois : 70,30€
   - 4 sessions/mois (1x/sem) : 136,30€
   - 8 sessions/mois (2x/sem) : 256,30€

3. PASS CROSSFORMER (Accès : La machine intense)
   - 2 sessions/mois : 78,30€
   - 4 sessions/mois : 152,30€
   - 8 sessions/mois : 288,30€

4. PASS FOCUS (Accès : Yoga, Boxe, Danse uniquement)
   - 4 sessions/mois : 72,30€
   - 8 sessions/mois : 136,30€

👶 PASS KIDS (Hors Juillet/Août)
- 2 sessions : 35,30€
- 4 sessions : 65,30€
- Engagement 4 mois.

💎 COACHING PRIVÉ (Sur mesure)
- PASS GOOD VIBES (Solo) : 4 séances (300,30€) ou 8 séances (560,30€).
- PASS DUO (À deux) : 4 séances (400,60€) ou 8 séances (720,60€).

=== 4. RÈGLEMENT INTÉRIEUR STRICT (A CITER SI BESOIN) ===
- ANNULATION COURS (Small Group) : Possible jusqu'à 1H avant le début (sinon perdu).
- ANNULATION COACHING PRIVÉ : Possible jusqu'à 24H avant.
- RETARD : + de 5 minutes = Cours REFUSÉ (Sécurité).
- CHAUSSETTES : Antidérapantes OBLIGATOIRES aux Lavandières (Vente 10€, Prêt 3€).
- REPORT : Les crédits du mois ne sont pas reportables sur le mois suivant.
- RÉSILIATION : Préavis d'1 mois par mail.
"""

# ==========================================
# ⚙️ MOTEUR TECHNIQUE & INTELLIGENCE
# ==========================================
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# Style CSS (Cache menu + Bouton WhatsApp Vert)
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
    border: none;
}
.stButton button:hover {
    background-color: #1ebc57;
    color: white;
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

# Historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais désormais tout sur nos plannings (Lavandières/Docks), nos tarifs détaillés et nos règles. Comment puis-je vous aider ?"}
    ]

# Titre
st.markdown("<h3 style='text-align: center; color: #EBC6A6;'>🧡 Bienvenue au Studio SVB</h3>", unsafe_allow_html=True)

# Affichage Chat
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
            
            # --- CERVEAU MIS À JOUR ---
            system_prompt = f"""
            Tu es Sarah, l'hôte d'accueil experte de SVB.
            
            TA BASE DE DONNÉES (RÈGLES ET PRIX ISSUS DES DOCUMENTS OFFICIELS) :
            {INFO_STUDIO}
            
            TES CONSIGNES DE COMPORTEMENT :
            1. SOIS PRÉCISE : Ne confonds jamais un SPORT (ex: Cross Training) et son ABONNEMENT (ex: Pass Cross).
            2. LOCALISATION : Si on parle de Reformer, précise que c'est aux Lavandières. Si on parle de Training Sol, c'est aux Docks.
            3. RÈGLES : Si on demande une annulation, rappelle la règle stricte (1h avant pour les cours collectifs).
            4. Si le client semble vouloir s'inscrire ou parler à un humain (Laura) -> Ajoute le code [HUMAN_ALERT].
            5. Ton : Expert, Chaleureux ("Cocon"), Rassurant.
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah consulte le planning..."):
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # Gestion bouton humain
                    show_whatsapp_button = False
                    if "[HUMAN_ALERT]" in text_response:
                        show_whatsapp_button = True
                        text_response = text_response.replace("[HUMAN_ALERT]", "")
                    
                    st.markdown(text_response)
                    st.session_state.messages.append({"role": "assistant", "content": text_response})
                    
                    if show_whatsapp_button:
                        st.markdown("---")
                        st.link_button("📞 Parler à Laura (WhatsApp)", "https://wa.me/33744919155")
        except:
            st.error("Une seconde, je reconnecte mon cerveau...")
    else:
        st.warning("Clé API manquante dans les Secrets.")
