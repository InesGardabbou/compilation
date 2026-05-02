from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

from database.db import get_db
from models.trajet import Trajet
from schemas.schemas import TrajetCreate, TrajetUpdate, TrajetOut

router = APIRouter(prefix="/trajets", tags=["Trajets"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=TrajetOut, status_code=status.HTTP_201_CREATED,
             summary="Créer un trajet")
def create_trajet(payload: TrajetCreate, db: Session = Depends(get_db)):
    trajet = Trajet(**payload.model_dump())
    db.add(trajet)
    db.commit()
    db.refresh(trajet)
    return trajet


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[TrajetOut], summary="Lister tous les trajets")
def get_trajets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_vehicule: Optional[int] = Query(None, description="Filtrer par véhicule"),
    statut: Optional[str] = Query(None, description="terminé | en_cours | planifié"),
    origine: Optional[str] = Query(None, description="Filtrer par ville d'origine"),
    destination: Optional[str] = Query(None, description="Filtrer par destination"),
    db: Session = Depends(get_db),
):
    q = db.query(Trajet)
    if id_vehicule:
        q = q.filter(Trajet.id_vehicule == id_vehicule)
    if statut:
        q = q.filter(Trajet.statut == statut)
    if origine:
        q = q.filter(Trajet.origine.ilike(f"%{origine}%"))
    if destination:
        q = q.filter(Trajet.destination.ilike(f"%{destination}%"))
    return q.order_by(desc(Trajet.date_debut)).offset(skip).limit(limit).all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_trajet}", response_model=TrajetOut, summary="Obtenir un trajet par ID")
def get_trajet(id_trajet: int, db: Session = Depends(get_db)):
    trajet = db.query(Trajet).filter(Trajet.id_trajet == id_trajet).first()
    if not trajet:
        raise HTTPException(status_code=404, detail=f"Trajet {id_trajet} introuvable")
    return trajet


# ── TRAJETS D'UN VÉHICULE ─────────────────────────────────────────────────────
@router.get("/vehicule/{id_vehicule}", response_model=List[TrajetOut],
            summary="Historique des trajets d'un véhicule")
def get_trajets_vehicule(id_vehicule: int, db: Session = Depends(get_db)):
    return (
        db.query(Trajet)
        .filter(Trajet.id_vehicule == id_vehicule)
        .order_by(desc(Trajet.date_debut))
        .all()
    )


# ── STATS CO2 ─────────────────────────────────────────────────────────────────
@router.get("/stats/co2", summary="Total CO₂ économisé par tous les trajets")
def stats_co2(db: Session = Depends(get_db)):
    total = db.query(func.sum(Trajet.economie_co2)).scalar() or 0.0
    count = db.query(func.count(Trajet.id_trajet)).scalar() or 0
    return {
        "total_co2_economise_kg": round(total, 3),
        "nombre_trajets": count,
        "moyenne_co2_par_trajet_kg": round(total / count, 3) if count > 0 else 0.0,
    }


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_trajet}", response_model=TrajetOut, summary="Mettre à jour un trajet")
def update_trajet(id_trajet: int, payload: TrajetUpdate, db: Session = Depends(get_db)):
    trajet = db.query(Trajet).filter(Trajet.id_trajet == id_trajet).first()
    if not trajet:
        raise HTTPException(status_code=404, detail=f"Trajet {id_trajet} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trajet, field, value)
    db.commit()
    db.refresh(trajet)
    return trajet


# ── PATCH STATUT ──────────────────────────────────────────────────────────────
@router.patch("/{id_trajet}/statut", response_model=TrajetOut,
              summary="Changer le statut d'un trajet")
def patch_statut(
    id_trajet: int,
    statut: str = Query(..., description="planifié | en_cours | terminé"),
    db: Session = Depends(get_db),
):
    trajet = db.query(Trajet).filter(Trajet.id_trajet == id_trajet).first()
    if not trajet:
        raise HTTPException(status_code=404, detail=f"Trajet {id_trajet} introuvable")
    trajet.statut = statut
    db.commit()
    db.refresh(trajet)
    return trajet


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_trajet}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un trajet")
def delete_trajet(id_trajet: int, db: Session = Depends(get_db)):
    trajet = db.query(Trajet).filter(Trajet.id_trajet == id_trajet).first()
    if not trajet:
        raise HTTPException(status_code=404, detail=f"Trajet {id_trajet} introuvable")
    db.delete(trajet)
    db.commit()
