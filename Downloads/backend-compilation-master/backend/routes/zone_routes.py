from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.zone import Zone
from schemas.schemas import ZoneCreate, ZoneUpdate, ZoneOut
from models.capteur import Capteur
from models.mesure import Mesure
from sqlalchemy import func

router = APIRouter(prefix="/zones", tags=["Zones"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=ZoneOut, status_code=status.HTTP_201_CREATED,
             summary="Créer une zone")
def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    zone = Zone(**payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[ZoneOut], summary="Lister toutes les zones")
def get_zones( db: Session = Depends(get_db),):
    q = db.query(Zone)
    return q


# ── STATUS ────────────────────────────────────────────────────────────────────
@router.get("/status", summary="Obtenir les statistiques des zones pour le dashboard")
def get_zones_status(db: Session = Depends(get_db)):
    zones = db.query(Zone).all()
    results = []
    
    for z in zones:
        # Get sensor count for this zone
        sensors_count = db.query(func.count(Capteur.id_capteur)).filter(Capteur.id_zone == z.id_zone).scalar() or 0
        
        # Get average pollution (AQI)
        avg_aqi = db.query(func.avg(Mesure.pollution)).filter(Mesure.id_zone == z.id_zone).scalar() or 0
        aqi_val = round(avg_aqi)
        
        # Determine status
        if aqi_val > 80:
            status = 'critical'
        elif aqi_val > 50:
            status = 'moderate'
        elif aqi_val > 30:
            status = 'good'
        else:
            status = 'excellent'
            
        results.append({
            "id": z.id_zone,
            "name": z.nom_zone,
            "aqi": aqi_val,
            "status": status,
            "sensors": sensors_count,
            "trend": "-2%" if aqi_val < 50 else "+5%",  # Mock trend for now
            "pos": [z.latitude, z.longitude] if z.latitude and z.longitude else [35.8256, 10.6369]
        })
        
    return results


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_zone}", response_model=ZoneOut, summary="Obtenir une zone par ID")
def get_zone(id_zone: int, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id_zone == id_zone).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {id_zone} introuvable")
    return zone


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_zone}", response_model=ZoneOut, summary="Mettre à jour une zone")
def update_zone(id_zone: int, payload: ZoneUpdate, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id_zone == id_zone).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {id_zone} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, field, value)
    db.commit()
    db.refresh(zone)
    return zone


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_zone}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer une zone")
def delete_zone(id_zone: int, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id_zone == id_zone).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {id_zone} introuvable")
    db.delete(zone)
    db.commit()
