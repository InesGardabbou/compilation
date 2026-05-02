import psycopg2
import select
import json
import asyncio
from websocket.manager import manager
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def start_listener():
    conn = psycopg2.connect("postgresql://postgres:1234@localhost:5433/city")

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("LISTEN new_mesure_channel;")

    print("📡 Listening PostgreSQL events...")

    while True:
        if select.select([conn], [], [], 5) == ([], [], []):
            continue

        conn.poll()

        while conn.notifies:
            notify = conn.notifies.pop(0)

            data = json.loads(notify.payload)

            # 🔥 AJOUT IMPORTANT : récupérer infos zone
            cur.execute("""
                SELECT nom_zone, type_zone
                FROM zones
                WHERE id_zone = %s
            """, (data["id_zone"],))

            zone = cur.fetchone()

            if zone:
                data["nom_zone"] = zone[0]
                data["type_zone"] = zone[1]

            print("📨 ENRICHED DATA:", data)

            asyncio.run(manager.broadcast({
                "type": "NEW_MESURE",
                "data": data
            }))