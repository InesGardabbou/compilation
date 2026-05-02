from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Intervention(Base):
    __tablename__ = "interventions"

    id_intervention = Column(Integer, primary_key=True, index=True)

    statut = Column(String)
    priorite = Column(String)
    ia_validee = Column(Boolean)

    cout = Column(Integer)
    nature_intervention = Column(String)
    impact_environnemental = Column(String)

    date_demande = Column(DateTime)
    date_debut = Column(DateTime)
    date_fin = Column(DateTime)

    id_zone = Column(Integer, ForeignKey("zones.id_zone"))
    id_proprietaire = Column(Integer, ForeignKey("proprietaires.id_proprietaire"))

    # 🔥 CORRECT FOREIGN KEY
    id_technicien = Column(Integer, ForeignKey("techniciens.id_technicien"))

    # relations
    zone = relationship("Zone", back_populates="interventions")
    proprietaire = relationship("Proprietaire", back_populates="interventions")

    technicien = relationship(
        "Technicien",
        back_populates="interventions"
    )