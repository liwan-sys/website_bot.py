import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# 1. CONFIGURATION BASIQUE
# ==============================================================================
st.set_page_config(page_title="Sarah - SVB", page_icon="🧡")

# On garde juste un tout petit peu de style pour le titre, rien qui casse l'affichage
st.markdown("""
<style>
    h1 { color: #E68D65; text-align: center; }
    .stChatMessage { background-color: #f9f9f9; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LA "BIBLE" DU STUDIO (CERVEAU)
# ==============================================================================

INFO_STUDIO = """
CONTEXTE : Tu es Sarah, l'assistante virtuelle du studio de sport "SVB" (Santez-Vous Bien).
TON RÔLE : Répondre aux clients avec précision, chaleur et professionnalisme.
TON INTERDICTION ABSOLUE : Ne jamais inventer une information qui n'est pas ci-dessous.

--- 1. IDENTITÉ & CONTACT ---
Nom : SVB (Santez-Vous Bien).
Philosophie : "Le bien-être au quotidien", cocon sportif, small group, suivi humain.
Contact Humain (Laura) : 07 44 91 91 55 (WhatsApp).
Email : hello@studiosvb.fr

--- 2. LES ADRESSES (NE PAS CONFONDRE) ---
LIEU A : "LAVANDIÈRES" (40 Cours des Lavandières, St Ouen).
-> Activités : Pilates Reformer, Crossformer, Yoga, Pilates Tapis.
-> Équipement : Machines, ambiance Zen.
-> Règle : Chaussettes antidérapantes OBLIGATOIRES.

LIEU B : "DOCKS" (6 Mail André Breton, St Ouen).
-> Activités : Cross Training, Boxe, Danse, Yoga Kids.
-> Équipement : Sacs de frappe, Sol, ambiance Énergie.

--- 3. CONFORT & SERVICE (ARGUMENT VENTE) ---
Douches : OUI, disponibles dans les deux studios.
Service : Tout est fourni (Serviettes, Gel douche, Shampoing, Sèche-cheveux).
Le client vient les mains libres.

--- 4. TARIFS & ABONNEMENTS (ENGAGEMENT 3 MOIS) ---
Frais de dossier : 49€ (OFFERTS si Option Boost).

OPTION "SVB BOOST" (+9,90€/mois) :
- Frais de dossier offerts.
- Suspension illimitée sans justificatif.
- 1 invité par mois.

PASS CROSS (Lieu Docks : Cross Training, Boxe, etc.)
- 2 sessions : 30,30€
- 4 sessions : 60,30€
- 8 sessions : 116,30€
- 12 sessions : 168,30€

PASS FOCUS (Mixte : Boxe, Danse, Yoga, Tapis)
- 2 sessions : 36,30€
- 4 sessions : 72,30€
- 8 sessions : 136,30€
- 12 sessions : 192,30€

PASS REFORMER (Lieu Lavandières : Machine Reformer)
- 2 sessions : 70,30€
- 4 sessions : 136,30€
- 8 sessions : 256,30€
- 12 sessions : 360,30€

PASS CROSSFORMER (Lieu Lavandières : Machine Cardio)
- 2 sessions : 78,30€
- 4 sessions : 152,30€
- 8 sessions : 288,30€
- 12 sessions : 408,30€

PASS FULL (Combo Sol : Cross + Focus)
- 2 sessions : 40,30€
- 4 sessions : 80,30€
- 8 sessions : 150,30€
- 12 sessions : 210,30€

PASS FULL FORMER (Combo Machines : Reformer + Crossformer)
- 2 sessions : 74,30€
- 4 sessions : 144,30€
- 8 sessions : 272,30€
- 12 sessions : 384,30€

OFFRE DÉCOUVERTE "STARTER" : 99,90€ (5 sessions au choix, valable 1 mois, sans engagement).
PRIX SÉANCE UNITAIRE (HORS ABO) : 30€ (Training) / 50€ (Machine).
AJOUT SÉANCE POUR ABONNÉ : Possible au tarif de 30€ l'unité.

--- 5. RÈGLES STRICTES ---
RETARD : Tolérance 5 min max. Porte fermée après.
ANNULATION : 1h avant (cours collectif) / 24h avant (privé). Sinon perdu.
CHAUSSETTES : Obligatoires sur machines (Vente 10€ / Prêt 3€).
SUSPENSION :
- Avec Boost : Immédiate.
- Sans Boost : Préavis 1 mois + Justificatif absence > 10 jours.
MODIFICATION ABONNEMENT :
- UPGRADE (Monter) : Possible tout de suite.
- DOWNGRADE (Baisser) : Impossible pendant l'engagement de 3 mois.
CUMUL : On peut cumuler 2 abonnements (ex: Reformer + Boxe).

--- 6. PLANNING TYPE (POUR INFO) ---
Lundi : Cross (Matin/Soir Docks), Reformer (Matin/Soir Lavandières).
Mardi : Boxe (Soir Docks), Yoga (Soir Lavandières).
Mercredi : Kids (Après-midi), Crossformer (Soir).
Jeudi/Vendredi : Mixte toute la journée.
Samedi/Dimanche : Matinées actives.
(Toujours dire : "Vérifiez l'horaire exact sur l'application").
"""

# ==============================================================================
# 3. LE MOTEUR IA
# ==============================================================================

# Récupération Clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ Clé API manquante. Vérifie le fichier .streamlit/secrets.toml")
    st.stop()

# Configuration Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialisation Mémoire
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis Sarah. Je connais tout sur le studio SVB (Tarifs, Planning, Règles). Comment puis-je t'aider ?"}
    ]

# Affichage Titre
st.title("🧡 Studio SVB")

# Affichage Historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Zone de saisie (Standard Streamlit - Pas de CSS bizarre)
if prompt := st.chat_input("Pose ta question ici..."):
    # 1. Afficher user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Préparer le contexte
    history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
    
    full_prompt = f"""
    {INFO_STUDIO}
    
    HISTORIQUE DE LA CONVERSATION :
    {history_context}
    
    QUESTION DU CLIENT : {prompt}
    
    CONSIGNES :
    - Réponds en utilisant UNIQUEMENT les infos ci-dessus.
    - Si c'est un prix, sois précis.
    - Si besoin d'aide humaine, ajoute [HUMAN_ALERT] à la fin.
    """

    # 3. Réponse IA
    with st.chat_message("assistant"):
        with st.spinner("..."):
            try:
                response = model.generate_content(full_prompt)
                text_response = response.text
                
                show_wa = False
                if "[HUMAN_ALERT]" in text_response:
                    show_wa = True
                    text_response = text_response.replace("[HUMAN_ALERT]", "")
                
                st.markdown(text_response)
                st.session_state.messages.append({"role": "assistant", "content": text_response})
                
                if show_wa:
                    st.markdown("---")
                    st.link_button("📞 Contacter Laura (WhatsApp)", "https://wa.me/33744919155")
            
            except Exception as e:
                st.error("Petit souci de connexion. Réessaie !")
