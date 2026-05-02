from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Capteur(Base):
    __tablename__ = "capteurs"

    id_capteur = Column(Integer, primary_key=True)
    nom = Column(String)
    type_capteur = Column(String)
    statut = Column(String)
    taux_erreur = Column(Float)
    date_installation = Column(DateTime)
    fabricant = Column(String)
    localisation_gps = Column(String)
    description = Column(String)
    unite = Column(String)

    id_zone = Column(Integer, ForeignKey("zones.id_zone"))

    zone = relationship("Zone", back_populates="capteurs")