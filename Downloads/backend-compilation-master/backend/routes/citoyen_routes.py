from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.citoyen import Citoyen
from schemas.schemas import CitoyenCreate, CitoyenUpdate, CitoyenOut

router = APIRouter(prefix="/citoyens", tags=["Citoyens"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=CitoyenOut, status_code=status.HTTP_201_CREATED,
             summary="Créer un citoyen")
def create_citoyen(payload: CitoyenCreate, db: Session = Depends(get_db)):
    citoyen = Citoyen(**payload.model_dump())
    db.add(citoyen)
    db.commit()
    db.refresh(citoyen)
    return citoyen


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[CitoyenOut], summary="Lister tous les citoyens")
def get_citoyens(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_zone: Optional[int] = Query(None, description="Filtrer par zone"),
    preference_mobilite: Optional[str] = Query(None, description="Filtrer par mode de mobilité"),
    score_min: Optional[int] = Query(None, ge=0, le=100, description="Score écolo minimum"),
    db: Session = Depends(get_db),
):
    q = db.query(Citoyen)
    if id_zone:
        q = q.filter(Citoyen.id_zone == id_zone)
    if preference_mobilite:
        q = q.filter(Citoyen.preference_mobilite == preference_mobilite)
    if score_min is not None:
        q = q.filter(Citoyen.score_ecolo >= score_min)
    return q.offset(skip).limit(limit).all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_citoyen}", response_model=CitoyenOut, summary="Obtenir un citoyen par ID")
def get_citoyen(id_citoyen: int, db: Session = Depends(get_db)):
    citoyen = db.query(Citoyen).filter(Citoyen.id_citoyen == id_citoyen).first()
    if not citoyen:
        raise HTTPException(status_code=404, detail=f"Citoyen {id_citoyen} introuvable")
    return citoyen


# ── CLASSEMENT SCORE ECOLO ────────────────────────────────────────────────────
@router.get("/classement/ecolo", response_model=List[CitoyenOut],
            summary="Top citoyens par score écologique")
def classement_ecolo(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return (
        db.query(Citoyen)
        .order_by(Citoyen.score_ecolo.desc())
        .limit(limit)
        .all()
    )


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_citoyen}", response_model=CitoyenOut, summary="Mettre à jour un citoyen")
def update_citoyen(id_citoyen: int, payload: CitoyenUpdate, db: Session = Depends(get_db)):
    citoyen = db.query(Citoyen).filter(Citoyen.id_citoyen == id_citoyen).first()
    if not citoyen:
        raise HTTPException(status_code=404, detail=f"Citoyen {id_citoyen} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(citoyen, field, value)
    db.commit()
    db.refresh(citoyen)
    return citoyen


# ── PATCH SCORE ECOLO ─────────────────────────────────────────────────────────
@router.patch("/{id_citoyen}/score", response_model=CitoyenOut,
              summary="Modifier le score écologique d'un citoyen")
def patch_score(
    id_citoyen: int,
    score: int = Query(..., ge=0, le=100, description="Nouveau score (0-100)"),
    db: Session = Depends(get_db),
):
    citoyen = db.query(Citoyen).filter(Citoyen.id_citoyen == id_citoyen).first()
    if not citoyen:
        raise HTTPException(status_code=404, detail=f"Citoyen {id_citoyen} introuvable")
    citoyen.score_ecolo = score
    db.commit()
    db.refresh(citoyen)
    return citoyen


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_citoyen}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un citoyen")
def delete_citoyen(id_citoyen: int, db: Session = Depends(get_db)):
    citoyen = db.query(Citoyen).filter(Citoyen.id_citoyen == id_citoyen).first()
    if not citoyen:
        raise HTTPException(status_code=404, detail=f"Citoyen {id_citoyen} introuvable")
    db.delete(citoyen)
    db.commit()
