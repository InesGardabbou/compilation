from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ══════════════════════════════════════════════
#  ZONE
# ══════════════════════════════════════════════

class ZoneCreate(BaseModel):
    nom_zone: str
    surface_km2: Optional[float] = None
    population: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    type_zone: Optional[str] = None

class ZoneUpdate(BaseModel):
    nom_zone: Optional[str] = None
    surface_km2: Optional[float] = None
    population: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    type_zone: Optional[str] = None

class ZoneOut(ZoneCreate):
    id_zone: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  CAPTEUR
# ══════════════════════════════════════════════

class CapteurCreate(BaseModel):
    nom: Optional[str] = None
    type_capteur: Optional[str] = None
    statut: Optional[str] = None
    taux_erreur: Optional[float] = None
    date_installation: Optional[datetime] = None
    fabricant: Optional[str] = None
    localisation_gps: Optional[str] = None
    description: Optional[str] = None
    unite: Optional[str] = None
    id_zone: Optional[int] = None

class CapteurUpdate(BaseModel):
    nom: Optional[str] = None
    type_capteur: Optional[str] = None
    statut: Optional[str] = None
    taux_erreur: Optional[float] = None
    date_installation: Optional[datetime] = None
    fabricant: Optional[str] = None
    localisation_gps: Optional[str] = None
    description: Optional[str] = None
    unite: Optional[str] = None
    id_zone: Optional[int] = None

class CapteurOut(CapteurCreate):
    id_capteur: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  MESURE
# ══════════════════════════════════════════════

class MesureCreate(BaseModel):
    timestamp: datetime
    pollution: Optional[float] = None
    temperature: Optional[float] = None
    humidite: Optional[float] = None
    id_capteur: Optional[int] = None

class MesureUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    pollution: Optional[float] = None
    temperature: Optional[float] = None
    humidite: Optional[float] = None
    id_capteur: Optional[int] = None

class MesureOut(MesureCreate):
    id_mesure: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  CITOYEN
# ══════════════════════════════════════════════

class CitoyenCreate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    score_ecolo: Optional[int] = None
    date_inscription: Optional[datetime] = None
    preference_mobilite: Optional[str] = None
    adresse: Optional[str] = None
    id_zone: Optional[int] = None

class CitoyenUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    score_ecolo: Optional[int] = None
    date_inscription: Optional[datetime] = None
    preference_mobilite: Optional[str] = None
    adresse: Optional[str] = None
    id_zone: Optional[int] = None

class CitoyenOut(CitoyenCreate):
    id_citoyen: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  TECHNICIEN
# ══════════════════════════════════════════════

class TechnicienCreate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    specialite: Optional[str] = None
    disponible: Optional[bool] = None
    certification: Optional[str] = None

class TechnicienUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    specialite: Optional[str] = None
    disponible: Optional[bool] = None
    certification: Optional[str] = None

class TechnicienOut(TechnicienCreate):
    id_technicien: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  PROPRIETAIRE
# ══════════════════════════════════════════════

class ProprietaireCreate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    siret: Optional[str] = None

class ProprietaireUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    siret: Optional[str] = None

class ProprietaireOut(ProprietaireCreate):
    id_proprietaire: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  INTERVENTION
# ══════════════════════════════════════════════

class InterventionCreate(BaseModel):
    statut: Optional[str] = None
    priorite: Optional[str] = None
    ia_validee: Optional[bool] = None
    cout: Optional[int] = None
    nature_intervention: Optional[str] = None
    impact_environnemental: Optional[str] = None
    date_demande: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    id_zone: Optional[int] = None
    id_proprietaire: Optional[int] = None

class InterventionUpdate(BaseModel):
    statut: Optional[str] = None
    priorite: Optional[str] = None
    ia_validee: Optional[bool] = None
    cout: Optional[int] = None
    nature_intervention: Optional[str] = None
    impact_environnemental: Optional[str] = None
    date_demande: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    id_zone: Optional[int] = None
    id_proprietaire: Optional[int] = None

class InterventionOut(InterventionCreate):
    id_intervention: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  CONSULTATION
# ══════════════════════════════════════════════

class ConsultationCreate(BaseModel):
    titre: Optional[str] = None
    date_consultation: Optional[datetime] = None
    statut: Optional[str] = None
    description: Optional[str] = None
    type_consultation: Optional[str] = None
    id_zone: Optional[int] = None

class ConsultationUpdate(BaseModel):
    titre: Optional[str] = None
    date_consultation: Optional[datetime] = None
    statut: Optional[str] = None
    description: Optional[str] = None
    type_consultation: Optional[str] = None
    id_zone: Optional[int] = None

class ConsultationOut(ConsultationCreate):
    id_consultation: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  VEHICULE
# ══════════════════════════════════════════════

class VehiculeCreate(BaseModel):
    modele: Optional[str] = None
    statut: Optional[str] = None
    batterie_pct: Optional[float] = None
    vitesse_kmh: Optional[float] = None
    type_vehicule: Optional[str] = None
    energie_utilisee: Optional[str] = None

class VehiculeUpdate(BaseModel):
    modele: Optional[str] = None
    statut: Optional[str] = None
    batterie_pct: Optional[float] = None
    vitesse_kmh: Optional[float] = None
    type_vehicule: Optional[str] = None
    energie_utilisee: Optional[str] = None

class VehiculeOut(VehiculeCreate):
    id_vehicule: int
    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  TRAJET
# ══════════════════════════════════════════════

class TrajetCreate(BaseModel):
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    distance_km: Optional[float] = None
    duree_min: Optional[float] = None
    economie_co2: Optional[float] = None
    statut: Optional[str] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    id_vehicule: Optional[int] = None

class TrajetUpdate(BaseModel):
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    distance_km: Optional[float] = None
    duree_min: Optional[float] = None
    economie_co2: Optional[float] = None
    statut: Optional[str] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    id_vehicule: Optional[int] = None

class TrajetOut(TrajetCreate):
    id_trajet: int
    model_config = ConfigDict(from_attributes=True)
