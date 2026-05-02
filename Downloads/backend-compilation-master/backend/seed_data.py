"""
╔══════════════════════════════════════════════════════════════╗
║        🌆 SMART CITY — GOUVERNORAT DE SOUSSE                 ║
║        Simulation réaliste des 17 délégations                ║
║        Aligné sur TN-sousse.geojson                         ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import SessionLocal, engine
from database.init_db import init_db
from models import (
    Zone, Capteur, Mesure, Intervention, Technicien,
    Proprietaire, Citoyen, Consultation, Vehicule, Trajet
)
from datetime import datetime, timedelta
import random
import math
import time

# ──────────────────────────────────────────────
#  17 DÉLÉGATIONS DE SOUSSE — alignées sur le GeoJSON
#  (del_fr exact + coordonnées GPS centrales)
# ──────────────────────────────────────────────

ZONES_SOUSSE = [
    {"nom": "Sousse Medina",            "surface": 3.2,  "pop": 42000, "lat": 35.8254, "lon": 10.6360, "type": "historique"},
    {"nom": "Sousse Jawhara",           "surface": 8.5,  "pop": 68000, "lat": 35.8417, "lon": 10.6042, "type": "residentiel"},
    {"nom": "Sousse Sidi Abedelhamid",  "surface": 6.1,  "pop": 55000, "lat": 35.8100, "lon": 10.6500, "type": "residentiel"},
    {"nom": "Hammam Sousse",            "surface": 12.4, "pop": 38000, "lat": 35.8597, "lon": 10.5933, "type": "touristique"},
    {"nom": "Sousse Riadh",             "surface": 9.8,  "pop": 47000, "lat": 35.8333, "lon": 10.6333, "type": "residentiel"},
    {"nom": "Zaouia Ksiba Thrayet",     "surface": 18.7, "pop": 22000, "lat": 35.7833, "lon": 10.7167, "type": "residentiel"},
    {"nom": "Kalaâ Seghira",            "surface": 14.3, "pop": 29000, "lat": 35.8667, "lon": 10.6833, "type": "residentiel"},
    {"nom": "Msaken",                   "surface": 25.6, "pop": 52000, "lat": 35.7306, "lon": 10.5833, "type": "commercial"},
    {"nom": "Kondar",                   "surface": 11.2, "pop": 18000, "lat": 35.7500, "lon": 10.6167, "type": "residentiel"},
    {"nom": "Kalaâ Kebira",             "surface": 20.1, "pop": 41000, "lat": 35.9000, "lon": 10.5333, "type": "commercial"},
    {"nom": "Akouda",                   "surface": 7.8,  "pop": 31000, "lat": 35.8750, "lon": 10.5667, "type": "touristique"},
    {"nom": "Enfidha",                  "surface": 45.2, "pop": 34000, "lat": 36.1333, "lon": 10.3667, "type": "industriel"},
    {"nom": "Hergla",                   "surface": 16.9, "pop": 12000, "lat": 36.0500, "lon": 10.5167, "type": "touristique"},
    {"nom": "Sid Bou Ali",              "surface": 22.5, "pop": 19000, "lat": 35.9833, "lon": 10.5667, "type": "residentiel"},
    {"nom": "Sidi El Hèni",            "surface": 31.0, "pop": 15000, "lat": 35.7667, "lon": 10.5333, "type": "residentiel"},
    {"nom": "Bouficha",                 "surface": 38.4, "pop": 26000, "lat": 36.2167, "lon": 10.5167, "type": "industriel"},
    # Note: une délégation apparaît sans nom (None) dans le GeoJSON → mappée ici
    
]

# ──────────────────────────────────────────────
#  DONNÉES DE RÉFÉRENCE
# ──────────────────────────────────────────────

FABRICANTS_CAPTEURS = [
    "Schneider Electric TN", "Siemens Maghreb", "ABB Tunisia",
    "Honeywell MENA", "Bosch IoT Solutions", "Teknica Sfax",
    "InnoTech Tunisie", "Satel Maghreb"
]

TYPES_CAPTEURS = {
    "pollution":   {"unite": "µg/m³", "description": "Capteur qualité air PM2.5/PM10"},
    "temperature": {"unite": "°C",    "description": "Sonde thermique ambiante"},
    "humidite":    {"unite": "%",     "description": "Hygromètre à condensateur"},
}

NOMS_TUNISIENS = [
    ("Ben Ali", "Mohamed"),    ("Trabelsi", "Sonia"),    ("Chaabane", "Youssef"),
    ("Riahi", "Amira"),        ("Hamdi", "Khalil"),      ("Gharbi", "Fatma"),
    ("Jlassi", "Anouar"),      ("Belhaj", "Leila"),      ("Karoui", "Slim"),
    ("Abidi", "Nadia"),        ("Ferchichi", "Tarek"),   ("Sellami", "Hajer"),
    ("Maaloul", "Riadh"),      ("Zouari", "Ines"),       ("Bouzid", "Karim"),
    ("Mansouri", "Olfa"),      ("Ayari", "Sami"),        ("Khlifi", "Manel"),
    ("Dridi", "Hichem"),       ("Ghannouchi", "Sara"),   ("Tlili", "Adel"),
    ("Chebbi", "Rahma"),       ("Jelassi", "Lotfi"),     ("Saidi", "Nour"),
    ("Oueslati", "Chaker"),    ("Derbel", "Asma"),       ("Haj Ali", "Mongi"),
    ("Frikha", "Wided"),       ("Baccouche", "Zied"),    ("Marzouki", "Emna"),
]

PRENOMS_TECH = [
    ("Hamdi", "Bilel"),         ("Rekik", "Imed"),          ("Ben Romdhane", "Wael"),
    ("Chouchane", "Marouen"),   ("Triki", "Firas"),         ("Gargouri", "Mehdi"),
    ("Baraket", "Nizar"),       ("Kamoun", "Iheb"),         ("Stambouli", "Yassine"),
    ("Ben Youssef", "Anis"),
]

EMAILS_DOMAINES = ["gmail.com", "yahoo.fr", "topnet.tn", "hexabyte.tn", "planet.tn"]

SPECIALITES_TECH = [
    "Électronique & Capteurs IoT",  "Réseaux & Télécommunications",
    "Maintenance Industrielle",      "Intelligence Artificielle & Data",
    "Énergie Solaire & Renouvelable","Systèmes Embarqués",
]

CERTIFICATIONS = [
    "ISO 9001 Qualité", "CEI 61000 CEM", "IEC 60068 Environnement",
    "AWS IoT Certified", "Cisco CCNA IoT", "ATEX Zone 1",
]

VEHICULES_DATA = [
    ("Bus Électrique CITé Sousse",  "bus_electrique",    "Électrique"),
    ("Tram Sousse T-100",           "tramway",           "Électrique"),
    ("Voiture Inspection ZOE",      "voiture_electrique","Électrique"),
    ("Vélo Cargo Smart Medina",     "velo_electrique",   "Électrique"),
    ("Scooter Patrol Sousse",       "scooter_electrique","Électrique"),
    ("Navette Autonome Hammam",     "navette_autonome",  "Hybride"),
    ("Camion Collecte Msaken",      "camion_hybride",    "Hybride"),
    ("Minibus Kalaâ Express",       "minibus_electrique","Électrique"),
]

TYPES_INTERVENTION = [
    "Remplacement capteur défaillant",  "Maintenance préventive réseau",
    "Réparation fuite eau",             "Inspection qualité air",
    "Installation nouveau nœud IoT",    "Mise à jour firmware capteurs",
    "Nettoyage panneau solaire",        "Contrôle système d'alarme",
]

IMPACTS_ENV = [
    "Faible — opération locale",
    "Moyen — zone résidentielle",
    "Fort — améliore qualité air",
    "Critique — réduction pollution immédiate",
]

# Quartiers réels de Sousse
QUARTIERS_SOUSSE = [
    "Cité Erriadh", "Bab El Bhar", "Hay Salam", "Ksar Hellal",
    "Cité Olympique", "Khezama", "Bouhsina", "Sahloul",
    "Cité Ezzouhour", "Cité El Wafa", "Centre Ville",
]

# ──────────────────────────────────────────────
#  UTILITAIRES
# ──────────────────────────────────────────────

def colored(text, code):
    return f"\033[{code}m{text}\033[0m"

def info(msg):   print(colored(f"  ✦ {msg}", "94"))
def ok(msg):     print(colored(f"  ✅ {msg}", "92"))
def warn(msg):   print(colored(f"  ⚡ {msg}", "93"))
def header(msg):
    print()
    print(colored("  " + "═"*60, "96"))
    print(colored(f"  🌊  {msg}", "96;1"))
    print(colored("  " + "═"*60, "96"))

def random_email(nom, prenom):
    dom = random.choice(EMAILS_DOMAINES)
    nom_clean = nom.lower().replace(' ', '').replace("'", '')
    return f"{prenom.lower()}.{nom_clean}@{dom}"

def random_phone():
    prefix = random.choice(["21","22","23","24","25","26","27","28","29",
                             "50","52","55","58","90","92","94","97","98","99"])
    return f"+216 {prefix} {random.randint(100,999):03d} {random.randint(100,999):03d}"

def random_date_past(days_back=730, days_recent=30):
    start = datetime.now() - timedelta(days=days_back)
    return start + timedelta(days=random.randint(0, days_back - days_recent))

# ──────────────────────────────────────────────
#  SIMULATION PHYSIQUE (Sousse — climat côtier)
# ──────────────────────────────────────────────

def simulate_temperature(ts: datetime, zone_type: str) -> float:
    hour  = ts.hour
    month = ts.month
    # Sousse : été chaud (~33°C), hiver doux (~12°C)
    seasonal_base = 22 + 11 * math.sin((month - 3) * math.pi / 6)
    diurnal = 6 * math.sin((hour - 5) * math.pi / 9) if 5 <= hour <= 23 else -3
    urban_heat = {
        "industriel": 2.5, "commercial": 1.8, "residentiel": 1.2,
        "touristique": 0.4, "historique": 1.0,
    }.get(zone_type, 1.0)
    return round(seasonal_base + diurnal + urban_heat + random.gauss(0, 0.3), 2)

def simulate_humidite(ts: datetime, zone_type: str) -> float:
    hour  = ts.hour
    month = ts.month
    # Sousse côtière : humidité plus élevée
    seasonal = 65 - 12 * math.sin((month - 3) * math.pi / 6)
    diurnal  = 8 * math.cos(hour * math.pi / 12)
    coastal  = 8 if zone_type == "touristique" else 0
    return round(max(25, min(95, seasonal + diurnal + coastal + random.gauss(0, 1.5))), 2)

def simulate_pollution(ts: datetime, zone_type: str) -> float:
    hour = ts.hour
    traffic_morning = 25 * math.exp(-((hour - 8) ** 2) / 2) if 5 <= hour <= 12 else 0
    traffic_evening = 20 * math.exp(-((hour - 18) ** 2) / 2) if 14 <= hour <= 23 else 0
    base = {
        "industriel": 42, "commercial": 26, "residentiel": 16,
        "touristique": 10, "historique": 20,
    }.get(zone_type, 18)
    return round(max(2, base + traffic_morning + traffic_evening + random.gauss(0, 2.0)), 2)


# ══════════════════════════════════════════════
#  FONCTIONS D'INSERTION
# ══════════════════════════════════════════════

def seed_zones(db):
    header("ZONES — 17 DÉLÉGATIONS DE SOUSSE")
    zones = []
    for z in ZONES_SOUSSE:
        zone = Zone(
            nom_zone=z["nom"],
            surface_km2=z["surface"],
            population=z["pop"],
            latitude=z["lat"],
            longitude=z["lon"],
            type_zone=z["type"],
        )
        db.add(zone)
        zones.append(zone)
        info(f"{z['nom']} ({z['type']}) — {z['pop']:,} hab. — {z['surface']} km²")
    db.commit()
    ok(f"{len(zones)} zones créées")
    return zones


def seed_capteurs(db, zones):
    header("CAPTEURS IoT PAR DÉLÉGATION")
    capteurs = []
    for zone in zones:
        nb = random.randint(3, 6)
        for i in range(nb):
            type_c = random.choice(list(TYPES_CAPTEURS.keys()))
            meta   = TYPES_CAPTEURS[type_c]
            lat_off = random.uniform(-0.015, 0.015)
            lon_off = random.uniform(-0.015, 0.015)
            c = Capteur(
                nom=f"CPT-{zone.id_zone:02d}-{i+1:03d}",
                type_capteur=type_c,
                statut=random.choices(
                    ["actif","actif","actif","maintenance","hors_service"],
                    weights=[7,7,7,2,1]
                )[0],
                taux_erreur=round(random.uniform(0.1, 4.5), 2),
                date_installation=random_date_past(900, 60),
                fabricant=random.choice(FABRICANTS_CAPTEURS),
                localisation_gps=f"{zone.latitude + lat_off:.6f}, {zone.longitude + lon_off:.6f}",
                description=meta["description"],
                unite=meta["unite"],
                id_zone=zone.id_zone,
            )
            db.add(c)
            capteurs.append(c)
        info(f"[{zone.nom_zone}] → {nb} capteurs")
    db.commit()
    ok(f"{len(capteurs)} capteurs enregistrés")
    return capteurs


def seed_mesures(db, capteurs, heures_historique=48):
    header(f"MESURES CAPTEURS — {heures_historique}h d'historique")
    actifs = [c for c in capteurs if c.statut == "actif"]

    zones_traitees = {}
    for capteur in actifs:
        zone = capteur.zone
        if zone and zone.id_zone not in zones_traitees:
            zones_traitees[zone.id_zone] = zone

    total      = 0
    batch_size = 500
    batch      = []
    now        = datetime.now()
    start_time = now - timedelta(hours=heures_historique)

    warn(f"Génération de mesures pour {len(zones_traitees)} délégations...")

    for zone in zones_traitees.values():
        zone_type = zone.type_zone or "residentiel"
        current   = start_time
        while current <= now:
            m = Mesure(
                timestamp=current,
                temperature=simulate_temperature(current, zone_type),
                humidite=simulate_humidite(current, zone_type),
                pollution=simulate_pollution(current, zone_type),
                id_zone=zone.id_zone,
            )
            batch.append(m)
            total   += 1
            current += timedelta(minutes=1)
            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                batch.clear()
                print(f"\r  📡 {total:,} mesures...", end="", flush=True)

    if batch:
        db.bulk_save_objects(batch)
        db.commit()
    print()
    ok(f"{total:,} mesures générées")
    return total


def seed_techniciens(db):
    header("TECHNICIENS DE TERRAIN — SOUSSE")
    techs = []
    for nom, prenom in PRENOMS_TECH:
        t = Technicien(
            nom=nom,
            prenom=prenom,
            specialite=random.choice(SPECIALITES_TECH),
            disponible=random.choice([True, True, True, False]),
            certification=random.choice(CERTIFICATIONS),
        )
        db.add(t)
        techs.append(t)
        statut = "🟢 Disponible" if t.disponible else "🔴 Occupé"
        info(f"{prenom} {nom} — {t.specialite} [{statut}]")
    db.commit()
    ok(f"{len(techs)} techniciens enregistrés")
    return techs


def seed_proprietaires(db):
    header("PROPRIÉTAIRES / ORGANISMES — SOUSSE")
    props = []
    entreprises = [
        ("STEG Sousse",          "Av. Habib Bourguiba, Sousse",   "société"),
        ("SONEDE Sousse",        "Rue de la République, Sousse",  "société"),
        ("Mairie de Sousse",     "Place Farhat Hached, Sousse",   "public"),
        ("ONAS Sousse",          "Route de Tunis, Sousse",        "public"),
        ("Tunisie Telecom Sss",  "Av. Mohamed V, Sousse",         "société"),
        ("SmartGov Sousse",      "Khezama Est, Sousse",           "public"),
        ("Nour IoT Sousse SARL", "Sahloul III, Sousse",           "privé"),
        ("Port Kantaoui Resort", "Port El Kantaoui, Sousse",      "privé"),
    ]
    for nom, adresse, type_ in entreprises:
        p = Proprietaire(
            nom=nom,
            adresse=adresse,
            telephone=random_phone(),
            email="contact@{}.tn".format(nom.lower().replace(' ','').replace("'",'')),
            type=type_,
            siret=f"TN{random.randint(10000000, 99999999)}",
        )
        db.add(p)
        props.append(p)
        info(f"{nom} ({type_}) — {adresse}")
    db.commit()
    ok(f"{len(props)} propriétaires enregistrés")
    return props


def seed_citoyens(db, zones):
    header("CITOYENS CONNECTÉS — SOUSSE")
    citoyens = []
    mobilites = ["vélo","transport_commun","covoiturage","marche","voiture_electrique"]
    for i, (nom, prenom) in enumerate(NOMS_TUNISIENS):
        zone    = zones[i % len(zones)]
        quartier = random.choice(QUARTIERS_SOUSSE)
        c = Citoyen(
            nom=nom,
            prenom=prenom,
            email=random_email(nom, prenom),
            telephone=random_phone(),
            score_ecolo=random.randint(12, 98),
            date_inscription=random_date_past(365, 10),
            preference_mobilite=random.choice(mobilites),
            adresse=f"Rue {random.randint(1,50)}, {quartier}, {zone.nom_zone}",
            id_zone=zone.id_zone,
        )
        db.add(c)
        citoyens.append(c)
        info(f"{prenom} {nom} — Score éco: {c.score_ecolo}/100 — {zone.nom_zone}")
    db.commit()
    ok(f"{len(citoyens)} citoyens enregistrés")
    return citoyens


def seed_interventions(db, zones, proprietaires, techniciens):
    header("INTERVENTIONS TERRAIN — SOUSSE")
    interventions = []
    priorites = ["basse","normale","haute","critique"]
    statuts   = ["planifiée","en_cours","terminée","annulée"]
    for i in range(20):
        zone  = random.choice(zones)
        prop  = random.choice(proprietaires)
        tech  = random.choice(techniciens)
        date_dem = random_date_past(180, 0)
        duree    = random.randint(1, 15)
        ia_ok    = random.choice([True, True, True, False])
        inv = Intervention(
            statut=random.choice(statuts),
            priorite=random.choice(priorites),
            ia_validee=ia_ok,
            cout=random.randint(800, 15000),
            nature_intervention=random.choice(TYPES_INTERVENTION),
            impact_environnemental=random.choice(IMPACTS_ENV),
            date_demande=date_dem,
            date_debut=date_dem + timedelta(days=random.randint(1, 5)),
            date_fin=date_dem + timedelta(days=duree),
            id_zone=zone.id_zone,
            id_proprietaire=prop.id_proprietaire,
            id_technicien=tech.id_technicien,
        )
        db.add(inv)
        interventions.append(inv)
        ia_icon = "🤖✅" if ia_ok else "🤖❌"
        info(f"[{inv.priorite.upper()}] {inv.nature_intervention} — {ia_icon} — {inv.cout} TND — {zone.nom_zone}")
    db.commit()
    ok(f"{len(interventions)} interventions créées")
    return interventions


def seed_consultations(db, zones):
    header("CONSULTATIONS PUBLIQUES — SOUSSE")
    sujets = [
        ("Plan Mobilité Verte Sousse 2026",        "mobilité"),
        ("Gestion déchets Medina Sousse",          "environnement"),
        ("Éclairage LED adaptatif Hammam Sousse",  "énergie"),
        ("Capteurs qualité eau Enfidha",           "eau"),
        ("Revitalisation Médina Sousse",           "urbanisme"),
        ("WiFi public Kantaoui",                   "numérique"),
        ("Jardins urbains Msaken",                 "biodiversité"),
        ("Pistes cyclables Kalaâ Kebira",          "mobilité"),
        ("Tri sélectif Akouda",                    "environnement"),
        ("Tableau de bord citoyen Smart Sousse",   "numérique"),
    ]
    consultations = []
    for titre, type_ in sujets:
        zone = random.choice(zones)
        c = Consultation(
            titre=titre,
            date_consultation=random_date_past(90, 0),
            statut=random.choice(["ouverte","ouverte","clôturée","en_analyse"]),
            description=f"Consultation citoyenne : {titre}. Participation active encouragée via l'application Smart City Sousse.",
            type_consultation=type_,
            id_zone=zone.id_zone,
        )
        db.add(c)
        consultations.append(c)
        info(f"[{type_}] {titre} — {zone.nom_zone}")
    db.commit()
    ok(f"{len(consultations)} consultations enregistrées")
    return consultations


def seed_vehicules(db):
    header("FLOTTE VÉHICULES SMART — SOUSSE")
    vehicules = []
    statuts = ["actif","actif","actif","en_charge","maintenance"]
    for modele, type_v, energie in VEHICULES_DATA:
        v = Vehicule(
            modele=modele,
            statut=random.choice(statuts),
            batterie_pct=round(random.uniform(35, 98), 1),
            vitesse_kmh=round(random.uniform(0, 65), 1) if random.random() > 0.3 else 0.0,
            type_vehicule=type_v,
            energie_utilisee=energie,
        )
        db.add(v)
        vehicules.append(v)
        info(f"{modele} ({energie}) — Batterie: {v.batterie_pct}% — {v.vitesse_kmh} km/h")
    db.commit()
    ok(f"{len(vehicules)} véhicules enregistrés")
    return vehicules


def seed_trajets(db, vehicules, zones):
    header("TRAJETS — RÉSEAU SOUSSE")
    trajets = []
    noms_zones = [z.nom_zone for z in zones]
    for vehicule in vehicules:
        nb = random.randint(4, 10)
        for _ in range(nb):
            orig = random.choice(noms_zones)
            dest = random.choice([z for z in noms_zones if z != orig])
            dist = round(random.uniform(2.5, 35.0), 1)   # distances intra-Sousse
            duree = round(dist * random.uniform(1.2, 2.8), 1)
            eco   = round(dist * random.uniform(0.08, 0.22), 3)
            date_dep = random_date_past(30, 0)
            t = Trajet(
                date_debut=date_dep,
                date_fin=date_dep + timedelta(minutes=int(duree)),
                distance_km=dist,
                duree_min=duree,
                economie_co2=eco,
                statut=random.choice(["terminé","terminé","en_cours","planifié"]),
                origine=orig,
                destination=dest,
                id_vehicule=vehicule.id_vehicule,
            )
            db.add(t)
            trajets.append(t)
    db.commit()
    ok(f"{len(trajets)} trajets enregistrés")
    return trajets


# ══════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════

def run_seed():
    print()
    print(colored("╔" + "═"*62 + "╗", "95;1"))
    print(colored("║   🌊 SMART CITY SOUSSE — INITIALISATION BASE DE DONNÉES   ║", "95;1"))
    print(colored("║        17 Délégations · Simulation IoT Réaliste            ║", "95;1"))
    print(colored("╚" + "═"*62 + "╝", "95;1"))
    print()

    t0 = time.time()
    info("Initialisation du schéma base de données...")
    init_db()
    ok("Schéma prêt")

    db = SessionLocal()
    try:
        zones         = seed_zones(db)
        capteurs      = seed_capteurs(db, zones)
        db.expire_all()
        capteurs_full = db.query(Capteur).all()
        for c in capteurs_full:
            _ = c.zone

        mesures_count = seed_mesures(db, capteurs_full, heures_historique=48)
        techniciens   = seed_techniciens(db)
        proprietaires = seed_proprietaires(db)
        seed_citoyens(db, zones)
        seed_interventions(db, zones, proprietaires, techniciens)
        seed_consultations(db, zones)
        vehicules     = seed_vehicules(db)
        seed_trajets(db, vehicules, zones)

        elapsed = time.time() - t0
        print()
        print(colored("╔" + "═"*62 + "╗", "92;1"))
        print(colored("║               ✅  SEED SOUSSE TERMINÉ                    ║", "92;1"))
        print(colored(f"║   ⏱️  Durée : {elapsed:.1f}s{' '*(46-len(f'{elapsed:.1f}'))}║", "92;1"))
        print(colored(f"║   📊  {mesures_count:,} mesures IoT insérées{' '*(35-len(str(mesures_count)))}║", "92;1"))
        print(colored("║   🇹🇳  17 délégations de Sousse prêtes !                 ║", "92;1"))
        print(colored("╚" + "═"*62 + "╝", "92;1"))
        print()

    except Exception as e:
        db.rollback()
        print(colored(f"\n  ❌ ERREUR : {e}", "91;1"))
        import traceback; traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()