from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database.db import get_db
from models.mesure import Mesure
from schemas.schemas import MesureCreate, MesureUpdate, MesureOut

router = APIRouter(prefix="/mesures", tags=["Mesures"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=MesureOut, status_code=status.HTTP_201_CREATED,
             summary="Enregistrer une mesure")
def create_mesure(payload: MesureCreate, db: Session = Depends(get_db)):
    mesure = Mesure(**payload.model_dump())
    db.add(mesure)
    db.commit()
    db.refresh(mesure)
    return mesure


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[MesureOut], summary="Lister les mesures")
def get_mesures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    id_zone: Optional[int] = Query(None, description="Filtrer par zone"),
    depuis: Optional[datetime] = Query(None, description="Mesures depuis cette date"),
    jusqu: Optional[datetime] = Query(None, description="Mesures jusqu'à cette date"),
    db: Session = Depends(get_db),
):
    q = db.query(Mesure)

    if id_zone is not None:
        q = q.filter(Mesure.id_zone == id_zone)

    if depuis:
        q = q.filter(Mesure.timestamp >= depuis)

    if jusqu:
        q = q.filter(Mesure.timestamp <= jusqu)

    return q.order_by(desc(Mesure.timestamp)).offset(skip).limit(limit).all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_mesure}", response_model=MesureOut,
            summary="Obtenir une mesure par ID")
def get_mesure(id_mesure: int, db: Session = Depends(get_db)):
    mesure = db.query(Mesure).filter(Mesure.id_mesure == id_mesure).first()
    if not mesure:
        raise HTTPException(status_code=404, detail=f"Mesure {id_mesure} introuvable")
    return mesure


# ── DERNIÈRES MESURES PAR ZONE ────────────────────────────────────────────────
@router.get("/zone/{id_zone}/dernieres", response_model=List[MesureOut],
            summary="Dernières N mesures d'une zone")
def get_dernieres_mesures(
    id_zone: int,
    n: int = Query(60, ge=1, le=1440,
                   description="Nombre de mesures à retourner"),
    db: Session = Depends(get_db),
):
    return (
        db.query(Mesure)
        .filter(Mesure.id_zone == id_zone)
        .order_by(desc(Mesure.timestamp))
        .limit(n)
        .all()
    )


# ── DERNIÈRE MESURE (LIVE) ────────────────────────────────────────────────────
@router.get("/zone/{id_zone}/live", response_model=MesureOut,
            summary="Dernière mesure en temps réel d'une zone")
def get_live(id_zone: int, db: Session = Depends(get_db)):
    mesure = (
        db.query(Mesure)
        .filter(Mesure.id_zone == id_zone)
        .order_by(desc(Mesure.timestamp))
        .first()
    )

    if not mesure:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune mesure pour la zone {id_zone}"
        )

    return mesure


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_mesure}", response_model=MesureOut,
            summary="Mettre à jour une mesure")
def update_mesure(id_mesure: int, payload: MesureUpdate,
                  db: Session = Depends(get_db)):
    mesure = db.query(Mesure).filter(Mesure.id_mesure == id_mesure).first()

    if not mesure:
        raise HTTPException(status_code=404,
                            detail=f"Mesure {id_mesure} introuvable")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(mesure, field, value)

    db.commit()
    db.refresh(mesure)
    return mesure


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_mesure}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer une mesure")
def delete_mesure(id_mesure: int, db: Session = Depends(get_db)):
    mesure = db.query(Mesure).filter(Mesure.id_mesure == id_mesure).first()

    if not mesure:
        raise HTTPException(status_code=404,
                            detail=f"Mesure {id_mesure} introuvable")

    db.delete(mesure)
    db.commit()


# ── DELETE ALL PAR ZONE ───────────────────────────────────────────────────────
@router.delete("/zone/{id_zone}/all",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer toutes les mesures d'une zone")
def delete_mesures_zone(id_zone: int, db: Session = Depends(get_db)):
    db.query(Mesure).filter(Mesure.id_zone == id_zone).delete()
    db.commit()