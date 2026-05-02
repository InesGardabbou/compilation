from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.intervention import Intervention
from schemas.schemas import InterventionCreate, InterventionUpdate, InterventionOut

router = APIRouter(prefix="/interventions", tags=["Interventions"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=InterventionOut, status_code=status.HTTP_201_CREATED,
             summary="Créer une intervention")
def create_intervention(payload: InterventionCreate, db: Session = Depends(get_db)):
    intervention = Intervention(**payload.model_dump())
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[InterventionOut], summary="Lister les 5 dernières interventions")
def get_interventions(db: Session = Depends(get_db)):
    q = (
        db.query(Intervention)
        .order_by(Intervention.date_demande.desc())  # ⚡ tri du plus récent au plus ancien
        .limit(5)
    )
    
    return q.all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/all", response_model=List[InterventionOut], summary="Lister les 5 dernières interventions")
def get_all_interventions(db: Session = Depends(get_db)):
    q = (
        db.query(Intervention)
        .order_by(Intervention.date_demande.desc())  # ⚡ tri du plus récent au plus ancien
    )
    
    return q.all()


# ── READ PAR ZONE ─────────────────────────────────────────────────────────────
@router.get("/zone/{id_zone}", response_model=List[InterventionOut],
            summary="Interventions d'une zone")
def get_interventions_zone(id_zone: int, db: Session = Depends(get_db)):
    return db.query(Intervention).filter(Intervention.id_zone == id_zone).all()


# ── READ CRITIQUES ────────────────────────────────────────────────────────────
@router.get("/priorite/critiques", response_model=List[InterventionOut],
            summary="Interventions critiques en cours")
def get_critiques(db: Session = Depends(get_db)):
    return (
        db.query(Intervention)
        .filter(Intervention.priorite == "critique", Intervention.statut == "en_cours")
        .all()
    )


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_intervention}", response_model=InterventionOut,
            summary="Mettre à jour une intervention")
def update_intervention(id_intervention: int, payload: InterventionUpdate,
                        db: Session = Depends(get_db)):
    intervention = db.query(Intervention).filter(
        Intervention.id_intervention == id_intervention
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention {id_intervention} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(intervention, field, value)
    db.commit()
    db.refresh(intervention)
    return intervention


# ── PATCH STATUT ──────────────────────────────────────────────────────────────
@router.patch("/{id_intervention}/statut", response_model=InterventionOut,
              summary="Changer le statut d'une intervention")
def patch_statut(
    id_intervention: int,
    statut: str = Query(..., description="planifiée | en_cours | terminée | annulée"),
    db: Session = Depends(get_db),
):
    intervention = db.query(Intervention).filter(
        Intervention.id_intervention == id_intervention
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention {id_intervention} introuvable")
    intervention.statut = statut
    db.commit()
    db.refresh(intervention)
    return intervention


# ── PATCH VALIDATION IA ───────────────────────────────────────────────────────
@router.patch("/{id_intervention}/ia-validation", response_model=InterventionOut,
              summary="Valider ou rejeter une intervention par IA")
def patch_ia(
    id_intervention: int,
    ia_validee: bool = Query(..., description="true = validée, false = rejetée"),
    db: Session = Depends(get_db),
):
    intervention = db.query(Intervention).filter(
        Intervention.id_intervention == id_intervention
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention {id_intervention} introuvable")
    intervention.ia_validee = ia_validee
    db.commit()
    db.refresh(intervention)
    return intervention


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_intervention}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer une intervention")
def delete_intervention(id_intervention: int, db: Session = Depends(get_db)):
    intervention = db.query(Intervention).filter(
        Intervention.id_intervention == id_intervention
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail=f"Intervention {id_intervention} introuvable")
    db.delete(intervention)
    db.commit()
