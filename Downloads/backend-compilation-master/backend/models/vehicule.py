from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database.db import Base

class Vehicule(Base):
    __tablename__ = "vehicules"

    id_vehicule = Column(Integer, primary_key=True)
    modele = Column(String)
    statut = Column(String)
    batterie_pct = Column(Float)
    vitesse_kmh = Column(Float)
    type_vehicule = Column(String)
    energie_utilisee = Column(String)

    trajets = relationship("Trajet", back_populates="vehicule")