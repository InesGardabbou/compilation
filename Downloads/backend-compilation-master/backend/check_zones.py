import sys
import os

# Add the backend directory to sys.path
backend_path = r'c:\Users\guita\Downloads\backend-compilation-master\backend'
sys.path.append(backend_path)

from database.db import SessionLocal
from models.zone import Zone

db = SessionLocal()
try:
    zones = db.query(Zone).all()
    print(f"Total zones: {len(zones)}")
    for z in zones:
        print(f"ID: {z.id_zone}, Name: {z.nom_zone}")
finally:
    db.close()
