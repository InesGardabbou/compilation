from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class CapteursHistoriqueEtats(Base):
    __tablename__ = "capteurs_historique_etats"

    id = Column(Integer, primary_key=True)

    capteur_id = Column(Integer, ForeignKey("capteurs.id_capteur"))

    ancien_etat = Column(String)
    nouvel_etat = Column(String)
    evenement = Column(String)

    date_transition = Column(DateTime, default=datetime.utcnow)

    # 🔗 relation vers capteur
    capteur = relationship("Capteur", backref="historique_etats")