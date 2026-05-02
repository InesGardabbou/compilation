from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.vehicule import Vehicule
from schemas.schemas import VehiculeCreate, VehiculeUpdate, VehiculeOut

router = APIRouter(prefix="/vehicules", tags=["Véhicules"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=VehiculeOut, status_code=status.HTTP_201_CREATED,
             summary="Créer un véhicule")
def create_vehicule(payload: VehiculeCreate, db: Session = Depends(get_db)):
    vehicule = Vehicule(**payload.model_dump())
    db.add(vehicule)
    db.commit()
    db.refresh(vehicule)
    return vehicule


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[VehiculeOut], summary="Lister tous les véhicules")
def get_vehicules(
    db: Session = Depends(get_db),
):
    q = db.query(Vehicule)
    return q.all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_vehicule}", response_model=VehiculeOut, summary="Obtenir un véhicule par ID")
def get_vehicule(id_vehicule: int, db: Session = Depends(get_db)):
    vehicule = db.query(Vehicule).filter(Vehicule.id_vehicule == id_vehicule).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail=f"Véhicule {id_vehicule} introuvable")
    return vehicule


# ── READ ACTIFS ───────────────────────────────────────────────────────────────
@router.get("/actifs/liste", response_model=List[VehiculeOut],
            summary="Lister les véhicules actifs en ce moment")
def get_actifs(db: Session = Depends(get_db)):
    return db.query(Vehicule).filter(Vehicule.statut == "actif").all()


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_vehicule}", response_model=VehiculeOut, summary="Mettre à jour un véhicule")
def update_vehicule(id_vehicule: int, payload: VehiculeUpdate, db: Session = Depends(get_db)):
    vehicule = db.query(Vehicule).filter(Vehicule.id_vehicule == id_vehicule).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail=f"Véhicule {id_vehicule} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicule, field, value)
    db.commit()
    db.refresh(vehicule)
    return vehicule


# ── PATCH BATTERIE ────────────────────────────────────────────────────────────
@router.patch("/{id_vehicule}/batterie", response_model=VehiculeOut,
              summary="Mettre à jour le niveau de batterie")
def patch_batterie(
    id_vehicule: int,
    batterie_pct: float = Query(..., ge=0.0, le=100.0, description="Niveau batterie en %"),
    db: Session = Depends(get_db),
):
    vehicule = db.query(Vehicule).filter(Vehicule.id_vehicule == id_vehicule).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail=f"Véhicule {id_vehicule} introuvable")
    vehicule.batterie_pct = batterie_pct
    db.commit()
    db.refresh(vehicule)
    return vehicule


# ── PATCH STATUT ──────────────────────────────────────────────────────────────
@router.patch("/{id_vehicule}/statut", response_model=VehiculeOut,
              summary="Changer le statut d'un véhicule")
def patch_statut(
    id_vehicule: int,
    statut: str = Query(..., description="actif | en_charge | maintenance"),
    db: Session = Depends(get_db),
):
    vehicule = db.query(Vehicule).filter(Vehicule.id_vehicule == id_vehicule).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail=f"Véhicule {id_vehicule} introuvable")
    vehicule.statut = statut
    db.commit()
    db.refresh(vehicule)
    return vehicule


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_vehicule}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un véhicule")
def delete_vehicule(id_vehicule: int, db: Session = Depends(get_db)):
    vehicule = db.query(Vehicule).filter(Vehicule.id_vehicule == id_vehicule).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail=f"Véhicule {id_vehicule} introuvable")
    db.delete(vehicule)
    db.commit()
