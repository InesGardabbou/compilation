
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def normalize_etat(etat: str) -> str:
    return (etat.lower()
            .replace("é","e").replace("è","e").replace("ê","e")
            .replace("î","i").replace("ô","o").replace("û","u"))

def db_to_automate(etat: str) -> str:
    etat = etat.strip().lower().replace("é","e").replace("è","e").replace("ê","e")
    mapping = {
        "demande": "DEMANDE", "tech1_assigne": "TECH1_ASSIGNÉ",
        "tech2_valide": "TECH2_VALIDÉ", "ia_valide": "IA_VALIDÉ",
        "termine": "TERMINÉ", "en_cours": "EN_COURS",
        "inactif": "INACTIF", "actif": "ACTIF",
        "signale": "SIGNALÉ", "en_maintenance": "EN_MAINTENANCE", "hors_service": "HORS_SERVICE",
        "stationne": "STATIONNÉ", "en_route": "EN_ROUTE", "en_panne": "EN_PANNE", "arrive": "ARRIVÉ",
    }
    return mapping.get(etat, etat.upper())


# ══════════════════════════════════════════════════════════════
#  MOTEUR DE BASE
# ══════════════════════════════════════════════════════════════

class TransitionError(Exception):
    pass

class Automate:
    ETATS = []; ETAT_INITIAL = ""; ETATS_FINAUX = []; TRANSITIONS = {}

    def __init__(self, identifiant: str, etat_courant: Optional[str] = None):
        self.identifiant  = identifiant
        self.etat_courant = etat_courant or self.ETAT_INITIAL
        self.historique   = [("init", self.etat_courant, datetime.now())]
        self.created_at   = datetime.now()
        self._alertes     = []

    def transition(self, evenement: str) -> str:
        cle = (self.etat_courant, evenement)
        if cle not in self.TRANSITIONS:
            valides = [ev for (et, ev) in self.TRANSITIONS if et == self.etat_courant]
            raise TransitionError(
                f"[{self.identifiant}] '{evenement}' impossible depuis '{self.etat_courant}'. Valides : {valides}")
        ancien = self.etat_courant
        self.etat_courant = self.TRANSITIONS[cle]
        self.historique.append((evenement, self.etat_courant, datetime.now()))
        print(f"  [{self.identifiant}] {ancien} --{evenement}--> {self.etat_courant}")
        self._actions_automatiques(evenement, ancien, self.etat_courant)
        return self.etat_courant

    def verifier_sequence(self, evenements: list) -> tuple:
        etat_test = self.ETAT_INITIAL
        for ev in evenements:
            cle = (etat_test, ev)
            if cle not in self.TRANSITIONS:
                msg = f"Séquence invalide : '{ev}' impossible depuis '{etat_test}'"
                print(f"  ❌ {msg}"); return False, msg
            etat_test = self.TRANSITIONS[cle]
        est_final = etat_test in self.ETATS_FINAUX
        msg = f"Séquence valide — état final : {etat_test}"
        print(f"  {'✅' if est_final else '⚠️ '} {msg}{'  (acceptant ✓)' if est_final else ''}")
        return True, msg

    def est_final(self) -> bool: return self.etat_courant in self.ETATS_FINAUX
    def evenements_possibles(self) -> list: return [ev for (et, ev) in self.TRANSITIONS if et == self.etat_courant]

    def afficher_historique(self):
        print(f"\n  Historique [{self.identifiant}] :")
        for ev, etat, ts in self.historique:
            print(f"    {ts.strftime('%H:%M:%S')}  {ev:25s} → {etat}")

    def table_de_transition(self):
        print(f"\n  Table de transition – {self.__class__.__name__}")
        print(f"  {'État courant':<20} {'Événement':<25} {'État suivant':<20}")
        print(f"  {'-'*65}")
        for (etat, ev), suivant in sorted(self.TRANSITIONS.items()):
            print(f"  {etat:<20} {ev:<25} {suivant:<20}")

    def _actions_automatiques(self, evenement, ancien, nouveau): pass


# ══════════════════════════════════════════════════════════════
#  AUTOMATE 1 : CAPTEUR
# ══════════════════════════════════════════════════════════════

class AutomateCapteur(Automate):
    ETATS        = ["INACTIF", "ACTIF", "SIGNALÉ", "EN_MAINTENANCE", "HORS_SERVICE"]
    ETAT_INITIAL = "INACTIF"
    ETATS_FINAUX = ["HORS_SERVICE"]
    TRANSITIONS  = {
        ("INACTIF",        "installation"):  "ACTIF",
        ("ACTIF",          "anomalie"):      "SIGNALÉ",
        ("SIGNALÉ",        "réparation"):    "EN_MAINTENANCE",
        ("EN_MAINTENANCE", "réparation_ok"): "ACTIF",
        ("EN_MAINTENANCE", "panne"):         "HORS_SERVICE",
    }
    SEUIL_ALERTE_HEURES = 24

    def _actions_automatiques(self, evenement, ancien, nouveau):
        if nouveau == "SIGNALÉ":
            a = f"⚠️  Capteur '{self.identifiant}' signalé – intervention requise !"
            self._alertes.append(a); print(f"  {a}")
        if nouveau == "HORS_SERVICE":
            a = f"🚨 Capteur '{self.identifiant}' HORS SERVICE !"
            self._alertes.append(a); print(f"  {a}")

    def verifier_alerte_hors_service(self, heures_ecoulees: float) -> bool:
        if self.etat_courant == "HORS_SERVICE" and heures_ecoulees > self.SEUIL_ALERTE_HEURES:
            a = f"🚨 ALERTE : Capteur '{self.identifiant}' hors service depuis {heures_ecoulees:.1f}h !"
            self._alertes.append(a); print(f"  {a}"); return True
        return False

    def appliquer_en_db(self, id_capteur: int, evenement: str, commentaire: str = "") -> bool:
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT statut FROM capteurs WHERE id_capteur = %s", (id_capteur,))
                    row = cur.fetchone()
                    if not row: print(f"  ✗ Capteur {id_capteur} introuvable."); return False
                    self.etat_courant = db_to_automate(row["statut"])
                    etat_prec = self.etat_courant
                    try: nouvel_etat = self.transition(evenement)
                    except TransitionError as e: print(f"  ✗ {e}"); return False
                    nouvel_db = normalize_etat(nouvel_etat)
                    cur.execute("UPDATE capteurs SET statut = %s WHERE id_capteur = %s", (nouvel_db, id_capteur))
                    cur.execute("""
                        INSERT INTO capteurs_historique_etats
                        (capteur_id, ancien_etat, nouvel_etat, evenement)
                        VALUES (%s, %s, %s, %s)
                    """, (id_capteur, etat_prec, nouvel_db, evenement))
            print(f"  ✓ Capteur {id_capteur} : {etat_prec} → {nouvel_db}"); return True
        except Exception as e: print(f"  ✗ Erreur DB : {e}"); return False


# ══════════════════════════════════════════════════════════════
#  AUTOMATE 2 : INTERVENTION
# ══════════════════════════════════════════════════════════════

class AutomateIntervention(Automate):
    ETATS        = ["DEMANDE", "TECH1_ASSIGNÉ", "TECH2_VALIDÉ", "IA_VALIDÉ", "TERMINÉ"]
    ETAT_INITIAL = "DEMANDE"
    ETATS_FINAUX = ["TERMINÉ"]
    TRANSITIONS  = {
        ("DEMANDE",       "assignation"):      "TECH1_ASSIGNÉ",
        ("TECH1_ASSIGNÉ", "validation_tech2"): "TECH2_VALIDÉ",
        ("TECH2_VALIDÉ",  "validation_ia"):    "IA_VALIDÉ",
        ("IA_VALIDÉ",     "clôture"):          "TERMINÉ",
    }

    def _actions_automatiques(self, evenement, ancien, nouveau):
        msgs = {
            "TECH1_ASSIGNÉ": f"  📋 Intervention '{self.identifiant}' : technicien 1 assigné.",
            "TECH2_VALIDÉ":  f"  ✅ Intervention '{self.identifiant}' : validée par technicien 2.",
            "IA_VALIDÉ":     f"  🤖 Intervention '{self.identifiant}' : validée par l'IA.",
            "TERMINÉ":       f"  🏁 Intervention '{self.identifiant}' terminée.",
        }
        if nouveau in msgs: print(msgs[nouveau])

    def appliquer_en_db(self, id_intervention: int, evenement: str, commentaire: str = "") -> bool:
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT statut FROM interventions WHERE id_intervention = %s", (id_intervention,))
                    row = cur.fetchone()
                    if not row: print(f"  ✗ Intervention {id_intervention} introuvable."); return False
                    self.etat_courant = db_to_automate(row["statut"])
                    etat_prec = self.etat_courant
                    try: nouvel_etat = self.transition(evenement)
                    except TransitionError as e: print(f"  ✗ {e}"); return False
                    nouvel_db = normalize_etat(nouvel_etat)
                    champs = "statut = %s"; vals = [nouvel_db]
                    if evenement == "validation_ia": champs += ", ia_validee = TRUE"
                    if evenement == "clôture":       champs += ", date_fin = NOW()"
                    vals.append(id_intervention)
                    cur.execute(f"UPDATE interventions SET {champs} WHERE id_intervention = %s", vals)
            print(f"  ✓ Intervention {id_intervention} : {etat_prec} → {nouvel_db}"); return True
        except Exception as e: print(f"  ✗ Erreur DB : {e}"); return False


# ══════════════════════════════════════════════════════════════
#  AUTOMATE 3 : VÉHICULE
# ══════════════════════════════════════════════════════════════

class AutomateVehicule(Automate):
    ETATS        = ["STATIONNÉ", "EN_ROUTE", "EN_PANNE", "ARRIVÉ"]
    ETAT_INITIAL = "STATIONNÉ"
    ETATS_FINAUX = ["ARRIVÉ"]
    TRANSITIONS  = {
        ("STATIONNÉ", "départ"):     "EN_ROUTE",
        ("EN_ROUTE",  "panne"):      "EN_PANNE",
        ("EN_PANNE",  "réparation"): "EN_ROUTE",
        ("EN_ROUTE",  "arrivée"):    "ARRIVÉ",
    }

    def _actions_automatiques(self, evenement, ancien, nouveau):
        if nouveau == "EN_PANNE":
            a = f"🚗💥 PANNE : Véhicule '{self.identifiant}' en panne !"
            self._alertes.append(a); print(f"  {a}")
        if nouveau == "EN_ROUTE" and ancien == "EN_PANNE": print(f"  🔧 Véhicule '{self.identifiant}' réparé.")
        if nouveau == "ARRIVÉ": print(f"  🏁 Véhicule '{self.identifiant}' arrivé.")

    def appliquer_en_db(self, id_vehicule: int, evenement: str, commentaire: str = "") -> bool:
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT statut FROM vehicules WHERE id_vehicule = %s", (id_vehicule,))
                    row = cur.fetchone()
                    if not row: print(f"  ✗ Véhicule {id_vehicule} introuvable."); return False
                    self.etat_courant = db_to_automate(row["statut"])
                    etat_prec = self.etat_courant
                    try: nouvel_etat = self.transition(evenement)
                    except TransitionError as e: print(f"  ✗ {e}"); return False
                    nouvel_db = normalize_etat(nouvel_etat)
                    cur.execute("UPDATE vehicules SET statut = %s WHERE id_vehicule = %s", (nouvel_db, id_vehicule))
            print(f"  ✓ Véhicule {id_vehicule} : {etat_prec} → {nouvel_db}"); return True
        except Exception as e: print(f"  ✗ Erreur DB : {e}"); return False


# ══════════════════════════════════════════════════════════════
#  SURVEILLANT
# ══════════════════════════════════════════════════════════════

class SurveillantCapteurs:
    def __init__(self, seuil_heures: int = 24): self.seuil = seuil_heures

    def verifier(self) -> list:
        alertes = []
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id_capteur, nom, statut FROM capteurs
                        WHERE statut = 'hors_service'
                          AND date_installation < NOW() - INTERVAL %s
                    """, (f"{self.seuil} hours",))
                    for row in cur.fetchall():
                        a = {"id_capteur": row["id_capteur"], "nom": row["nom"],
                             "message": f"Capteur '{row['nom']}' hors service depuis > {self.seuil}h !"}
                        alertes.append(a); print(f"  🚨 ALERTE : {a['message']}")
        except Exception as e: print(f"  ✗ Erreur surveillance : {e}")
        return alertes

SurveillanCapteurs = SurveillantCapteurs


# ══════════════════════════════════════════════════════════════
#  DÉMOS
# ══════════════════════════════════════════════════════════════

def demo_sans_db():
    print("\n" + "═"*60)
    print("  DÉMONSTRATION AUTOMATES (sans DB)")
    print("═"*60)

    print("\n--- Capteur C-452 ---")
    c = AutomateCapteur("C-452")
    for ev in ["installation", "anomalie", "réparation", "réparation_ok", "anomalie", "réparation", "panne"]:
        c.transition(ev)
    c.verifier_alerte_hors_service(30)

    print("\n--- Vérification séquences ---")
    c2 = AutomateCapteur("C-TEST")
    c2.verifier_sequence(["installation", "anomalie", "réparation", "panne"])
    c2.verifier_sequence(["installation", "panne"])

    c.table_de_transition()

    print("\n--- Intervention INT-001 ---")
    i = AutomateIntervention("INT-001")
    for ev in ["assignation", "validation_tech2", "validation_ia", "clôture"]:
        i.transition(ev)

    print("\n--- Véhicule VEH-007 ---")
    v = AutomateVehicule("VEH-007")
    for ev in ["départ", "panne", "réparation", "arrivée"]:
        v.transition(ev)

    print("\n--- Transition invalide ---")
    try: v.transition("départ")
    except TransitionError as e: print(f"  ❌ {e}")

    print("\n✅ Terminé.")


def demo_avec_db():
    print("\n" + "═"*60)
    print("  DÉMONSTRATION AVEC BASE DE DONNÉES")
    print("═"*60)

    print("\n--- Capteur ---")
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id_capteur, statut FROM capteurs WHERE statut IN ('inactif','actif') LIMIT 1")
                row = cur.fetchone()
        if row:
            cap_id = row["id_capteur"]
            ac = AutomateCapteur(f"C-{cap_id}")
            if db_to_automate(row["statut"]) == "INACTIF":
                ac.appliquer_en_db(cap_id, "installation")
            ac.appliquer_en_db(cap_id, "anomalie", "Taux erreur > 15%")
        else: print("  Aucun capteur inactif/actif trouvé.")
    except Exception as e: print(f"  ✗ {e}")

    print("\n--- Intervention ---")
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id_intervention FROM interventions WHERE statut = 'demande' LIMIT 1")
                row = cur.fetchone()
        if row:
            inter_id = row["id_intervention"]
            ai = AutomateIntervention(f"INT-{inter_id}")
            for ev in ["assignation", "validation_tech2", "validation_ia", "clôture"]:
                ai.appliquer_en_db(inter_id, ev)
        else: print("  Aucune intervention en demande.")
    except Exception as e: print(f"  ✗ {e}")

    print("\n--- Surveillance ---")
    alertes = SurveillantCapteurs(24).verifier()
    print(f"  {len(alertes)} alerte(s).")
