from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Mesure(Base):
    __tablename__ = "mesures"

    id_mesure = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, nullable=False)

    pollution = Column(Float)
    temperature = Column(Float)
    humidite = Column(Float)

    id_zone = Column(Integer, ForeignKey("zones.id_zone"))

    zone = relationship("Zone", back_populates="mesures")