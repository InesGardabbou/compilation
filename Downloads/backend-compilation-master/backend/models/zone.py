from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database.db import Base

class Zone(Base):
    __tablename__ = "zones"

    id_zone = Column(Integer, primary_key=True, index=True)
    nom_zone = Column(String, nullable=False)
    surface_km2 = Column(Float)
    population = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    type_zone = Column(String)

    capteurs = relationship("Capteur", back_populates="zone")
    citoyens = relationship("Citoyen", back_populates="zone")
    consultations = relationship("Consultation", back_populates="zone")
    interventions = relationship("Intervention", back_populates="zone")
    mesures = relationship("Mesure", back_populates="zone")  