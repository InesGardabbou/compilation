# 🏙️ Smart City Tunisia — Backend API + WebSocket Temps Réel

> API FastAPI pour la gestion d'une ville intelligente (Sousse, Tunisie).  
> Surveillance IoT en temps réel via PostgreSQL NOTIFY → WebSocket → Frontend.

---

## 📁 Structure du projet

```
project/
├── main.py                  # Point d'entrée FastAPI
├── live_sensor_sim.py       # Simulateur de capteurs IoT (temps réel)
├── seed_data.py             # Peuplement initial de la base de données
│
├── database/
│   ├── db.py                # Connexion SQLAlchemy + session
│   ├── init_db.py           # Création des tables ORM
│   └── listener.py          # Listener PostgreSQL NOTIFY → WebSocket
│
├── websocket/
│   └── manager.py           # Gestionnaire des connexions WebSocket
│
├── models/                  # Modèles SQLAlchemy (ORM)
│   ├── zone.py
│   ├── capteur.py
│   ├── mesure.py
│   ├── intervention.py
│   ├── technicien.py
│   ├── citoyen.py
│   ├── proprietaire.py
│   ├── consultation.py
│   ├── vehicule.py
│   ├── trajet.py
│   └── historique.py
│
├── routes/                  # Endpoints API REST
│   ├── zone_routes.py
│   ├── capteur_routes.py
│   ├── mesure_routes.py
│   ├── intervention_routes.py
│   ├── technicien_routes.py
│   ├── vehicule_routes.py
│   ├── trajet_routes.py
│   ├── citoyen_routes.py
│   ├── proprietaire_routes.py
│   ├── consultation_routes.py
│   ├── kpis.py
│   ├── ia.py
│   ├── compilateur.py       # NLP → SQL
│   └── automates.py
│
├── schemas/
│   └── schemas.py           # Schémas Pydantic (validation)
│
└── services/
    ├── ia_generative.py     # Moteur IA (rapports, anomalies)
    ├── compilateur.py       # Compilateur langage naturel → SQL
    └── automates.py         # Automates finis
```

---

## ⚙️ Installation

### 1. Prérequis

- Python 3.11+
- PostgreSQL 14+
- pip

---

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

---

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Contenu du `requirements.txt` (basé sur les imports réels du projet) :

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
pydantic
openai
```

| Package | Fichier(s) source | Rôle |
|---|---|---|
| `fastapi` | `main.py`, tous les `routes/*.py` | Framework API REST + WebSocket |
| `uvicorn` | runner CLI | Serveur ASGI pour lancer FastAPI |
| `sqlalchemy` | `database/db.py`, tous les `models/*.py`, `routes/*.py` | ORM — mappage Python ↔ PostgreSQL |
| `psycopg2-binary` | `database/listener.py`, `live_sensor_sim.py`, `services/ia_generative.py`, `services/automates.py` | Driver PostgreSQL natif (LISTEN/NOTIFY, insertions directes) |
| `python-dotenv` | `database/db.py`, `database/listener.py`, `live_sensor_sim.py`, `services/ia_generative.py` | Lecture du fichier `.env` |
| `pydantic` | `schemas/schemas.py`, `routes/ia.py`, `routes/compilateur.py` | Validation et sérialisation des données |
| `openai` | `services/ia_generative.py` | Appel à l'API OpenAI pour les rapports et suggestions IA |

---

### 4. Créer la base de données PostgreSQL

Connectez-vous à PostgreSQL en tant que superuser et exécutez :

```sql
CREATE DATABASE smart_city_db;
```

---

### 5. Configurer le fichier `.env`

Créez un fichier `.env` à la racine du projet :

```env
DB_USER=smart_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_city_db
```

> ⚠️ Ne commitez jamais votre `.env` dans git. Ajoutez-le à `.gitignore`.

---

### 6. Créer les tables (init DB)

```bash
python main.py
```

Ou directement via uvicorn (les tables se créent au démarrage) :

```bash
uvicorn main:app --reload
```

SQLAlchemy va automatiquement créer toutes les tables définies dans les modèles grâce à `init_db()` appelé dans le hook `on_startup`.

---

### 7. Peupler la base avec les données initiales

```bash
python seed_data.py
```

Ce script insère les données de référence : zones de Sousse (17 délégations), capteurs IoT, techniciens, véhicules, citoyens, et historique de mesures simulées.

---

### 8. Créer le trigger PostgreSQL pour le temps réel

Connectez-vous à votre base `smart_city_db` et exécutez ces deux commandes SQL :

```sql
-- 1. Créer la fonction qui envoie la notification
CREATE OR REPLACE FUNCTION notify_new_mesure()
RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify(
    'new_mesure_channel',
    row_to_json(NEW)::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Attacher la fonction au trigger sur la table mesures
CREATE TRIGGER mesure_insert_trigger
AFTER INSERT ON mesures
FOR EACH ROW
EXECUTE FUNCTION notify_new_mesure();
```

> ✅ Vérification : `\df notify_new_mesure` dans psql doit retourner la fonction.

---

### 9. Lancer le simulateur temps réel

Dans un **second terminal** (le serveur FastAPI doit déjà tourner) :

```bash
python live_sensor_sim.py
```

Le simulateur insère une mesure par zone toutes les 5 secondes, ce qui déclenche le trigger PostgreSQL, qui envoie un NOTIFY, que le listener capte et diffuse via WebSocket au frontend.

---

## 🚀 Démarrage complet (ordre recommandé)

```bash
# Terminal 1 — API + WebSocket server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Simulateur IoT temps réel
python live_sensor_sim.py
```

Accès : `http://localhost:8000/docs` — Documentation Swagger interactive.

---

## 🔌 WebSocket — Architecture Temps Réel

### Schéma du flux

```
[live_sensor_sim.py]
       │
       │  INSERT INTO mesures
       ▼
[PostgreSQL]
       │
       │  TRIGGER → pg_notify('new_mesure_channel', JSON)
       ▼
[database/listener.py]   ← thread daemon lancé au démarrage FastAPI
       │
       │  LISTEN new_mesure_channel
       │  Enrichit les données (nom_zone, type_zone)
       │  asyncio.run(manager.broadcast(...))
       ▼
[websocket/manager.py]
       │
       │  send_json() à tous les clients connectés
       ▼
[Frontend React/Vue/JS]
       │
       └─ ws://localhost:8000/ws/dashboard
```

---

### Endpoint WebSocket

```
ws://localhost:8000/ws/dashboard
```

**Connexion côté frontend (JavaScript) :**

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/dashboard");

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === "NEW_MESURE") {
    const mesure = message.data;
    console.log("Nouvelle mesure reçue :", mesure);
    // Exemple de payload :
    // {
    //   "id_mesure": 1042,
    //   "timestamp": "2026-04-29T14:30:05.123",
    //   "pollution": 23.7,
    //   "temperature": 28.4,
    //   "humidite": 61.2,
    //   "id_zone": 65,
    //   "nom_zone": "Sousse Medina",
    //   "type_zone": "historique"
    // }
  }
};
```

---

### Explication du trigger PostgreSQL

```sql
-- Fonction PL/pgSQL déclenchée à chaque INSERT sur "mesures"
CREATE OR REPLACE FUNCTION notify_new_mesure()
RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify(
    'new_mesure_channel',  -- nom du canal d'écoute
    row_to_json(NEW)::text -- payload = la nouvelle ligne convertie en JSON
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger : s'exécute AFTER INSERT, pour chaque ligne
CREATE TRIGGER mesure_insert_trigger
AFTER INSERT ON mesures
FOR EACH ROW
EXECUTE FUNCTION notify_new_mesure();
```

**Pourquoi AFTER INSERT et non BEFORE ?**
Le `AFTER INSERT` garantit que la ligne est bien committée en base avant d'envoyer la notification. Avec `BEFORE`, la ligne pourrait ne pas encore exister si la transaction est annulée.

**`row_to_json(NEW)`** convertit automatiquement la ligne insérée en objet JSON avec tous ses champs (id_mesure, timestamp, pollution, temperature, humidite, id_zone).

**`pg_notify`** est une fonction PostgreSQL native qui publie un message sur un canal. Tous les processus qui écoutent ce canal (`LISTEN`) reçoivent le message instantanément.

---

### Explication du Listener Python (`database/listener.py`)

```
1. Ouvre une connexion psycopg2 dédiée (séparée de SQLAlchemy)
2. Se met en mode AUTOCOMMIT (obligatoire pour LISTEN/NOTIFY)
3. Exécute : LISTEN new_mesure_channel
4. Boucle infinie avec select() — attend des événements sans bloquer le CPU
5. À chaque NOTIFY reçu :
   - Parse le JSON de la mesure
   - Enrichit avec nom_zone et type_zone (requête SQL supplémentaire)
   - Diffuse via manager.broadcast() à tous les WebSocket clients connectés
```

Ce listener tourne dans un **thread daemon** lancé au démarrage de FastAPI, donc il ne bloque pas le serveur.

---

### Gestionnaire WebSocket (`websocket/manager.py`)

```python
class ConnectionManager:
    active_connections = []   # liste des WebSockets actifs

    async def connect(websocket):     # accepte + enregistre
    def disconnect(websocket):        # supprime de la liste
    async def broadcast(data):        # envoie JSON à TOUS les clients
```

Chaque fois qu'un frontend se connecte à `/ws/dashboard`, il est ajouté à `active_connections`. Le `broadcast()` itère cette liste et pousse le message à chacun simultanément.

---

## 📡 API REST — Référence complète

### 🗺️ Zones — `/zones`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/zones/` | Lister toutes les zones |
| `GET` | `/zones/{id_zone}` | Détail d'une zone |
| `POST` | `/zones/` | Créer une zone |
| `PUT` | `/zones/{id_zone}` | Mettre à jour une zone |
| `DELETE` | `/zones/{id_zone}` | Supprimer une zone |

Une **zone** représente une délégation géographique (ex: Sousse Medina, Hammam Sousse). Elle contient : `nom_zone`, `type_zone` (historique, résidentiel, commercial, touristique, industriel), `surface_km2`, `population`, `latitude`, `longitude`.

---

### 📟 Capteurs — `/capteurs`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/capteurs/` | Lister tous les capteurs |
| `GET` | `/capteurs/{id_capteur}` | Détail d'un capteur |
| `GET` | `/capteurs/zone/{id_zone}` | Capteurs d'une zone |
| `POST` | `/capteurs/` | Créer un capteur |
| `PUT` | `/capteurs/{id_capteur}` | Mettre à jour un capteur |
| `PATCH` | `/capteurs/{id_capteur}/statut?statut=actif` | Changer le statut |
| `DELETE` | `/capteurs/{id_capteur}` | Supprimer un capteur |

Statuts disponibles : `actif`, `maintenance`, `hors_service`.

---

### 📊 Mesures — `/mesures`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/mesures/` | Lister les mesures (avec filtres) |
| `GET` | `/mesures/{id_mesure}` | Détail d'une mesure |
| `GET` | `/mesures/zone/{id_zone}/dernieres?n=60` | Dernières N mesures d'une zone |
| `GET` | `/mesures/zone/{id_zone}/live` | **Dernière mesure en temps réel** |
| `POST` | `/mesures/` | Enregistrer une mesure manuellement |
| `PUT` | `/mesures/{id_mesure}` | Mettre à jour une mesure |
| `DELETE` | `/mesures/{id_mesure}` | Supprimer une mesure |
| `DELETE` | `/mesures/zone/{id_zone}/all` | Supprimer toutes les mesures d'une zone |

**Filtres disponibles sur `GET /mesures/`** :
- `?id_zone=65` — filtrer par zone
- `?depuis=2026-04-01T00:00:00` — depuis une date
- `?jusqu=2026-04-29T23:59:59` — jusqu'à une date
- `?skip=0&limit=100` — pagination

Chaque mesure contient : `timestamp`, `temperature` (°C), `humidite` (%), `pollution` (µg/m³), `id_zone`.

---

### 🔧 Interventions — `/interventions`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/interventions/` | 5 dernières interventions |
| `GET` | `/interventions/all` | Toutes les interventions |
| `GET` | `/interventions/zone/{id_zone}` | Interventions d'une zone |
| `POST` | `/interventions/` | Créer une intervention |
| `PUT` | `/interventions/{id_intervention}` | Mettre à jour |
| `DELETE` | `/interventions/{id_intervention}` | Supprimer |

---

### 👨‍🔧 Techniciens — `/techniciens`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/techniciens/` | Lister tous les techniciens |
| `GET` | `/techniciens/{id_technicien}` | Détail d'un technicien |
| `POST` | `/techniciens/` | Créer un technicien |
| `PUT` | `/techniciens/{id_technicien}` | Mettre à jour |
| `DELETE` | `/techniciens/{id_technicien}` | Supprimer |

Champ clé : `disponible` (booléen) — utilisé par le dashboard KPI.

---

### 🚗 Véhicules — `/vehicules`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/vehicules/` | Lister tous les véhicules |
| `GET` | `/vehicules/{id_vehicule}` | Détail d'un véhicule |
| `POST` | `/vehicules/` | Créer un véhicule |
| `PUT` | `/vehicules/{id_vehicule}` | Mettre à jour |
| `DELETE` | `/vehicules/{id_vehicule}` | Supprimer |

Statuts : `actif`, `en_maintenance`, `hors_service`.

---

### 🛣️ Trajets — `/trajets`

Gestion des trajets effectués par les véhicules. Chaque trajet enregistre : `distance_km`, `duree_minutes`, `economie_co2` (kg de CO₂ économisé).

---

### 👥 Citoyens — `/citoyens`

CRUD complet des citoyens de la ville.

---

### 🏠 Propriétaires — `/proprietaires`

CRUD complet des propriétaires de biens.

---

### 🗨️ Consultations — `/consultations`

Gestion des consultations citoyennes liées aux zones.

---

### 📈 KPIs Dashboard — `/kpis`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/kpis/dashboard` | **Tableau de bord global Smart City** |

Retourne en un seul appel :
```json
{
  "smart_city": "Tunisia 🇹🇳",
  "zones": 17,
  "capteurs": { "total": 85, "actifs": 70, "en_maintenance": 10, "hors_service": 5 },
  "mesures": {
    "total": 12500,
    "derniere_mesure": "2026-04-29T14:30:05",
    "moyennes": { "pollution_µg_m3": 24.5, "temperature_C": 27.3, "humidite_pct": 63.1 }
  },
  "interventions": { "en_cours": 3, "critiques": 1 },
  "vehicules": { "total": 20, "actifs": 15 },
  "environnement": { "co2_economise_kg_total": 842.5 },
  "techniciens_disponibles": 8,
  "citoyens": 450
}
```

---

### 🤖 IA Générative — `/ia`

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/ia/rapport` | Générer un rapport IA (type: pollution, température…) |
| `GET` | `/ia/suggestions` | Obtenir des suggestions d'actions IA |
| `POST` | `/ia/valider` | Valider une transition d'état via IA |

---

### 🗣️ NLP → SQL — `/nl`

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/nl/query` | Convertir une question en langage naturel en requête SQL et l'exécuter |

**Exemple de requête :**
```json
POST /nl/query
{ "phrase": "quelles sont les zones avec une pollution supérieure à 50 ?" }
```

---

### ⚙️ Automates — `/automates`

Gestion des automates finis pour la logique métier de la ville (transitions d'états des équipements).

---

## 🔗 URLs utiles

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Documentation Swagger interactive |
| `http://localhost:8000/redoc` | Documentation ReDoc |
| `http://localhost:8000/health` | Health check API + DB |
| `ws://localhost:8000/ws/dashboard` | WebSocket temps réel |

---

## ❓ FAQ

**Q: Le trigger ne se déclenche pas.**  
R: Vérifiez que vous avez bien exécuté les deux commandes SQL (la fonction ET le trigger). Testez avec : `INSERT INTO mesures (timestamp, temperature, humidite, pollution, id_zone) VALUES (NOW(), 25.0, 60.0, 30.0, 65);`

**Q: Le WebSocket ne reçoit rien.**  
R: Assurez-vous que `live_sensor_sim.py` tourne, que le listener est actif (logs `📡 Listening PostgreSQL events...` dans la console uvicorn) et que le trigger est créé.

**Q: `psycopg2.OperationalError`**  
R: Vérifiez vos variables `.env` et que PostgreSQL accepte les connexions depuis localhost.

**Q: `ModuleNotFoundError`**  
R: Assurez-vous que votre environnement virtuel est activé et que tous les packages sont installés.