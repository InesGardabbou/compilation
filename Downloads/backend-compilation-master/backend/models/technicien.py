from sqlalchemy import Column, Integer, String, Boolean
from database.db import Base
from sqlalchemy.orm import relationship

class Technicien(Base):
    __tablename__ = "techniciens"

    id_technicien = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    specialite = Column(String)
    disponible = Column(Boolean)
    certification = Column(String)

    # 🔥 relation correcte
    interventions = relationship(
        "Intervention",
        back_populates="technicien"
    )