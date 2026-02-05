import streamlit as st
import google.generativeai as genai

# --- 1. LA MÉMOIRE (DIRECTEMENT INCLUSE ICI) ---
# Plus besoin de fichier externe, impossible de perdre les infos.
INFO_STUDIO = """
=== 1. IDENTITÉ & PHILOSOPHIE ===
NOM : SVB (Santez-Vous Bien).
AMBIANCE : "Cocon Sportif". Bienveillante, sans jugement.
COULEURS : Pêche (#EBC6A6), Sauge (#88C0A6), Crème.
ADRESSES (Saint-Ouen, Métro Mairie de St-Ouen) :
1. Studio Lavandières : 40 Cours des Lavandières (Reformer, Crossformer, Yoga).
2. Studio Docks : Parc des Docks (Coaching privé, Small Group).

=== 2. OFFRES DE BIENVENUE ===
OFFRE STAR : "New Pass Starter" à 99,90€ (5 séances, val. 1 mois, sans engagement).
Alternative : Séance d'essai à l'unité à 30€ (15€ remboursés si inscription derrière).

=== 3. TARIFS ABONNEMENTS (ENGAGEMENT 3 MOIS) ===
FRAIS DE DOSSIER : 49€ (OFFERTS si option Boost).
1. REFORMER (Machine Classique) : 1x/semaine : 136,30€/mois | 2x/semaine : 256,30€/mois.
2. CROSSFORMER (Machine Intense) : 2x/semaine : 288,30€/mois.
3. PASS CROSS (Training Sol) : 1x/semaine : 60,30€/mois | 2x/semaine : 116,30€/mois.
4. PASS FOCUS (Yoga/Boxe) : 1x/semaine : 72,30€/mois.

=== 4. RÈGLES D'OR ===
- RETARD : Refusé après 5 min (Sécurité).
- CHAUSSETTES : Antidérapantes OBLIGATOIRES sur machines (Vente 10€).
- TÉLÉPHONE : Interdit en salle.

=== 5. FAQ PSYCHOLOGIQUE ===
- "Je suis débutant" -> Bienveillance totale, le coach adapte.
- "C'est cher" -> C'est du semi-privé (Small Group), qualité coach/machine.
- "Mal au dos" -> Le Pilates Reformer est recommandé.
"""

# --- 2. CONFIGURATION PAGE ---
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# Masquer le menu Streamlit
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CLÉ API (SECRETS) ---
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# --- 4. INTERFACE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je peux vous renseigner sur nos plannings, tarifs ou machines. Que souhaitez-vous savoir ?"}
    ]

st.markdown("<h3 style='text-align: center; color: #EBC6A6;'>🧡 Bienvenue au Studio SVB</h3>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- LE CERVEAU DE SARAH ---
            system_prompt = f"""
            Tu es Sarah, l'hôte d'accueil virtuelle du studio SVB.
            
            TES INFORMATIONS OFFICIELLES (Respecte-les STRICTEMENT) :
            {INFO_STUDIO}
            
            TES CONSIGNES :
            1. Tu es DOUCE, POLIE et ACCUEILLANTE (Style "Cocon", émojis 🍑🌿).
            2. Tu réponds UNIQUEMENT avec les infos ci-dessus. N'invente AUCUN prix.
            3. Si tu ne trouves pas l'info dans le texte ci-dessus, dis : "Je préfère vous inviter à contacter Laura sur WhatsApp au 07 44 91 91 55 pour cette précision."
            4. Ne donne jamais de conseils médicaux.
            5. Fais des réponses courtes (max 3 phrases).
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah écrit..."):
                    response = model.generate_content([system_prompt, prompt])
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error("Oups, petite maintenance. Réessayez dans 1 minute !")
    else:
        st.info("L'assistante se réveille...")
