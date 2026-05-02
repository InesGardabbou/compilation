from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Citoyen(Base):
    __tablename__ = "citoyens"

    id_citoyen = Column(Integer, primary_key=True)
    nom = Column(String)
    prenom = Column(String)
    email = Column(String)
    telephone = Column(String)
    score_ecolo = Column(Integer)
    date_inscription = Column(DateTime)
    preference_mobilite = Column(String)
    adresse = Column(String)

    id_zone = Column(Integer, ForeignKey("zones.id_zone"))

    zone = relationship("Zone", back_populates="citoyens")