from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.proprietaire import Proprietaire
from schemas.schemas import ProprietaireCreate, ProprietaireUpdate, ProprietaireOut

router = APIRouter(prefix="/proprietaires", tags=["Propriétaires"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=ProprietaireOut, status_code=status.HTTP_201_CREATED,
             summary="Créer un propriétaire")
def create_proprietaire(payload: ProprietaireCreate, db: Session = Depends(get_db)):
    prop = Proprietaire(**payload.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[ProprietaireOut], summary="Lister tous les propriétaires")
def get_proprietaires(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    type: Optional[str] = Query(None, description="Filtrer par type (public, société, privé)"),
    db: Session = Depends(get_db),
):
    q = db.query(Proprietaire)
    if type:
        q = q.filter(Proprietaire.type == type)
    return q.offset(skip).limit(limit).all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_proprietaire}", response_model=ProprietaireOut,
            summary="Obtenir un propriétaire par ID")
def get_proprietaire(id_proprietaire: int, db: Session = Depends(get_db)):
    prop = db.query(Proprietaire).filter(
        Proprietaire.id_proprietaire == id_proprietaire
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail=f"Propriétaire {id_proprietaire} introuvable")
    return prop


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_proprietaire}", response_model=ProprietaireOut,
            summary="Mettre à jour un propriétaire")
def update_proprietaire(id_proprietaire: int, payload: ProprietaireUpdate,
                        db: Session = Depends(get_db)):
    prop = db.query(Proprietaire).filter(
        Proprietaire.id_proprietaire == id_proprietaire
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail=f"Propriétaire {id_proprietaire} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return prop


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_proprietaire}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un propriétaire")
def delete_proprietaire(id_proprietaire: int, db: Session = Depends(get_db)):
    prop = db.query(Proprietaire).filter(
        Proprietaire.id_proprietaire == id_proprietaire
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail=f"Propriétaire {id_proprietaire} introuvable")
    db.delete(prop)
    db.commit()
