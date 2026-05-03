
from __future__ import annotations
import os, json, statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ✅ AJOUT ICI
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
# ══════════════════════════════════════════════════════════════
#  TYPES
# ══════════════════════════════════════════════════════════════

class TypeRapport(str, Enum):
    QUALITE_AIR="qualite_air"; CAPTEURS="capteurs"; INTERVENTIONS="interventions"
    VEHICULES="vehicules"; CITOYENS="citoyens"; COMPLET="complet"

@dataclass
class Anomalie:
    entite: str; identifiant: str; severite: str; message: str
    valeur: float | None = None; seuil: float | None = None; recommandation: str = ""

@dataclass
class Rapport:
    type_rapport: str; genere_le: str; periode: str; resume: str; details: str
    recommandations: list[dict]; anomalies: list[Anomalie]
    kpis: dict[str, Any]; score_global: float; moteur: str

SEUILS = {"pollution": 50.0, "taux_erreur": 10.0, "hors_service": 24, "score_ecolo": 40, "batterie": 20}


# ══════════════════════════════════════════════════════════════
#  DB
# ══════════════════════════════════════════════════════════════

def _query(sql: str, params: tuple = ()) -> list[dict]:
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"  ✗ Erreur DB : {e}"); return []

"""
PATCH FINAL pour services/ia_generative.py
===========================================
Schéma réel découvert :

  mesures  : id_mesure, timestamp, pollution, temperature, humidite, id_zone
  capteurs : id_capteur, nom, type_capteur, statut, taux_erreur,
             date_installation, fabricant, localisation_gps,
             description, unite, id_zone
  zones    : id_zone, nom_zone, ...

  ➜ mesures et capteurs sont liés via id_zone (pas de FK directe)
  ➜ pas de colonne 'bruit' dans mesures
  ➜ TimescaleDB absent → pas de time_bucket(), on utilise date_trunc()

Remplace _charger_donnees() dans services/ia_generative.py par ce bloc.
"""


def _charger_donnees() -> dict:

    # ── Mesures agrégées par heure + zone (7 jours) ──────────
    # mesures.id_zone = capteurs.id_zone = zones.id_zone
    sql_mesures = """
        SELECT
            date_trunc('hour', m.timestamp)        AS bucket,
            z.nom_zone,
            ROUND(AVG(m.pollution)::NUMERIC, 2)    AS pollution,
            ROUND(AVG(m.temperature)::NUMERIC, 2)  AS temperature,
            ROUND(AVG(m.humidite)::NUMERIC, 2)     AS humidite,
            COUNT(*)                                AS nb_mesures
        FROM mesures m
        JOIN zones z ON m.id_zone = z.id_zone
        WHERE m.timestamp > NOW() - INTERVAL '7 days'
        GROUP BY bucket, z.nom_zone
        ORDER BY bucket DESC
    """

    # ── Mesures récentes : dernière mesure par zone ───────────
    sql_recentes = """
        SELECT DISTINCT ON (m.id_zone)
               m.id_zone,
               m.id_zone        AS id_capteur,
               m.timestamp,
               m.pollution,
               m.temperature,
               m.humidite
        FROM mesures m
        ORDER BY m.id_zone, m.timestamp DESC
    """

    # ── Évolution pollution 24h par tranche de 3h ────────────
    sql_evolution = """
        SELECT
            date_trunc('hour', m.timestamp)
                - (EXTRACT(HOUR FROM m.timestamp)::INT % 3) * INTERVAL '1 hour'
                                                            AS bucket,
            z.nom_zone,
            ROUND(AVG(m.pollution)::NUMERIC, 2)             AS pollution_moy,
            ROUND(MAX(m.pollution)::NUMERIC, 2)             AS pollution_max,
            ROUND(MIN(m.pollution)::NUMERIC, 2)             AS pollution_min
        FROM mesures m
        JOIN zones z ON m.id_zone = z.id_zone
        WHERE m.timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY bucket, z.nom_zone
        ORDER BY bucket DESC, pollution_moy DESC
    """

    return {
        "capteurs":            _query("SELECT * FROM capteurs"),
        "mesures":             _query(sql_mesures),
        "mesures_recentes":    _query(sql_recentes),
        "evolution_pollution": _query(sql_evolution),
        "zones":               _query("SELECT * FROM zones"),
        "citoyens":            _query("SELECT * FROM citoyens"),
        "interventions":       _query("SELECT * FROM interventions"),
        "techniciens":         _query("SELECT * FROM techniciens"),
        "vehicules":           _query("SELECT * FROM vehicules"),
        "trajets":             _query("SELECT * FROM trajets"),
    }

# ══════════════════════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════════════════════

def _moy(v): return round(statistics.mean(v), 2) if v else 0.0
def _now_fr(): return datetime.now().strftime("%d/%m/%Y à %H:%M")
def _periode(j=7):
    fin = datetime.now(); debut = fin - timedelta(days=j)
    return f"du {debut.strftime('%d/%m/%Y')} au {fin.strftime('%d/%m/%Y')}"
def _severite(ratio):
    if ratio >= 2.0: return "critique"
    if ratio >= 1.5: return "élevée"
    if ratio >= 1.0: return "modérée"
    return "faible"
def _emoji(s): return {"critique":"🔴","élevée":"🟠","modérée":"🟡","faible":"🟢"}.get(s,"⚪")


# ══════════════════════════════════════════════════════════════
#  MOTEUR IA
# ══════════════════════════════════════════════════════════════

class MoteurIA:

    def generer_rapport(self, type_rapport: str, donnees: dict | None = None) -> Rapport:
        if donnees is None: donnees = _charger_donnees()
        return {
            TypeRapport.QUALITE_AIR:   self._rapport_air,
            TypeRapport.CAPTEURS:      self._rapport_capteurs,
            TypeRapport.INTERVENTIONS: self._rapport_interventions,
            TypeRapport.VEHICULES:     self._rapport_vehicules,
            TypeRapport.CITOYENS:      self._rapport_citoyens,
            TypeRapport.COMPLET:       self._rapport_complet,
        }.get(type_rapport, self._rapport_complet)(donnees)

    def _rapport_air(self, d):
        mesures   = d.get("mesures", [])
        evolution = d.get("evolution_pollution", [])
        poll_zone = {}
        for m in mesures:
            zone = m.get("nom_zone", "?")
            val  = m.get("pollution")
            if val is not None: poll_zone.setdefault(zone, []).append(float(val))
        stats = {z: _moy(v) for z, v in poll_zone.items()}
        anomalies = []
        for zone, moy in sorted(stats.items(), key=lambda x: -x[1]):
            if moy > SEUILS["pollution"]:
                ratio = moy / SEUILS["pollution"]
                anomalies.append(Anomalie("zone", zone, _severite(ratio),
                    f"{zone} : {moy} µg/m³ (seuil {SEUILS['pollution']})", moy, SEUILS["pollution"],
                    f"Réduire les émissions dans {zone} — dépasse de {round((ratio-1)*100)}% le seuil."))
        critiques = [a for a in anomalies if a.severite in ("critique","élevée")]
        toutes    = [v for vs in poll_zone.values() for v in vs]
        moy_glob  = _moy(toutes)
        kpis      = {"pollution_moyenne": moy_glob, "zones_surveillees": len(stats), "zones_critiques": len(critiques), "total_buckets_ts": len(mesures), "seuil_oms": SEUILS["pollution"]}
        date_auj  = datetime.now().strftime("%d/%m/%Y")
        if not critiques:
            resume = f"Rapport qualité de l'air du {date_auj} : toutes les zones respectent les seuils. Pollution moyenne : {moy_glob} µg/m³."
        else:
            noms = ", ".join(a.identifiant for a in critiques[:3])
            resume = f"Rapport qualité de l'air du {date_auj} : {len(critiques)} zone(s) dépassent les seuils : {noms}. Pollution moyenne : {moy_glob} µg/m³."
        details = [f"📊 Analyse pollution par zone — {_periode()} :"]
        for zone, moy in sorted(stats.items(), key=lambda x: -x[1]):
            details.append(f"  • {zone:<20} {moy:>7.2f} µg/m³  {'⚠️ DÉPASSE' if moy > SEUILS['pollution'] else '✅ OK'}")
        if evolution:
            details.append(f"\n📈 Évolution 24h (buckets 3h) :")
            vues = set()
            for e in evolution[:6]:
                z = e.get("nom_zone","?")
                if z not in vues:
                    vues.add(z)
                    details.append(f"  • {z:<20} moy={e.get('pollution_moy','?')} max={e.get('pollution_max','?')} min={e.get('pollution_min','?')} µg/m³")
        score = max(0, 100 - (len(critiques)/max(len(stats),1))*100)
        return Rapport(TypeRapport.QUALITE_AIR, _now_fr(), _periode(), resume, "\n".join(details), self._recos_air(anomalies, kpis), anomalies, kpis, round(score,1), "MoteurIA v2.0 (TimescaleDB)")

    def _rapport_capteurs(self, d):
        capteurs = d.get("capteurs", []); mesures_rec = d.get("mesures_recentes", [])
        derniere  = {m["id_capteur"]: m for m in mesures_rec}
        compteurs = {"inactif":0,"actif":0,"signale":0,"en_maintenance":0,"hors_service":0}
        anomalies = []
        for c in capteurs:
            statut   = str(c.get("statut","")).lower().replace("é","e")
            nom      = c.get("nom", f"C-{c.get('id_capteur','?')}")
            taux_err = float(c.get("taux_erreur") or 0)
            for k in compteurs:
                if k in statut: compteurs[k] += 1; break
            if "hors_service" in statut:
                anomalies.append(Anomalie("capteur", nom, "critique", f"Capteur {nom} hors service", recommandation=f"Maintenance urgente pour {nom}."))
            elif "signal" in statut:
                anomalies.append(Anomalie("capteur", nom, "élevée", f"Capteur {nom} signalé", recommandation=f"Inspecter {nom}."))
            elif taux_err > SEUILS["taux_erreur"]:
                anomalies.append(Anomalie("capteur", nom, "modérée", f"Capteur {nom} : taux erreur = {taux_err:.1f}%", taux_err, SEUILS["taux_erreur"], f"Recalibrer {nom}."))
        total = len(capteurs); taux_dispo = round(compteurs["actif"]/total*100,1) if total else 0
        kpis  = {**compteurs, "total": total, "taux_disponibilite": taux_dispo, "mesures_temps_reel": len(derniere)}
        if compteurs["hors_service"] == 0:
            resume = f"✅ Réseau de {total} capteurs opérationnel à {taux_dispo}%. Aucun hors service."
        else:
            resume = f"🔴 {compteurs['hors_service']} capteur(s) hors service, {compteurs['en_maintenance']} en maintenance. Disponibilité : {taux_dispo}%."
        details = (f"📡 État du parc ({total} unités) :\n"
                   f"  • Actifs : {compteurs['actif']} | Signalés : {compteurs['signale']} | "
                   f"En maintenance : {compteurs['en_maintenance']} | Hors service : {compteurs['hors_service']}\n"
                   f"  • Disponibilité : {taux_dispo}% | Mesures temps réel : {len(derniere)} capteurs")
        return Rapport(TypeRapport.CAPTEURS, _now_fr(), _periode(), resume, details, self._recos_capteurs(anomalies, kpis), anomalies, kpis, taux_dispo, "MoteurIA v2.0 (TimescaleDB)")

    def _rapport_interventions(self, d):
        interventions = d.get("interventions", []); anomalies = []
        compteurs = {"demande":0,"tech1_assigne":0,"tech2_valide":0,"ia_valide":0,"termine":0}
        for inter in interventions:
            statut = str(inter.get("statut","")).lower().replace("é","e")
            for k in compteurs:
                if k in statut: compteurs[k] += 1; break
            if "demande" in statut and str(inter.get("priorite","")).lower() == "urgente":
                anomalies.append(Anomalie("intervention", str(inter.get("id_intervention","?")), "critique",
                    f"Intervention urgente #{inter.get('id_intervention')} non assignée", recommandation="Affecter un technicien immédiatement."))
        total = len(interventions); en_cours = compteurs["tech1_assigne"]+compteurs["tech2_valide"]+compteurs["ia_valide"]
        taux  = round(compteurs["termine"]/total*100,1) if total else 0
        kpis  = {"total":total,"en_attente":compteurs["demande"],"en_cours":en_cours,"terminees":compteurs["termine"],"taux_completion":taux}
        resume  = f"📋 {total} interventions : {en_cours} en cours, {compteurs['demande']} en attente, {compteurs['termine']} terminées ({taux}%)."
        details = (f"🔧 Suivi interventions :\n"
                   f"  • En attente : {compteurs['demande']} | Tech1 : {compteurs['tech1_assigne']} | "
                   f"Tech2 : {compteurs['tech2_valide']} | IA : {compteurs['ia_valide']} | Terminées : {compteurs['termine']}\n"
                   f"  • Taux complétion : {taux}%")
        return Rapport(TypeRapport.INTERVENTIONS, _now_fr(), _periode(), resume, details, self._recos_interventions(anomalies, kpis), anomalies, kpis, taux, "MoteurIA v2.0")

    def _rapport_vehicules(self, d):
        vehicules = d.get("vehicules", []); anomalies = []
        compteurs = {"stationne":0,"en_route":0,"en_panne":0,"arrive":0}
        for v in vehicules:
            statut = str(v.get("statut","")).lower().replace("é","e")
            modele = v.get("modele","?"); batt = float(v.get("batterie_pct") or 100)
            for k in compteurs:
                if k in statut: compteurs[k] += 1; break
            if "panne" in statut:
                anomalies.append(Anomalie("véhicule", modele, "élevée", f"Véhicule {modele} en panne", recommandation=f"Dépanner {modele}."))
            if batt < SEUILS["batterie"]:
                anomalies.append(Anomalie("véhicule", modele, "modérée", f"Batterie {batt:.0f}% sur {modele}", batt, SEUILS["batterie"], f"Recharger {modele}."))
        total = len(vehicules); taux_op = round(compteurs["en_route"]/total*100,1) if total else 0
        kpis   = {**compteurs, "total":total, "taux_operationnel":taux_op}
        resume = f"🚗 Flotte {total} véhicule(s) : {compteurs['en_route']} en route, {compteurs['en_panne']} en panne, {compteurs['stationne']} stationnés. Taux op. : {taux_op}%."
        details= (f"🚘 État flotte :\n"
                  f"  • En route : {compteurs['en_route']} | En panne : {compteurs['en_panne']} | "
                  f"Stationnés : {compteurs['stationne']} | Arrivés : {compteurs['arrive']}\n"
                  f"  • Taux opérationnel : {taux_op}%")
        return Rapport(TypeRapport.VEHICULES, _now_fr(), _periode(), resume, details, self._recos_vehicules(anomalies, kpis), anomalies, kpis, taux_op, "MoteurIA v2.0")

    def _rapport_citoyens(self, d):
        citoyens = d.get("citoyens", [])
        scores   = [float(c["score_ecolo"]) for c in citoyens if c.get("score_ecolo") is not None]
        moy_score= _moy(scores); sous_seuil = [c for c in citoyens if float(c.get("score_ecolo") or 0) < SEUILS["score_ecolo"]]
        top5     = sorted(citoyens, key=lambda c: float(c.get("score_ecolo") or 0), reverse=True)[:5]
        kpis     = {"total":len(citoyens),"score_moyen":moy_score,"score_max":max(scores,default=0),"score_min":min(scores,default=0),"citoyens_critiques":len(sous_seuil)}
        resume   = f"👥 {len(citoyens)} citoyens. Score moyen : {moy_score}/100. {len(sous_seuil)} sous le seuil ({SEUILS['score_ecolo']} pts)."
        top5_str = "\n".join(f"    {i+1}. {c.get('nom')} {c.get('prenom')} — {c.get('score_ecolo')}/100" for i, c in enumerate(top5))
        details  = f"🌱 Engagement citoyens :\n  Score moy/max/min : {moy_score}/{max(scores,default=0)}/{min(scores,default=0)}\n  Sous seuil : {len(sous_seuil)}\n\n  🏆 Top 5 :\n{top5_str}"
        return Rapport(TypeRapport.CITOYENS, _now_fr(), _periode(), resume, details,
                       [{"priorite":"modérée","action":f"Campagne de sensibilisation pour {len(sous_seuil)} citoyens.","impact":"+5 pts score moyen.","delai":"Prochain mois"}],
                       [], kpis, moy_score, "MoteurIA v2.0")

    def _rapport_complet(self, d):
        r_air=self._rapport_air(d); r_cap=self._rapport_capteurs(d)
        r_int=self._rapport_interventions(d); r_veh=self._rapport_vehicules(d); r_cit=self._rapport_citoyens(d)
        toutes  = r_air.anomalies+r_cap.anomalies+r_int.anomalies+r_veh.anomalies
        critiq  = sum(1 for a in toutes if a.severite=="critique")
        score   = round((r_air.score_global+r_cap.score_global+r_int.score_global+r_veh.score_global)/4,1)
        etat    = "✅ BONNE" if critiq==0 else ("⚠️ DÉGRADÉE" if critiq<=3 else "🔴 CRITIQUE")
        date    = datetime.now().strftime("%d/%m/%Y")
        resume  = f"[RAPPORT COMPLET — {date}] Santé : {etat}. Score : {score}/100. {critiq} anomalie(s) critique(s)."
        details = f"{'='*60}\n  RAPPORT COMPLET SMART CITY — {date}\n{'='*60}\n\n{r_air.details}\n\n{r_cap.details}\n\n{r_int.details}\n\n{r_veh.details}\n\n{r_cit.details}"
        recos   = sorted(r_air.recommandations[:2]+r_cap.recommandations[:2]+r_int.recommandations[:1]+r_veh.recommandations[:1],
                         key=lambda r: {"critique":0,"élevée":1,"modérée":2,"faible":3}.get(r.get("priorite","faible"),4))
        return Rapport(TypeRapport.COMPLET, _now_fr(), _periode(), resume, details, recos, toutes,
                       {"score_global":score,"anomalies_critiques":critiq,"air":r_air.kpis,"capteurs":r_cap.kpis,"interventions":r_int.kpis,"vehicules":r_veh.kpis,"citoyens":r_cit.kpis},
                       score, "MoteurIA v2.0 (TimescaleDB)")

    # ── Suggestions ───────────────────────────────────────────

    def suggerer_actions(self, donnees: dict | None = None) -> list[dict]:
        if donnees is None: donnees = _charger_donnees()
        suggestions = []
        for c in donnees.get("capteurs", []):
            nom=c.get("nom","?"); statut=str(c.get("statut","")).lower(); taux_err=float(c.get("taux_erreur") or 0)
            if "hors_service" in statut:
                suggestions.append({"type":"🔴 URGENT","entite":f"Capteur {nom}","message":f"Capteur {nom} hors service.","action":"Maintenance corrective immédiate.","priorite":"critique","delai":"Immédiat (< 6h)"})
            elif "signal" in statut:
                suggestions.append({"type":"🟠 ÉLEVÉ","entite":f"Capteur {nom}","message":f"Capteur {nom} signalé.","action":"Envoyer un technicien.","priorite":"élevée","delai":"Sous 24h"})
            elif taux_err > SEUILS["taux_erreur"]:
                suggestions.append({"type":"🟡 MODÉRÉ","entite":f"Capteur {nom}","message":f"Capteur {nom} : taux erreur {taux_err:.1f}%.","action":"Recalibrer.","priorite":"modérée","delai":"Sous 48h"})
        for inter in donnees.get("interventions", []):
            statut=str(inter.get("statut","")).lower(); priorite=str(inter.get("priorite","")).lower(); iid=inter.get("id_intervention","?")
            if "demande" in statut and priorite in ("urgente","haute"):
                suggestions.append({"type":"🔴 URGENT","entite":f"Intervention #{iid}","message":f"Intervention #{iid} ({priorite}) en attente.","action":"Affecter un technicien.","priorite":"critique","delai":"Immédiat"})
        for v in donnees.get("vehicules", []):
            statut=str(v.get("statut","")).lower(); modele=v.get("modele","?"); batt=float(v.get("batterie_pct") or 100)
            if "panne" in statut:
                suggestions.append({"type":"🟠 ÉLEVÉ","entite":f"Véhicule {modele}","message":f"{modele} en panne.","action":"Envoyer assistance.","priorite":"élevée","delai":"Sous 2h"})
            if batt < SEUILS["batterie"]:
                suggestions.append({"type":"🟡 MODÉRÉ","entite":f"Véhicule {modele}","message":f"Batterie {batt:.0f}% sur {modele}.","action":"Recharger.","priorite":"modérée","delai":"Sous 4h"})
        for m in donnees.get("mesures_recentes", []):
            poll=float(m.get("pollution") or 0); cid=m.get("id_capteur","?")
            if poll > SEUILS["pollution"]*1.5:
                suggestions.append({"type":"🔴 URGENT","entite":f"Capteur #{cid}","message":f"Pic pollution : {poll} µg/m³.","action":"Alerter citoyens.","priorite":"critique","delai":"Immédiat"})
        suggestions.sort(key=lambda s: {"critique":0,"élevée":1,"modérée":2,"faible":3}.get(s.get("priorite","faible"),4))
        return suggestions

    # ── Validation transitions ────────────────────────────────

    def valider_transition(self, type_entite, etat_courant, evenement, contexte=None):
        TRANSITIONS = {
            "capteur": {("inactif","installation"):"actif",("actif","anomalie"):"signale",("signale","reparation"):"en_maintenance",("en_maintenance","reparation_ok"):"actif",("en_maintenance","panne"):"hors_service"},
            "intervention": {("demande","assignation"):"tech1_assigne",("tech1_assigne","validation_tech2"):"tech2_valide",("tech2_valide","validation_ia"):"ia_valide",("ia_valide","cloture"):"termine"},
            "vehicule": {("stationne","depart"):"en_route",("en_route","panne"):"en_panne",("en_panne","reparation"):"en_route",("en_route","arrivee"):"arrive"},
        }
        trans   = TRANSITIONS.get(type_entite, {})
        ec_norm = etat_courant.lower().replace("é","e").replace("è","e")
        ev_norm = evenement.lower().replace("é","e").replace("è","e")
        nouvel  = trans.get((ec_norm, ev_norm))
        if nouvel:
            avert = None
            ctx   = contexte or {}
            if type_entite == "capteur" and ev_norm == "anomalie":
                te = float(ctx.get("taux_erreur", 0))
                if te > 20: avert = f"⚠️ Taux d'erreur très élevé ({te:.1f}%) — vérifier avant réparation."
            return {"valide":True,"nouvel_etat":nouvel,"message":f"✅ [{etat_courant}] --{evenement}--> [{nouvel}] validée.","avertissement":avert,"confiance_ia":0.95}
        else:
            valides = [ev for (et,ev) in trans if et == ec_norm]
            return {"valide":False,"nouvel_etat":None,"message":f"❌ '{evenement}' impossible depuis '{etat_courant}'. Valides : {valides or ['aucun']}.","avertissement":None,"confiance_ia":1.0}

    # ── Recommandations ───────────────────────────────────────

    def _recos_air(self, anomalies, kpis):
        recos = []
        if [a for a in anomalies if a.severite=="critique"]:
            recos.append({"priorite":"critique","action":"Activer le plan d'urgence pollution.","impact":"Réduction exposition immédiate.","delai":"Immédiat"})
        if kpis.get("pollution_moyenne",0) > SEUILS["pollution"]:
            recos.append({"priorite":"élevée","action":"Restreindre circulation dans zones dépassant les seuils.","impact":"Amélioration sous 72h.","delai":"Sous 24h"})
        return recos

    def _recos_capteurs(self, anomalies, kpis):
        recos = []
        if kpis.get("hors_service",0)>0: recos.append({"priorite":"critique","action":f"Remplacer {kpis['hors_service']} capteur(s) hors service.","impact":"Restauration couverture.","delai":"Immédiat"})
        if kpis.get("signale",0)>0:      recos.append({"priorite":"élevée","action":f"Inspecter {kpis['signale']} capteur(s) signalés.","impact":"Prévention pannes.","delai":"Sous 24h"})
        return recos

    def _recos_interventions(self, anomalies, kpis):
        if kpis.get("en_attente",0)>0:
            return [{"priorite":"élevée","action":f"Affecter {kpis['en_attente']} intervention(s) en attente.","impact":"Réduction délai traitement.","delai":"Sous 12h"}]
        return []

    def _recos_vehicules(self, anomalies, kpis):
        if kpis.get("en_panne",0)>0:
            return [{"priorite":"élevée","action":f"Dépanner {kpis['en_panne']} véhicule(s) en panne.","impact":"Restauration capacité.","delai":"Sous 4h"}]
        return []


# ══════════════════════════════════════════════════════════════
#  MOTEUR AVANCÉ (OpenAI optionnel)
# ══════════════════════════════════════════════════════════════

class MoteurIAAvance(MoteurIA):
    def __init__(self):
        super().__init__()
        self.client_langchain = None
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if GROQ_API_KEY:
            try:
                from langchain_groq import ChatGroq
                self.client_langchain = ChatGroq(
                    temperature=0.4,
                    model_name="llama-3.1-8b-instant",
                    api_key=GROQ_API_KEY,
                    max_tokens=250
                )
                print("  ✅ LangChain (Groq Llama-3.1) connecté.")
            except ImportError:
                print("  ⚠️ langchain ou langchain-groq non installé.")
        else:
            print("  ⚠️ GROQ_API_KEY manquante.")

    def _appel_llm(self, prompt, max_tokens=1024):
        if not self.client_langchain: return None
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content="Tu es expert en gestion urbaine Neo-Sousse 2030. Rédige un rapport détaillé, structuré (avec des puces et des titres si nécessaire), professionnel, et concis mais complet."),
                HumanMessage(content=prompt)
            ]
            resp = self.client_langchain.invoke(messages)
            return resp.content.strip()
        except Exception as e:
            print(f"  ⚠️ LangChain/Groq Erreur : {e}")
            return None

    def generer_rapport(self, type_rapport, donnees=None):
        rapport = super().generer_rapport(type_rapport, donnees)
        if not self.client_langchain: return rapport
        critiques = sum(1 for a in rapport.anomalies if a.severite=="critique")
        
        prompt = f"""
        Fais une analyse DÉTAILLÉE pour la Smart City Neo-Sousse concernant le rapport '{type_rapport}'.
        - Score de santé : {rapport.score_global}/100. 
        - Anomalies critiques : {critiques}. 
        - KPIs actuels : {json.dumps(rapport.kpis, ensure_ascii=False, default=float)}.
        
        Ton rapport doit inclure :
        1. Un diagnostic complet de l'état actuel de la ville.
        2. Une explication des anomalies détectées.
        3. Des recommandations concrètes d'actions à prendre.
        """
        
        llm = self._appel_llm(prompt, max_tokens=1024)
        if llm: 
            rapport.resume = llm
            rapport.moteur = "MoteurIAAvance (LangChain + Groq + TimescaleDB)"
        return rapport


# ══════════════════════════════════════════════════════════════
#  AFFICHAGE
# ══════════════════════════════════════════════════════════════

def _afficher_rapport(rapport: Rapport):
    print("\n" + "═"*65)
    print(f"  RAPPORT {rapport.type_rapport.upper()} — {rapport.genere_le}")
    print("═"*65)
    print(f"\n📄 RÉSUMÉ\n  {rapport.resume}")
    print(f"\n📊 DÉTAILS\n{rapport.details}")
    if rapport.anomalies:
        print(f"\n⚠️  ANOMALIES ({len(rapport.anomalies)}) :")
        for a in rapport.anomalies[:5]:
            print(f"  {_emoji(a.severite)} [{a.severite.upper()}] {a.message}")
            if a.recommandation: print(f"     → {a.recommandation}")
    if rapport.recommandations:
        print(f"\n💡 RECOMMANDATIONS ({len(rapport.recommandations)}) :")
        for i, r in enumerate(rapport.recommandations[:4], 1):
            print(f"  {i}. [{r.get('priorite','?').upper()}] {r.get('action','')} | {r.get('delai','')}")
    print(f"\n🤖 {rapport.moteur} | Score : {rapport.score_global}/100")
    print("═"*65)

def _afficher_suggestions(suggestions):
    print("\n" + "═"*65)
    print("  SUGGESTIONS D'ACTIONS — IA GÉNÉRATIVE")
    print("═"*65)
    if not suggestions: print("  ✅ Aucune action urgente."); return
    for i, s in enumerate(suggestions, 1):
        print(f"\n  {i}. {s['type']} — {s['entite']}")
        print(f"     📢 {s['message']}")
        print(f"     ✅ {s['action']} | ⏱️ {s['delai']}")
    print("═"*65)


# ══════════════════════════════════════════════════════════════
#  DÉMOS
# ══════════════════════════════════════════════════════════════

def demo_sans_db():
    print("\n" + "═"*65)
    print("  DÉMONSTRATION IA GÉNÉRATIVE (sans DB)")
    print("═"*65)
    donnees_test = {
        "capteurs": [
            {"id_capteur":1,"nom":"C-101","statut":"actif","taux_erreur":2.1},
            {"id_capteur":2,"nom":"C-202","statut":"hors_service","taux_erreur":25.0},
            {"id_capteur":3,"nom":"C-303","statut":"signale","taux_erreur":12.3},
            {"id_capteur":4,"nom":"C-404","statut":"actif","taux_erreur":0.5},
            {"id_capteur":5,"nom":"C-452","statut":"en_maintenance","taux_erreur":8.7},
        ],
        "mesures": [
            {"nom_zone":"Zone Nord","pollution":45.2},{"nom_zone":"Zone Nord","pollution":51.3},
            {"nom_zone":"Zone Sud","pollution":78.9},{"nom_zone":"Zone Sud","pollution":81.2},
            {"nom_zone":"Zone Centre","pollution":22.3},{"nom_zone":"Zone Industrielle","pollution":95.0},
        ],
        "mesures_recentes": [{"id_capteur":2,"timestamp":datetime.now(),"pollution":82.0}],
        "evolution_pollution": [],
        "interventions": [
            {"id_intervention":1,"statut":"demande","priorite":"urgente"},
            {"id_intervention":2,"statut":"tech1_assigne","priorite":"haute"},
            {"id_intervention":3,"statut":"termine","priorite":"normale"},
            {"id_intervention":4,"statut":"termine","priorite":"normale"},
            {"id_intervention":5,"statut":"ia_valide","priorite":"haute"},
        ],
        "vehicules": [
            {"id_vehicule":1,"modele":"Tesla Model 3","statut":"en_route","batterie_pct":95.0},
            {"id_vehicule":2,"modele":"Renault Zoe","statut":"en_panne","batterie_pct":45.2},
            {"id_vehicule":3,"modele":"BMW iX","statut":"stationne","batterie_pct":15.0},
        ],
        "citoyens": [
            {"id_citoyen":1,"nom":"Ben Ali","prenom":"Mohamed","score_ecolo":85},
            {"id_citoyen":2,"nom":"Trabelsi","prenom":"Fatma","score_ecolo":92},
            {"id_citoyen":3,"nom":"Chaabani","prenom":"Youssef","score_ecolo":35},
        ],
    }
    ia = MoteurIA()
    print("\n📋 Génération de rapports")
    _afficher_rapport(ia.generer_rapport(TypeRapport.QUALITE_AIR,   donnees_test))
    _afficher_rapport(ia.generer_rapport(TypeRapport.CAPTEURS,      donnees_test))
    _afficher_rapport(ia.generer_rapport(TypeRapport.INTERVENTIONS, donnees_test))
    print("\n💡 Suggestions d'actions")
    _afficher_suggestions(ia.suggerer_actions(donnees_test))
    print("\n🤖 Validation de transitions")
    for entite, etat, evenement, ctx in [
        ("capteur","actif","anomalie",{"taux_erreur":25.0}),
        ("capteur","actif","panne",{}),
        ("intervention","tech1_assigne","validation_tech2",{}),
        ("vehicule","arrive","depart",{}),
    ]:
        res = ia.valider_transition(entite, etat, evenement, ctx)
        print(f"\n  {entite} | {etat} --{evenement}-->")
        print(f"  {res['message']}")
        if res.get("avertissement"): print(f"  {res['avertissement']}")
    print("\n✅ Démonstration terminée.")

def demo_avec_db():
    print("\n" + "═"*65)
    print("  DÉMONSTRATION IA GÉNÉRATIVE (avec DB + TimescaleDB)")
    print("═"*65)
    print("  Chargement données...")
    donnees = _charger_donnees()
    if not any(donnees.values()): print("  ✗ Impossible de charger les données."); return
    ia = MoteurIAAvance()
    _afficher_rapport(ia.generer_rapport(TypeRapport.COMPLET, donnees))
    _afficher_suggestions(ia.suggerer_actions(donnees))
    print(f"\n  📊 Analysés : {len(donnees['capteurs'])} capteurs, {len(donnees['mesures'])} buckets, {len(donnees['interventions'])} interventions, {len(donnees['vehicules'])} véhicules, {len(donnees['citoyens'])} citoyens")
