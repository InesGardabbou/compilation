from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Consultation(Base):
    __tablename__ = "consultations"

    id_consultation = Column(Integer, primary_key=True)
    titre = Column(String)
    date_consultation = Column(DateTime)
    statut = Column(String)
    description = Column(String)
    type_consultation = Column(String)

    id_zone = Column(Integer, ForeignKey("zones.id_zone"))

    zone = relationship("Zone", back_populates="consultations")