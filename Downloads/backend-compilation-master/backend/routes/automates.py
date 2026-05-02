from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db import get_db
from services.automates import (
    AutomateCapteur,
    AutomateIntervention,
    AutomateVehicule,
    SurveillantCapteurs
)

# 🔥 IMPORT MODELS (IMPORTANT)
from models.capteur import Capteur
from models.historique import CapteursHistoriqueEtats

router = APIRouter(prefix="/automates", tags=["Automates"])


class ActionRequest(BaseModel):
    id: int
    event: str


@router.post("/capteur/action")
def capteur_action(req: ActionRequest):
    try:
        auto = AutomateCapteur(f"C-{req.id}")
        ok = auto.appliquer_en_db(req.id, req.event)

        return {"success": ok}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/capteur/{id}")
def get_capteur(id: int, db: Session = Depends(get_db)):
    try:
        capteur = db.query(Capteur).filter(Capteur.id_capteur == id).first()

        if not capteur:
            return {"success": False, "error": "Not found"}

        return {
            "id": capteur.id_capteur,
            "nom": capteur.nom,
            "statut": capteur.statut
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 🔥 AUTOMATE DYNAMIQUE (SANS STATIQUE)
# ============================================================

@router.get("/capteur/{id}/automate")
def automate_graph(id: int, db: Session = Depends(get_db)):
    try:
        # état actuel
        capteur = db.query(Capteur).filter(Capteur.id_capteur == id).first()
        etat_actuel = capteur.statut if capteur else None

        # 🔥 historique réel
        rows = db.query(CapteursHistoriqueEtats)\
            .filter(CapteursHistoriqueEtats.capteur_id == id)\
            .order_by(CapteursHistoriqueEtats.date_transition.asc())\
            .all()

        historique = [
            {
                "ancien_etat": h.ancien_etat,
                "nouvel_etat": h.nouvel_etat,
                "evenement": h.evenement,
                "date_transition": h.date_transition
            }
            for h in rows
        ]

        return {
            "etat_actuel": etat_actuel,
            "historique": historique
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 🔹 HISTORIQUE SEUL
# ============================================================

@router.get("/capteur/{id}/historique")
def historique_capteur(id: int, db: Session = Depends(get_db)):
    try:
        rows = db.query(CapteursHistoriqueEtats)\
            .filter(CapteursHistoriqueEtats.capteur_id == id)\
            .order_by(CapteursHistoriqueEtats.date_transition.desc())\
            .all()

        data = [
            {
                "ancien_etat": h.ancien_etat,
                "nouvel_etat": h.nouvel_etat,
                "evenement": h.evenement,
                "date_transition": h.date_transition
            }
            for h in rows
        ]

        return {"count": len(data), "historique": data}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 🔹 INTERVENTION
# ============================================================

@router.post("/intervention/action")
def intervention_action(req: ActionRequest):
    try:
        auto = AutomateIntervention(f"INT-{req.id}")
        ok = auto.appliquer_en_db(req.id, req.event)

        return {"success": ok}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 🔹 VEHICULE
# ============================================================

@router.post("/vehicule/action")
def vehicule_action(req: ActionRequest):
    try:
        auto = AutomateVehicule(f"V-{req.id}")
        ok = auto.appliquer_en_db(req.id, req.event)

        return {"success": ok}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# 🔹 ALERTES
# ============================================================

@router.get("/alertes")
def alertes():
    try:
        s = SurveillantCapteurs()
        alertes = s.verifier()

        return {
            "count": len(alertes),
            "alertes": alertes
        }

    except Exception as e:
        return {"success": False, "error": str(e)}