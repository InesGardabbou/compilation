from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base

class Proprietaire(Base):
    __tablename__ = "proprietaires"

    id_proprietaire = Column(Integer, primary_key=True)
    nom = Column(String)
    adresse = Column(String)
    telephone = Column(String)
    email = Column(String)
    type = Column(String)
    siret = Column(String)

    interventions = relationship("Intervention", back_populates="proprietaire")