"""
AgroConnect — Seed (version Django)
Insère 10 utilisateurs + admin + publications de démonstration.
"""
import random
from datetime import datetime, timedelta
from database import get_users_col, get_posts_col, get_db
from auth_utils import hash_password

USERS_DATA = [
    {"pseudo": "AgriSenior_Diallo",  "region": "Casamance",    "type_culture": "mil"},
    {"pseudo": "CultivBio_Ndiaye",   "region": "Sine Saloum",  "type_culture": "arachide"},
    {"pseudo": "FermeVerte_Mbaye",   "region": "Thiès",        "type_culture": "riz"},
    {"pseudo": "RizierePlus_Sow",    "region": "Saint-Louis",  "type_culture": "maïs"},
    {"pseudo": "ArachidePro_Fall",   "region": "Ziguinchor",   "type_culture": "coton"},
    {"pseudo": "SolSain_Diop",       "region": "Diourbel",     "type_culture": "sorgho"},
    {"pseudo": "EauVive_Thiaw",      "region": "Fatick",       "type_culture": "niébé"},
    {"pseudo": "GrainDor_Kane",      "region": "Kolda",        "type_culture": "bissap"},
    {"pseudo": "NatureAg_Sarr",      "region": "Tambacounda",  "type_culture": "fonio"},
    {"pseudo": "PaysanModerne_Sy",   "region": "Kédougou",     "type_culture": "mangue"},
]

TAGS_POOL = [
    "irrigation", "fertilisation", "semences", "récolte", "météo",
    "maladies", "insectes", "exportation", "bio", "technique",
    "conseil", "marché", "équipement", "eau", "sol"
]

CONTENUS = [
    "🌾 Excellente récolte de mil cette saison ! La technique d'irrigation goutte-à-goutte a donné des résultats impressionnants. Rendement : 2,8 t/ha.",
    "🥜 Mes plants d'arachide sont en pleine floraison. Semences certifiées SONACOS — qualité top cette année ! Qui veut les coordonnées du fournisseur ?",
    "💧 Nouveau système d'irrigation solaire installé. Coût : 485 000 FCFA. Amortissement prévu en 1,5 saison. Je partage les détails techniques.",
    "🌿 Compostage naturel : bouse de vache + déchets végétaux + cendres. Après 6 semaines, mon sol est transformé. Matière organique x3 !",
    "⚠️ Alerte insectes sur les cultures de mil ! J'utilise de l'huile de neem (2%) — résultats probants sans pesticides chimiques.",
    "📈 Prix du marché Touba cette semaine : mil 350 FCFA/kg (+12%). Bonne période pour vendre. J'ai écoulé 1,2 tonne ce matin.",
    "🌧️ Les pluies arrivent ! Semis de fonio démarré hier soir. Technique : rangs espacés de 20 cm, profondeur 3 cm, 8 kg/ha.",
    "🥭 Première exportation de mangues Kent vers l'Europe réussie ! 2 tonnes à Rotterdam. Certification GlobalGAP obtenue.",
    "🔬 Étude comparative semences locales vs certifiées sur 3 saisons : +58% de rendement avec les certifiées. Les données complètes ci-dessous.",
    "🤝 Notre coopérative a vendu 18 tonnes d'arachide collectivement : prix obtenu +20% vs marché individuel. La solidarité ça paye !",
    "☀️ Sécheresse en cours dans la zone de Diourbel. Conseils d'urgence : paillage immédiat + irrigation nocturne. Qui a des stocks de paille ?",
    "🌱 Jachère améliorée au Mucuna : matière organique passée de 0,8% à 2,4% en une saison. Technique gratuite et efficace !",
    "🏆 Premier prix à la Foire Agricole de Ziguinchor pour mon système d'arrosage automatique à base d'Arduino ! Plans disponibles.",
    "📊 Mon bilan de saison : 3,2 t/ha de riz avec semences certifiées vs 2,1 t/ha avec semences locales. La différence est nette.",
    "🌾 Récolte de fonio en cours ! Culture d'avenir : cycle 70 jours, résistant à la sécheresse, prix premium 700 FCFA/kg.",
]

POST_TAGS = [
    ["irrigation", "récolte", "technique"],
    ["arachide", "semences", "conseil"],
    ["irrigation", "eau", "solaire"],
    ["sol", "fertilisation", "bio"],
    ["insectes", "bio", "protection"],
    ["marché", "mil", "vente"],
    ["semences", "pluie", "technique"],
    ["exportation", "mangue", "marché"],
    ["semences", "rendement", "riz"],
    ["coopérative", "arachide", "conseil"],
    ["sécheresse", "irrigation", "eau"],
    ["sol", "fertilisation", "technique"],
    ["technique", "innovation", "équipement"],
    ["riz", "semences", "récolte"],
    ["fonio", "récolte", "marché"],
]

IMAGES_AGRI = [
    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=700&q=80",
    "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=700&q=80",
    "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=700&q=80",
    "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=700&q=80",
    "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=700&q=80",
    "https://images.unsplash.com/photo-1586771107445-d3ca888129ff?w=700&q=80",
    "https://images.unsplash.com/photo-1622383563227-04401ab4e5ea?w=700&q=80",
    "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=700&q=80",
    "https://images.unsplash.com/photo-1593113598332-cd288d649433?w=700&q=80",
    "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=700&q=80",
    "https://images.unsplash.com/photo-1599420186946-7b6fb4e297f0?w=700&q=80",
    "https://images.unsplash.com/photo-1592991538534-00972b6f59ab?w=700&q=80",
    "https://images.unsplash.com/photo-1631556097153-16e48aada7a4?w=700&q=80",
    "https://images.unsplash.com/photo-1602595755085-59c94a55c80b?w=700&q=80",
    "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=700&q=80",
]

COMMENTAIRES_DEMO = [
    "Félicitations ! Des résultats impressionnants 👏",
    "Merci pour le partage, très utile pour notre région !",
    "Quelle variété de semences utilisez-vous exactement ?",
    "Je vais essayer cette technique dès la prochaine saison.",
    "Dans notre zone de Fatick, même constat cette année.",
    "Bravo ! Vous inspirez beaucoup d'agriculteurs.",
    "Est-ce que cette méthode fonctionne aussi pour le maïs ?",
    "Merci infiniment pour ce guide détaillé !",
]


def seed_database():
    """
    Insère 10 utilisateurs + admin + publications de démo.
    Réinitialise la base si elle contient déjà des données.
    """
    users_col = get_users_col()
    posts_col = get_posts_col()
    db = get_db()

    # Nettoyage
    users_col.drop()
    posts_col.drop()
    db.logs_admin.drop()
    print("🗑  Collections vidées.")

    # ── 1. Créer le compte Admin ───────────────────────────────────────────────
    admin_doc = {
        "pseudo":        "admin",
        "region":        "Dakar",
        "type_culture":  "Administration",
        "role":          "admin",
        "password":      hash_password("admin123"),
        "statut":        "actif",
        "followers":     [],
        "following":     [],
        "date_creation": datetime.now(),
    }
    users_col.insert_one(admin_doc)
    print("👑 Compte admin créé (pseudo: admin / mdp: admin123)")

    # ── 2. Insérer les 10 utilisateurs agriculteurs ───────────────────────────
    user_docs = []
    for u in USERS_DATA:
        user_docs.append({
            "pseudo":        u["pseudo"],
            "region":        u["region"],
            "type_culture":  u["type_culture"],
            "role":          "user",
            "password":      hash_password("agri123"),
            "statut":        "actif",
            "followers":     [],
            "following":     [],
            "date_creation": datetime.now() - timedelta(days=random.randint(10, 365)),
        })
    result = users_col.insert_many(user_docs)
    user_ids = result.inserted_ids
    print(f"👥 {len(user_ids)} utilisateurs insérés (mot de passe par défaut : agri123)")

    # ── Relations followers/following aléatoires ──────────────────────────────
    for uid in user_ids:
        autres = [x for x in user_ids if x != uid]
        follows = random.sample(autres, random.randint(2, 5))
        users_col.update_one({"_id": uid}, {"$set": {"following": follows}})
        for fid in follows:
            users_col.update_one({"_id": fid}, {"$push": {"followers": uid}})
    print("🤝 Relations followers/following créées.")

    # ── 3. Insérer les publications de démonstration ──────────────────────────
    all_users = list(users_col.find({"role": "user"}))
    now = datetime.now()

    for i, (contenu, tags) in enumerate(zip(CONTENUS, POST_TAGS)):
        auteur = all_users[i % len(all_users)]
        nb_likes = random.randint(1, 9)
        likers = random.sample(
            [u["_id"] for u in all_users if u["_id"] != auteur["_id"]],
            min(nb_likes, len(all_users) - 1)
        )
        nb_comms = random.randint(1, 3)
        commentaires = []
        for j in range(nb_comms):
            comm_auteur = random.choice(all_users)
            commentaires.append({
                "auteur_id":     comm_auteur["_id"],
                "auteur_pseudo": comm_auteur["pseudo"],
                "texte":         COMMENTAIRES_DEMO[random.randint(0, len(COMMENTAIRES_DEMO) - 1)],
                "date":          now - timedelta(hours=random.randint(1, 48)),
            })
        posts_col.insert_one({
            "auteur_id":     auteur["_id"],
            "auteur_pseudo": auteur["pseudo"],
            "contenu":       contenu,
            "image":         IMAGES_AGRI[i % len(IMAGES_AGRI)],
            "tags":          tags,
            "likes":         likers,
            "commentaires":  commentaires,
            "epingle":       False,
            "signalements":  [],
            "date":          now - timedelta(hours=random.randint(1, 96)),
        })

    print(f"📝 {len(CONTENUS)} publications de démonstration insérées.")
    print("✅ Base de données initialisée avec succès !\n")
    return user_ids


if __name__ == "__main__":
    seed_database()
