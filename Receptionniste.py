import streamlit as st
import os
import datetime

# ==============================================================================
# 0. PROTOCOLE DE SÉCURITÉ & DÉPENDANCES
# ==============================================================================
# Ce bloc assure que l'application ne plante pas si l'environnement est mal configuré.
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ ERREUR CRITIQUE : Le module d'intelligence artificielle est manquant.")
    st.info("Veuillez installer 'google-generativeai' via le fichier requirements.txt")
    st.stop()

# ==============================================================================
# 1. LA GRANDE ENCYCLOPÉDIE DU STUDIO SVB (LE CERVEAU)
# ==============================================================================
# Cette section est la "Bible". Elle contient plus de 100 règles métiers.
# Elle est structurée pour empêcher l'IA d'halluciner.

INFO_STUDIO = """
********************************************************************************
SECTION A : L'IDENTITÉ FONDAMENTALE (POUR LE TON)
********************************************************************************
[NOM] : SVB (Santez-Vous Bien).
[SLOGAN] : "Le bien-être au quotidien".
[PHILOSOPHIE] : Nous sommes un "Cocon Sportif".
[POSITIONNEMENT] : Premium, Semi-Privé, Suivi, Humain.
[CONTRE-EXEMPLE] : Nous ne sommes PAS une salle "low-cost" en libre accès.

[CONTACTS]
- Responsable : Laura.
- Téléphone : 07 44 91 91 55 (Canal privilégié : WhatsApp).
- Email : hello@studiosvb.fr
- Site Web/Appli : Pour les réservations et achats.

********************************************************************************
SECTION B : LES INFRASTRUCTURES & SERVICES PREMIUM (ARGUMENTS DE VENTE)
********************************************************************************

📍 LIEU 1 : STUDIO "LAVANDIÈRES" (L'ESPACE ZEN)
- Adresse : 40 Cours des Lavandières, 93400 Saint-Ouen.
- Ambiance : Lumière douce, Calme, Concentration.
- Vestiaires : OUI.
- Douches : OUI (1 douche disponible).
- Équipements Sportifs : Machines Reformer, Machines Crossformer, Tapis Pilates épais.

📍 LIEU 2 : STUDIO "DOCKS" (L'ESPACE ÉNERGIE)
- Adresse : 6 Mail André Breton, 93400 Saint-Ouen.
- Ambiance : Dynamique, Musique, Dépassement de soi.
- Vestiaires : OUI.
- Douches : OUI (1 douche disponible).
- Équipements Sportifs : Sacs de frappe, Kettlebells, TRX, Espace fonctionnel.

🚿 LE SERVICE "HÔTEL" (TOUT INCLUS)
C'est un différenciateur majeur. Le client n'a besoin de rien.
- Serviettes de bain : FOURNIES sur place.
- Gel douche / Shampoing : FOURNIS (Marques de qualité).
- Sèche-cheveux : DISPONIBLE.
- Produits féminins / Déodorant : Souvent à disposition.
-> Argumentaire : "Venez avant ou après le travail, vous n'avez pas besoin de charger votre sac."

********************************************************************************
SECTION C : DÉFINITION TECHNIQUE DES COURS (POUR BIEN ORIENTER)
********************************************************************************

[PILATES REFORMER] (Lieu : Lavandières)
- C'est quoi ? Pilates sur machine avec chariot coulissant et ressorts.
- Bienfaits : Renforcement profond, posture, allongement de la silhouette.
- Pour qui ? Tout le monde (y compris femmes enceintes et blessés légers).

[PILATES CROSSFORMER] (Lieu : Lavandières)
- C'est quoi ? Pilates sur machine MAIS plus dynamique et cardio.
- Bienfaits : Brûle-graisse et sculpture musculaire.
- Intensité : Élevée.

[CROSS TRAINING] (Lieu : Docks)
- C'est quoi ? Circuit training fonctionnel (HIIT).
- Matériel : Poids du corps, Kettlebells, Cordes.
- Objectif : Cardio, perte de poids, condition physique.

[BOXE] (Lieu : Docks)
- C'est quoi ? Technique pieds-poings et cardio (sur sacs).
- Matériel : Gants (prêt possible mais mieux d'avoir les siens).
- Ambiance : Défouloir.

[AFRODANC'ALL] (Lieu : Docks)
- C'est quoi ? Danse cardio sur rythmes africains/tropicaux.
- Objectif : Lâcher prise, fun, cardio.

[YOGA VINYASA] (Lieu : Lavandières)
- C'est quoi ? Yoga dynamique, enchaînement de postures.

[CROSS YOGA] (Lieu : DOCKS - ATTENTION À L'ADRESSE)
- C'est quoi ? Un hybride entre le yoga et le renforcement musculaire.

********************************************************************************
SECTION D : GRILLE TARIFAIRE MILLIMÉTRÉE (ENGAGEMENT 3 MOIS)
********************************************************************************
RÈGLE GÉNÉRALE : Tous les abonnements mensuels ont un engagement initial de 3 mois.
FRAIS DE DOSSIER : 49€ (Payés une seule fois à l'inscription).
ASTUCE COMMERCIALE : Ces frais sont OFFERTS si le client prend l'option BOOST.

💎 L'OPTION "SVB BOOST" (+9,90€/MOIS)
C'est l'option indispensable.
1. Rembourse les frais de dossier (49€ d'économie immédiate).
2. Permet la suspension de l'abonnement sans préavis.
3. Offre 1 séance "Invité" par mois (valeur 30€).

--- DÉTAIL EXHAUSTIF DES PRIX (PAR CATÉGORIE) ---

1️⃣ LE "PASS CROSS" (ACCÈS : DOCKS / SOL INTENSE)
Cours inclus : Cross Training, Cross Core, Cross Body, Cross Rox, Cross Yoga.
Cours EXCLUS : Boxe, Reformer, Vinyasa.
- Formule 2 sessions/mois : 30,30€
- Formule 4 sessions/mois : 60,30€ (Idéal 1x/semaine)
- Formule 6 sessions/mois : 90,30€
- Formule 8 sessions/mois : 116,30€ (Idéal 2x/semaine)
- Formule 10 sessions/mois : 145,30€
- Formule 12 sessions/mois : 168,30€ (Idéal 3x/semaine)

2️⃣ LE "PASS FOCUS" (ACCÈS : MIXTE / TECHNIQUE & ARTS)
Cours inclus : Boxe, Afrodanc'All, Yoga (Vinyasa/Hatha), Pilates Tapis.
- Formule 2 sessions/mois : 36,30€
- Formule 4 sessions/mois : 72,30€
- Formule 6 sessions/mois : 105,30€
- Formule 8 sessions/mois : 136,30€
- Formule 10 sessions/mois : 165,30€
- Formule 12 sessions/mois : 192,30€

3️⃣ LE "PASS REFORMER" (ACCÈS : LAVANDIÈRES / MACHINE ZEN)
Cours inclus : Pilates Reformer uniquement.
- Formule 2 sessions/mois : 70,30€
- Formule 4 sessions/mois : 136,30€
- Formule 6 sessions/mois : 198,30€
- Formule 8 sessions/mois : 256,30€
- Formule 10 sessions/mois : 310,30€
- Formule 12 sessions/mois : 360,30€

4️⃣ LE "PASS CROSSFORMER" (ACCÈS : LAVANDIÈRES / MACHINE CARDIO)
Cours inclus : Pilates Crossformer uniquement.
- Formule 2 sessions/mois : 78,30€
- Formule 4 sessions/mois : 152,30€
- Formule 6 sessions/mois : 222,30€
- Formule 8 sessions/mois : 288,30€
- Formule 10 sessions/mois : 350,30€
- Formule 12 sessions/mois : 408,30€

5️⃣ LE "PASS FULL" (LE COMBO SOL)
Cours inclus : Tous les cours du Pass CROSS + Tous les cours du Pass FOCUS.
(Idéal pour mixer Cardio et Boxe/Yoga).
- Formule 2 sessions/mois : 40,30€
- Formule 4 sessions/mois : 80,30€
- Formule 6 sessions/mois : 115,30€
- Formule 8 sessions/mois : 150,30€
- Formule 10 sessions/mois : 180,30€
- Formule 12 sessions/mois : 210,30€

6️⃣ LE "PASS FULL FORMER" (LE COMBO MACHINES)
Cours inclus : Reformer + Crossformer.
- Formule 2 sessions/mois : 74,30€
- Formule 4 sessions/mois : 144,30€
- Formule 6 sessions/mois : 210,30€
- Formule 8 sessions/mois : 272,30€
- Formule 10 sessions/mois : 330,30€
- Formule 12 sessions/mois : 384,30€

👶 PASS KIDS (YOGA & TRAINING ENFANTS)
- Engagement 4 mois. Hors vacances scolaires été.
- 2 sessions : 35,30€
- 4 sessions : 65,30€
- Session sup : 18,30€

⭐️ NEW PASS STARTER (OFFRE DÉCOUVERTE)
- Prix : 99,90€ (Paiement unique).
- Contenu : 5 sessions au choix (Machine, Sol, Yoga...).
- Validité : 1 mois.
- Engagement : Zéro.
- Note : Offre réservée aux nouveaux clients, non renouvelable.

💰 PRIX À L'UNITÉ (HORS ABONNEMENT)
- Séance à l'unité : 30€.
- (Utile pour ajouter une séance ponctuelle en plus de son forfait).

********************************************************************************
SECTION E : RÈGLES DE GESTION & LOGISTIQUE (POLITIQUE STRICTE)
********************************************************************************

🛑 1. POLITIQUE DE RETARD
- Règle : "5 minutes de tolérance, pas une de plus."
- Action : La porte est verrouillée après 5 min.
- Motif : Sécurité, respect des autres membres, échauffement manqué (risque de blessure).
- Conséquence : La séance est comptabilisée comme "No Show" (perdue).

🛑 2. POLITIQUE D'ANNULATION
- Cours Collectifs (Small Group) :
  * Annulation possible jusqu'à 1H avant le début du cours.
  * Si < 1H : Crédit perdu ("Late Cancel").
- Coaching Privé / Duo :
  * Annulation possible jusqu'à 24H avant le RDV.
  * Si < 24H : Crédit perdu.

🛑 3. POLITIQUE DES CHAUSSETTES (LAVANDIÈRES)
- Règle : Les chaussettes antidérapantes sont OBLIGATOIRES pour tous les cours sur Machines (Reformer/Crossformer).
- Raison : Hygiène et sécurité (pour ne pas glisser).
- Solutions sur place :
  * Vente : 10€ la paire (Chaussettes techniques SVB).
  * Prêt (Location) : 3€ la paire. (Attention : Si non rendue, facturation 10€).

🛑 4. POLITIQUE D'AJOUT DE SÉANCE
- Problème : "J'ai un Pass 4 sessions mais je veux en faire 5 ce mois-ci."
- Solution : "C'est tout à fait possible."
- Méthode : Le client contacte le studio. On ajoute la séance manuellement.
- Facturation : 30€ (Prix unitaire).

🛑 5. POLITIQUE DE SUSPENSION (PAUSE)
- CAS A (Client avec BOOST) : Suspension immédiate, durée libre, sans justificatif.
- CAS B (Client STANDARD) : Suspension possible SEULEMENT SI :
  * L'absence prévue est > 10 jours.
  * Le client respecte un préavis d'1 mois.
- Note : La suspension prolonge la date de fin d'engagement d'autant.

🛑 6. POLITIQUE DE MODIFICATION D'ABONNEMENT (UPGRADE/DOWNGRADE)
C'est une règle critique pour le chiffre d'affaires.
- SCÉNARIO "UPGRADE" (Le client veut passer de 4 à 8 séances) :
  * Possible : OUI.
  * Quand : IMMÉDIATEMENT (Même pendant l'engagement).
  * Frais : Aucun.
- SCÉNARIO "DOWNGRADE" (Le client veut passer de 8 à 4 séances) :
  * PENDANT LES 3 PREMIERS MOIS (Engagement) : ⛔️ STRICTEMENT INTERDIT. On ne peut pas baisser son forfait.
  * APRÈS LES 3 MOIS : Possible avec un préavis d'un mois.

🛑 7. POLITIQUE DE REPORT (CARRY OVER)
- Règle : "Use it or Lose it".
- Les séances non utilisées dans le mois ne sont PAS reportées sur le mois suivant.
- Exception : Cas médical grave (sur présentation d'un certificat).

********************************************************************************
SECTION F : SCÉNARIOS COMPLEXES & RÉPONSES TYPES
********************************************************************************

SCÉNARIO : CUMUL D'ACTIVITÉS
Client : "Je veux faire du Reformer (Machine) et de la Boxe (Sol). Quel abonnement je prends ?"
Analyse : Il n'y a pas d'abonnement unique couvrant ces deux catégories spécifiques (sauf si on considère le Full, mais le Full ne couvre pas le Reformer).
Réponse IA : "C'est une excellente combinaison ! Comme ces activités appartiennent à deux catégories différentes, la solution est de prendre deux abonnements complémentaires : un Pass Reformer et un Pass Focus. Les prélèvements se cumulent et vous avez une liberté totale sur les deux plannings."

SCÉNARIO : FEMME ENCEINTE
Client : "Je suis enceinte, qu'est-ce que je peux faire ?"
Réponse IA : "Félicitations ! Jusqu'à un certain stade et avec accord médical, nous recommandons le Pilates Reformer (excellent pour le dos et le périnée) et le Yoga doux. Nous déconseillons les cours à impacts comme le Cross Training, la Boxe ou le Crossformer."

SCÉNARIO : DÉBUTANT INQUIET
Client : "Je n'ai jamais fait de sport, j'ai peur de ne pas suivre."
Réponse IA : "Aucune inquiétude. C'est tout l'intérêt du 'Small Group' (petits effectifs). Le coach est là pour vous, il adapte chaque exercice à votre niveau. Personne n'est laissé de côté chez SVB."
"""

# ==============================================================================
# 3. INTERFACE UTILISATEUR & MOTEUR D'INTELLIGENCE
# ==============================================================================

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Accueil SVB",
    page_icon="🧡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Injection de CSS pour un design Premium et fonctionnel
st.markdown("""
<style>
    /* Masquer les éléments techniques de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Design du chat */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Bouton d'action WhatsApp (Vert Officiel) */
    .whatsapp-btn {
        display: inline-block;
        background-color: #25D366;
        color: white;
        padding: 15px 30px;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        font-weight: bold;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
        width: 100%;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
        color: white;
        transform: translateY(-2px);
        text-decoration: none;
    }
    
    /* Titre élégant */
    h1 {
        color: #EBC6A6; /* Couleur Pêche SVB */
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Récupération sécurisée de la clé API
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except:
    pass # Gestion locale silencieuse

# Initialisation de la mémoire de conversation (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour ! Bienvenue chez SVB 🧡. Je suis Sarah, votre assistante dédiée. Je connais tout sur le studio : les plannings, les tarifs millimétrés, les services confort (douches, serviettes...), et les règles administratives. Comment puis-je vous aider ?"
        }
    ]

# Affichage du Titre
st.markdown("<h1>🧡 Studio Santez-Vous Bien</h1>", unsafe_allow_html=True)

# Boucle d'affichage des messages existants
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question (Tarifs, Suspension, Douche, Annulation...)..."):
    
    # 1. Sauvegarde et affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Logique de réponse de l'IA
    if api_key:
        try:
            # Configuration du modèle
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # --- CONSTRUCTION DU CONTEXTE (MÉMOIRE) ---
            # On concatène les 15 derniers échanges pour garder le fil de la discussion
            history_context = ""
            for msg in st.session_state.messages[-15:]: 
                role_label = "CLIENT" if msg["role"] == "user" else "SARAH"
                history_context += f"{role_label}: {msg['content']}\n"

            # --- SYSTEM PROMPT (LE CERVEAU DE SARAH) ---
            # C'est ici que l'IA reçoit ses instructions comportementales et sa base de connaissances
            system_prompt = f"""
            TU ES : Sarah, l'assistante virtuelle experte, élégante et infaillible du Studio SVB.
            
            TA BASE DE CONNAISSANCES ABSOLUE (BIBLE) :
            Tu dois t'y référer pour CHAQUE réponse. Ne jamais inventer.
            {INFO_STUDIO}
            
            HISTORIQUE DE LA DISCUSSION EN COURS :
            {history_context}
            
            TES RÈGLES D'INTERACTION (STRICTES) :
            1. **DOUCHES & CONFORT** : Si on parle d'équipement, rappelle fièrement que "Tout est fourni" (Serviettes, Gel douche, Sèche-cheveux). C'est un service luxe.
            2. **MODIFICATION ABONNEMENT** : 
               - UPGRADE (Monter en gamme) : Possible immédiatement.
               - DOWNGRADE (Baisser en gamme) : **INTERDIT** tant que l'engagement de 3 mois n'est pas fini. C'est une règle financière stricte.
            3. **AJOUT SÉANCE** : Confirme que le client peut payer 30€ pour une séance hors forfait.
            4. **SUSPENSION** : Fais la distinction : 
               - Client BOOST = Suspension libre.
               - Client STANDARD = Préavis 1 mois + 10 jours d'absence mini.
            5. **CUMUL** : Valide le fait de prendre 2 abonnements (ex: Reformer + Focus) pour avoir accès à tout.
            6. **TON DE VOIX** : Professionnel, Premium, Chaleureux. Ne répète pas "Bonjour" à chaque phrase.
            7. **SÉCURITÉ HUMAINE** : Si la demande est une réclamation, une demande complexe, ou si le mot "Laura" ou "Téléphone" apparait -> Termine ta réponse par le code : [HUMAN_ALERT].
            
            Réponds maintenant au CLIENT avec précision :
            """
            
            # Génération de la réponse
            with st.chat_message("assistant"):
                with st.spinner("Sarah consulte les registres..."):
                    response = model.generate_content([system_prompt, prompt])
                    text_response = response.text
                    
                    # Gestion du bouton WhatsApp (Code secret)
                    show_whatsapp_button = False
                    if "[HUMAN_ALERT]" in text_response:
                        show_whatsapp_button = True
                        text_response = text_response.replace("[HUMAN_ALERT]", "")
                    
                    # Affichage du texte
                    st.markdown(text_response)
                    st.session_state.messages.append({"role": "assistant", "content": text_response})
                    
                    # Affichage du bouton si nécessaire
                    if show_whatsapp_button:
                        st.markdown("---")
                        st.markdown("""
                            <a href="https://wa.me/33744919155" target="_blank">
                                <button class="whatsapp-btn">📞 Contacter Laura (Directrice) sur WhatsApp</button>
                            </a>
                        """, unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Une erreur technique est survenue : {e}")
            st.info("Astuce : Vérifiez votre connexion internet.")
    else:
        st.warning("⚠️ Clé API manquante. Veuillez configurer les 'Secrets' dans Streamlit.")