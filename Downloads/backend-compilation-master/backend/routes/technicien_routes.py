from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.technicien import Technicien
from schemas.schemas import TechnicienCreate, TechnicienUpdate, TechnicienOut

router = APIRouter(prefix="/techniciens", tags=["Techniciens"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=TechnicienOut, status_code=status.HTTP_201_CREATED,
             summary="Créer un technicien")
def create_technicien(payload: TechnicienCreate, db: Session = Depends(get_db)):
    tech = Technicien(**payload.model_dump())
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[TechnicienOut], summary="Lister tous les techniciens")
def get_techniciens(
    db: Session = Depends(get_db),
):
    q = db.query(Technicien)
    return q.all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_technicien}", response_model=TechnicienOut,
            summary="Obtenir un technicien par ID")
def get_technicien(id_technicien: int, db: Session = Depends(get_db)):
    tech = db.query(Technicien).filter(Technicien.id_technicien == id_technicien).first()
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technicien {id_technicien} introuvable")
    return tech


# ── READ DISPONIBLES ──────────────────────────────────────────────────────────
@router.get("/disponibles/liste", response_model=List[TechnicienOut],
            summary="Lister les techniciens disponibles")
def get_disponibles(db: Session = Depends(get_db)):
    return db.query(Technicien).filter(Technicien.disponible == True).all()


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_technicien}", response_model=TechnicienOut,
            summary="Mettre à jour un technicien")
def update_technicien(id_technicien: int, payload: TechnicienUpdate,
                      db: Session = Depends(get_db)):
    tech = db.query(Technicien).filter(Technicien.id_technicien == id_technicien).first()
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technicien {id_technicien} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tech, field, value)
    db.commit()
    db.refresh(tech)
    return tech


# ── PATCH DISPONIBILITÉ ───────────────────────────────────────────────────────
@router.patch("/{id_technicien}/disponibilite", response_model=TechnicienOut,
              summary="Changer la disponibilité d'un technicien")
def patch_disponibilite(
    id_technicien: int,
    disponible: bool = Query(..., description="true = disponible, false = occupé"),
    db: Session = Depends(get_db),
):
    tech = db.query(Technicien).filter(Technicien.id_technicien == id_technicien).first()
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technicien {id_technicien} introuvable")
    tech.disponible = disponible
    db.commit()
    db.refresh(tech)
    return tech


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_technicien}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un technicien")
def delete_technicien(id_technicien: int, db: Session = Depends(get_db)):
    tech = db.query(Technicien).filter(Technicien.id_technicien == id_technicien).first()
    if not tech:
        raise HTTPException(status_code=404, detail=f"Technicien {id_technicien} introuvable")
    db.delete(tech)
    db.commit()
