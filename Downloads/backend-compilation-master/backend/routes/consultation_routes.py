from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from models.consultation import Consultation
from schemas.schemas import ConsultationCreate, ConsultationUpdate, ConsultationOut

router = APIRouter(prefix="/consultations", tags=["Consultations"])


# ── CREATE ────────────────────────────────────────────────────────────────────
@router.post("/", response_model=ConsultationOut, status_code=status.HTTP_201_CREATED,
             summary="Créer une consultation")
def create_consultation(payload: ConsultationCreate, db: Session = Depends(get_db)):
    consultation = Consultation(**payload.model_dump())
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


# ── READ ALL ──────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[ConsultationOut], summary="Lister toutes les consultations")
def get_consultations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    statut: Optional[str] = Query(None, description="ouverte | clôturée | en_analyse"),
    type_consultation: Optional[str] = Query(None, description="mobilité | environnement | énergie…"),
    id_zone: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Consultation)
    if statut:
        q = q.filter(Consultation.statut == statut)
    if type_consultation:
        q = q.filter(Consultation.type_consultation == type_consultation)
    if id_zone:
        q = q.filter(Consultation.id_zone == id_zone)
    return q.offset(skip).limit(limit).all()


# ── READ ONE ──────────────────────────────────────────────────────────────────
@router.get("/{id_consultation}", response_model=ConsultationOut,
            summary="Obtenir une consultation par ID")
def get_consultation(id_consultation: int, db: Session = Depends(get_db)):
    consultation = db.query(Consultation).filter(
        Consultation.id_consultation == id_consultation
    ).first()
    if not consultation:
        raise HTTPException(status_code=404, detail=f"Consultation {id_consultation} introuvable")
    return consultation


# ── READ OUVERTES ─────────────────────────────────────────────────────────────
@router.get("/ouvertes/liste", response_model=List[ConsultationOut],
            summary="Lister les consultations ouvertes")
def get_ouvertes(db: Session = Depends(get_db)):
    return db.query(Consultation).filter(Consultation.statut == "ouverte").all()


# ── UPDATE ────────────────────────────────────────────────────────────────────
@router.put("/{id_consultation}", response_model=ConsultationOut,
            summary="Mettre à jour une consultation")
def update_consultation(id_consultation: int, payload: ConsultationUpdate,
                        db: Session = Depends(get_db)):
    consultation = db.query(Consultation).filter(
        Consultation.id_consultation == id_consultation
    ).first()
    if not consultation:
        raise HTTPException(status_code=404, detail=f"Consultation {id_consultation} introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(consultation, field, value)
    db.commit()
    db.refresh(consultation)
    return consultation


# ── PATCH STATUT ──────────────────────────────────────────────────────────────
@router.patch("/{id_consultation}/statut", response_model=ConsultationOut,
              summary="Changer le statut d'une consultation")
def patch_statut(
    id_consultation: int,
    statut: str = Query(..., description="ouverte | clôturée | en_analyse"),
    db: Session = Depends(get_db),
):
    consultation = db.query(Consultation).filter(
        Consultation.id_consultation == id_consultation
    ).first()
    if not consultation:
        raise HTTPException(status_code=404, detail=f"Consultation {id_consultation} introuvable")
    consultation.statut = statut
    db.commit()
    db.refresh(consultation)
    return consultation


# ── DELETE ────────────────────────────────────────────────────────────────────
@router.delete("/{id_consultation}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer une consultation")
def delete_consultation(id_consultation: int, db: Session = Depends(get_db)):
    consultation = db.query(Consultation).filter(
        Consultation.id_consultation == id_consultation
    ).first()
    if not consultation:
        raise HTTPException(status_code=404, detail=f"Consultation {id_consultation} introuvable")
    db.delete(consultation)
    db.commit()
