import streamlit as st
import google.generativeai as genai

# ==========================================
# 🧠 ZONE MÉMOIRE : TOUT LE SAVOIR DU STUDIO
# ==========================================
INFO_STUDIO = """
=== 1. L'UNIVERS SVB (SANTEZ-VOUS BIEN) ===
NOM : SVB (Santez-Vous Bien).
PHILOSOPHIE : "Investissez en vous-même". L'intensité dans un écrin de douceur.
AMBIANCE : "Cocon Sportif". On est l'opposé des salles agressives (Noir/Rouge). Ici c'est Pêche, Sauge, Bienveillance.
ADRESSES (Saint-Ouen, Métro Mairie de St-Ouen) :
1. Studio Lavandières : 40 Cours des Lavandières (Machines : Reformer, Crossformer).
2. Studio Docks : Parc des Docks (Coaching privé, Small Group).

=== 2. LES DISCIPLINES (C'EST QUOI ?) ===
- REFORMER (Le Classique) : Pilates sur machine avec chariot. On allonge, on renforce en profondeur. Idéal pour posture et dos.
- CROSSFORMER (La Signature SVB) : Machine intense. Mix de Pilates et Cardio. On transpire, on sculpte, zéro choc.
- PASS CROSS (Le Sol) : Entraînement fonctionnel sur tapis (Cross Training, Hyrox). Pas de machine, mais grosse intensité.
- YOGA : Vinyasa ou Hatha. Pour la mobilité et l'équilibre.

=== 3. OFFRE DÉCOUVERTE (POUR COMMENCER) ===
OFFRE STAR : "New Pass Starter" à 99,90€ (soit 19,90€/séance).
- Contenu : 5 sessions au choix (Reformer, Crossformer, Training...).
- Validité : 1 mois. Sans engagement.
- Alternative : Séance d'essai unique à 30€.

=== 4. TARIFS ABONNEMENTS (ENGAGEMENT 3 MOIS) ===
FRAIS DE DOSSIER : 49€ (OFFERTS si option Boost).
1. REFORMER (Machine Classique) :
   - 1x/semaine : 136,30€/mois.
   - 2x/semaine : 256,30€/mois.
2. CROSSFORMER (Machine Intense) :
   - 2x/semaine : 288,30€/mois (Le Best Seller).
3. PASS CROSS (Training Sol - Le moins cher) :
   - 1x/semaine : 60,30€/mois.
   - 2x/semaine : 116,30€/mois.
4. PASS FOCUS (Yoga/Boxe) :
   - 1x/semaine : 72,30€/mois.

=== 5. RÈGLES D'OR ===
- CHAUSSETTES : Antidérapantes OBLIGATOIRES sur machines (Vente 10€).
- RETARD : Tolérance ZÉRO après 5 min (Sécurité). Porte fermée.
- ANNULATION : 24h avant pour le privé, sinon séance perdue.

=== 6. QUESTIONS FRÉQUENTES (FAQ) ===
- "Je suis débutant" -> C'est du Small Group (petits groupes), le coach vous corrige tout le temps. Commencez par le Reformer.
- "C'est cher" -> C'est du semi-privé premium. Rien à voir avec Basic Fit. C'est un investissement santé.
- "J'ai mal au dos" -> Le Reformer est excellent pour ça (signalez-le au coach).
"""

# ==========================================
# ⚙️ LE MOTEUR (CODE TECHNIQUE)
# ==========================================
st.set_page_config(page_title="Accueil SVB", page_icon="🧡", layout="centered")

# Masquer les menus moches
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Récupération de la clé
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass

# Initialisation du chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah. Je connais tout sur nos cours (Reformer, Crossformer...), nos tarifs et le planning. Comment puis-je vous aider ?"}
    ]

# Titre
st.markdown("<h3 style='text-align: center; color: #EBC6A6;'>🧡 Bienvenue au Studio SVB</h3>", unsafe_allow_html=True)

# Affichage historique
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
            
            # LE CERVEAU DE SARAH
            system_prompt = f"""
            Tu es Sarah, l'hôte d'accueil du studio SVB.
            
            TA MÉMOIRE OBLIGATOIRE :
            {INFO_STUDIO}
            
            TES CONSIGNES :
            1. Utilise UNIQUEMENT les infos ci-dessus. N'invente rien.
            2. Ton : Doux, Bienveillant, "Cocon", Professionnel.
            3. Si la réponse est dans la mémoire (Prix, Règle, adresse), donne-la clairement.
            4. Si tu ne sais pas : "Je préfère que vous voyiez ça directement avec l'équipe sur WhatsApp au 07 44 91 91 55 pour être sûre ! 🧡"
            5. Fais court et invite à venir essayer.
            """
            
            with st.chat_message("assistant"):
                with st.spinner("Sarah réfléchit..."):
                    response = model.generate_content([system_prompt, prompt])
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.error("Petite maintenance en cours...")
    else:
        st.warning("⚠️ Clé API introuvable. (Vérifiez les Secrets)")
