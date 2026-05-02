from models.capteur import Capteur
from models.citoyen import Citoyen
from models.intervention import Intervention
from models.mesure import Mesure
from models.technicien import Technicien
from models.trajet import Trajet
from models.vehicule import Vehicule
from models.zone import Zone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.db import get_db
from sqlalchemy import func

router = APIRouter(prefix="/kpis", tags=["kpis"])

@router.get("/dashboard", tags=["Général"], summary="Tableau de bord global")
def dashboard(db: Session = Depends(get_db)):
    total_capteurs  = db.query(func.count(Capteur.id_capteur)).scalar()
    actifs          = db.query(func.count(Capteur.id_capteur)).filter(Capteur.statut == "actif").scalar()
    maintenance     = db.query(func.count(Capteur.id_capteur)).filter(Capteur.statut == "maintenance").scalar()
    hors_service    = db.query(func.count(Capteur.id_capteur)).filter(Capteur.statut == "hors_service").scalar()

    total_mesures   = db.query(func.count(Mesure.id_mesure)).scalar()
    derniere_mesure = db.query(func.max(Mesure.timestamp)).scalar()
    avg_pollution   = db.query(func.avg(Mesure.pollution)).scalar()
    avg_temperature = db.query(func.avg(Mesure.temperature)).scalar()
    avg_humidite    = db.query(func.avg(Mesure.humidite)).scalar()

    interv_en_cours  = db.query(func.count(Intervention.id_intervention)).scalar()
    interv_critiques = db.query(func.count(Intervention.id_intervention)).scalar()

    vehicules_actifs = db.query(func.count(Vehicule.id_vehicule)).filter(Vehicule.statut == "actif").scalar()
    total_vehicules  = db.query(func.count(Vehicule.id_vehicule)).scalar()
    total_co2        = db.query(func.sum(Trajet.economie_co2)).scalar() or 0.0
    techs_dispo      = db.query(Technicien).filter(Technicien.disponible == True).count()

    return {
        "smart_city": "Tunisia 🇹🇳",
        "zones": db.query(func.count(Zone.id_zone)).scalar(),
        "capteurs": {
            "total": total_capteurs,
            "actifs": actifs,
            "en_maintenance": maintenance,
            "hors_service": hors_service,
        },
        "mesures": {
            "total": total_mesures,
            "derniere_mesure": derniere_mesure,
            "moyennes": {
                "pollution_µg_m3": round(avg_pollution or 0, 2),
                "temperature_C":   round(avg_temperature or 0, 2),
                "humidite_pct":    round(avg_humidite or 0, 2),
            },
        },
        "interventions": {
            "en_cours": interv_en_cours,
            "critiques": interv_critiques,
        },
        "vehicules": {
            "total": total_vehicules,
            "actifs": vehicules_actifs,
        },
        "environnement": {
            "co2_economise_kg_total": round(total_co2, 3),
        },
        "techniciens_disponibles": techs_dispo,
        "citoyens": db.query(func.count(Citoyen.id_citoyen)).scalar(),
    }