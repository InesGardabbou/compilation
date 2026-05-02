from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.capteur import Capteur
from schemas.schemas import CapteurCreate, CapteurUpdate, CapteurOut

router = APIRouter(prefix="/capteurs", tags=["Capteurs"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=CapteurOut, status_code=status.HTTP_201_CREATED,
             summary="Créer un capteur")
def create_capteur(payload: CapteurCreate, db: Session = Depends(get_db)):
    capteur = Capteur(**payload.model_dump())
    db.add(capteur)
    db.commit()
    db.refresh(capteur)
    return capteur


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[CapteurOut], summary="Lister tous les capteurs")
def get_capteurs(
    db: Session = Depends(get_db),
):
    q = db.query(Capteur)
    return q.all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_capteur}", response_model=CapteurOut, summary="Obtenir un capteur par ID")
def get_capteur(id_capteur: int, db: Session = Depends(get_db)):
    capteur = db.query(Capteur).filter(Capteur.id_capteur == id_capteur).first()
    if not capteur:
        raise HTTPException(status_code=404, detail=f"Capteur {id_capteur} introuvable")
    return capteur


# ── READ BY ZONE ──────────────────────────────────────────────────────────────
@router.get("/zone/{id_zone}", response_model=List[CapteurOut],
            summary="Lister les capteurs d'une zone")
def get_capteurs_by_zone(id_zone: int, db: Session = Depends(get_db)):
    return db.query(Capteur).filter(Capteur.id_zone == id_zone).all()


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_capteur}", response_model=CapteurOut, summary="Mettre à jour un capteur")
def update_capteur(id_capteur: int, payload: CapteurUpdate, db: Session = Depends(get_db)):
    capteur = db.query(Capteur).filter(Capteur.id_capteur == id_capteur).first()
    if not capteur:
        raise HTTPException(status_code=404, detail=f"Capteur {id_capteur} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(capteur, field, value)
    db.commit()
    db.refresh(capteur)
    return capteur


# ── PATCH STATUT ──────────────────────────────────────────────────────────────
@router.patch("/{id_capteur}/statut", response_model=CapteurOut,
              summary="Changer le statut d'un capteur")
def patch_statut(
    id_capteur: int,
    statut: str = Query(..., description="Nouveau statut : actif | maintenance | hors_service"),
    db: Session = Depends(get_db),
):
    capteur = db.query(Capteur).filter(Capteur.id_capteur == id_capteur).first()
    if not capteur:
        raise HTTPException(status_code=404, detail=f"Capteur {id_capteur} introuvable")
    capteur.statut = statut
    db.commit()
    db.refresh(capteur)
    return capteur


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_capteur}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un capteur")
def delete_capteur(id_capteur: int, db: Session = Depends(get_db)):
    capteur = db.query(Capteur).filter(Capteur.id_capteur == id_capteur).first()
    if not capteur:
        raise HTTPException(status_code=404, detail=f"Capteur {id_capteur} introuvable")
    db.delete(capteur)
    db.commit()
