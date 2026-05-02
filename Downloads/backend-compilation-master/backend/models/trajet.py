from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Trajet(Base):
    __tablename__ = "trajets"

    id_trajet = Column(Integer, primary_key=True)

    date_debut = Column(DateTime)
    date_fin = Column(DateTime)
    distance_km = Column(Float)
    duree_min = Column(Float)
    economie_co2 = Column(Float)

    statut = Column(String)
    origine = Column(String)
    destination = Column(String)

    id_vehicule = Column(Integer, ForeignKey("vehicules.id_vehicule"))

    vehicule = relationship("Vehicule", back_populates="trajets")