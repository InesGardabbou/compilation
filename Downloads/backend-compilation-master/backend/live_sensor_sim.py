"""
╔══════════════════════════════════════════════════════════════╗
║        📡 LIVE SENSOR SIMULATOR — SOUSSE                     ║
║        Simule les capteurs IoT en temps réel                 ║
║        Compatible avec seed.py (17 délégations)              ║
║        Envoie via PostgreSQL NOTIFY → WebSocket              ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import time
import math
import random
import json
import signal
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host":     os.getenv("DB_HOST", "127.0.0.1"),
    "port":     os.getenv("DB_PORT", "5432"),
}

INTERVAL_SECONDS = 5        # intervalle entre chaque batch de mesures
CHANNEL          = "new_mesure_channel"

# ──────────────────────────────────────────────
#  17 ZONES SOUSSE — doit correspondre EXACTEMENT
#  aux id_zone insérés par seed.py (ordre = id)
# ──────────────────────────────────────────────

ZONES_SOUSSE = [
    {"id": 65, "nom": "Sousse Medina",           "type": "historique"},
    {"id": 66, "nom": "Sousse Jawhara",          "type": "residentiel"},
    {"id": 67, "nom": "Sousse Sidi Abedelhamid", "type": "residentiel"},
    {"id": 68, "nom": "Hammam Sousse",           "type": "touristique"},
    {"id": 69, "nom": "Sousse Riadh",            "type": "residentiel"},
    {"id": 70, "nom": "Zaouia Ksiba Thrayet",    "type": "residentiel"},
    {"id": 71, "nom": "Kalaâ Seghira",           "type": "residentiel"},
    {"id": 72, "nom": "Msaken",                  "type": "commercial"},
    {"id": 73, "nom": "Kondar",                  "type": "residentiel"},
    {"id": 74, "nom": "Kalaâ Kebira",            "type": "commercial"},
    {"id": 75, "nom": "Akouda",                  "type": "touristique"},
    {"id": 76, "nom": "Enfidha",                 "type": "industriel"},
    {"id": 77, "nom": "Hergla",                  "type": "touristique"},
    {"id": 78, "nom": "Sid Bou Ali",             "type": "residentiel"},
    {"id": 79, "nom": "Sidi El Hèni",            "type": "residentiel"},
    {"id": 80, "nom": "Bouficha",                "type": "industriel"},
]

# ──────────────────────────────────────────────
#  SIMULATION PHYSIQUE — identique à seed.py
# ──────────────────────────────────────────────

def simulate_temperature(ts: datetime, zone_type: str) -> float:
    hour  = ts.hour
    month = ts.month
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

# ──────────────────────────────────────────────
#  UTILITAIRES CONSOLE
# ──────────────────────────────────────────────

def colored(text, code):
    return f"\033[{code}m{text}\033[0m"

def log_info(msg):  print(colored(f"  ✦ {msg}", "94"))
def log_ok(msg):    print(colored(f"  ✅ {msg}", "92"))
def log_warn(msg):  print(colored(f"  ⚡ {msg}", "93"))
def log_err(msg):   print(colored(f"  ❌ {msg}", "91"))

POLLUTION_EMOJI = lambda p: "🟢" if p < 30 else ("🟡" if p <= 60 else "🔴")

# ──────────────────────────────────────────────
#  INSERTION EN BASE + NOTIFY
# ──────────────────────────────────────────────

INSERT_SQL = """
    INSERT INTO mesures (timestamp, temperature, humidite, pollution, id_zone)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id_mesure;
"""

NOTIFY_SQL = "SELECT pg_notify(%s, %s);"

def insert_and_notify(cur, zone: dict, ts: datetime) -> dict:
    """Insère une mesure et envoie le NOTIFY PostgreSQL."""
    temp  = simulate_temperature(ts, zone["type"])
    humid = simulate_humidite(ts, zone["type"])
    poll  = simulate_pollution(ts, zone["type"])

    cur.execute(INSERT_SQL, (ts, temp, humid, poll, zone["id"]))
    id_mesure = cur.fetchone()[0]

    payload = {
        "id_mesure":   id_mesure,
        "timestamp":   ts.isoformat(),
        "pollution":   poll,
        "temperature": temp,
        "humidite":    humid,
        "id_zone":     zone["id"],
    }

    cur.execute(NOTIFY_SQL, (CHANNEL, json.dumps(payload)))
    return payload

# ──────────────────────────────────────────────
#  BOUCLE PRINCIPALE
# ──────────────────────────────────────────────

running = True

def handle_signal(sig, frame):
    global running
    print()
    log_warn("Signal reçu — arrêt propre...")
    running = False

signal.signal(signal.SIGINT,  handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def run_simulator():
    global ZONES_SOUSSE
    print()
    print(colored("╔" + "═"*62 + "╗", "95;1"))
    print(colored("║   📡 LIVE SENSOR SIM — GOUVERNORAT DE SOUSSE             ║", "95;1"))
    print(colored(f"║   {len(ZONES_SOUSSE)} zones · toutes les {INTERVAL_SECONDS}s · canal: {CHANNEL:<20}║", "95;1"))
    print(colored("╚" + "═"*62 + "╝", "95;1"))
    print()

    conn = None
    cycle = 0

    while running:
        try:
            # (Re)connexion si nécessaire
            if conn is None or conn.closed:
                log_info("Connexion PostgreSQL...")
                conn = psycopg2.connect(**DB_CONFIG)
                conn.autocommit = True
                log_ok("Connecté ✓")
                
                # Fetch actual zones from the database to get the correct IDs
                cur = conn.cursor()
                cur.execute("SELECT id_zone, nom_zone, type_zone FROM zones ORDER BY id_zone;")
                db_zones = cur.fetchall()
                if db_zones:
                    ZONES_SOUSSE = [{"id": row[0], "nom": row[1], "type": row[2]} for row in db_zones]
                cur.close()

            cur = conn.cursor()
            ts  = datetime.now()
            cycle += 1

            print()
            print(colored(f"  ── Cycle #{cycle} · {ts.strftime('%H:%M:%S')} ──────────────────────────────", "96"))

            sent = 0
            for zone in ZONES_SOUSSE:
                try:
                    payload = insert_and_notify(cur, zone, ts)
                    p = payload["pollution"]
                    print(
                        f"  {POLLUTION_EMOJI(p)} "
                        f"Zone {zone['id']:>2} · {zone['nom']:<28} "
                        f"🌡{payload['temperature']:>5.1f}°C  "
                        f"🌫{p:>5.1f}µg  "
                        f"💧{payload['humidite']:>5.1f}%"
                    )
                    sent += 1
                except Exception as zone_err:
                    log_err(f"Zone {zone['id']} ({zone['nom']}): {zone_err}")

            cur.close()
            log_ok(f"{sent}/{len(ZONES_SOUSSE)} mesures envoyées · prochain batch dans {INTERVAL_SECONDS}s")

        except psycopg2.OperationalError as e:
            log_err(f"Connexion perdue : {e}")
            if conn and not conn.closed:
                conn.close()
            conn = None
            log_warn("Reconnexion dans 5s...")
            time.sleep(10)
            continue

        except Exception as e:
            log_err(f"Erreur inattendue : {e}")
            import traceback; traceback.print_exc()

        # Attendre avant le prochain cycle
        for _ in range(INTERVAL_SECONDS * 10):
            if not running:
                break
            time.sleep(0.1)

    # Nettoyage
    if conn and not conn.closed:
        conn.close()

    print()
    print(colored("╔" + "═"*62 + "╗", "93;1"))
    print(colored(f"║   📡 Simulateur arrêté après {cycle} cycles                     ║", "93;1"))
    print(colored("╚" + "═"*62 + "╝", "93;1"))
    print()


if __name__ == "__main__":
    run_simulator()