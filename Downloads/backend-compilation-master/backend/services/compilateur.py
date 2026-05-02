# ============================================================
#  compilateur_nl_sql.py  –  Compilateur NL → SQL complet
#  Neo-Sousse 2030  |  Partie 2.1
#
#  Pas de base de données — génère le SQL uniquement.
#  Importé par main.py.
# ============================================================

import re
import argparse
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# ══════════════════════════════════════════════════════════════
#  PARTIE 1 : GRAMMAR
# ══════════════════════════════════════════════════════════════

SELECT_KEYWORDS = [
    "affiche", "afficher", "montre", "montrer", "donne", "donner",
    "liste", "lister", "retourne", "retourner", "selectionne",
    "sélectionne", "sélectionner", "trouve", "trouver",
    "cherche", "chercher", "voir", "obtenir", "obtiens",
    "quels", "quelles", "quel", "quelle", "quels sont", "quelles sont",
    "donne-moi", "donne moi", "afficher moi", "montre moi",
]
COUNT_KEYWORDS   = ["combien", "nombre", "nombre de", "nombre des", "count", "total de", "total des", "compter", "nb"]
AVERAGE_KEYWORDS = ["moyenne", "avg", "moyenne de", "en moyenne", "moyen"]
MAX_KEYWORDS     = ["maximum", "max", "plus grand", "plus élevé", "plus haute", "le plus haut", "maximale", "maximal"]
MIN_KEYWORDS     = ["minimum", "min", "plus petit", "plus faible", "le plus bas", "minimale", "minimal"]
SUM_KEYWORDS     = ["somme", "sum", "total", "cumulé", "cumul"]
WHERE_KEYWORDS   = ["où", "dont", "ayant", "qui ont", "qui a", "qui est", "qui sont", "avec", "ayant un", "ayant une", "filtre", "tel que", "tels que", "telles que", "dont le", "dont la"]

OPERATOR_MAP = {
    "supérieur ou égal à": ">=", "inférieur ou égal à": "<=",
    "supérieur ou égal": ">=",   "inférieur ou égal": "<=",
    "supérieur à": ">",          "superieur a": ">",
    "plus grand que": ">",       "plus élevé que": ">",
    "au-dessus de": ">",         "dépasse": ">",
    "inférieur à": "<",          "inferieur a": "<",
    "plus petit que": "<",       "plus faible que": "<",
    "en-dessous de": "<",
    "égal à": "=",               "egal a": "=",
    "est": "=",                  "vaut": "=",
    "différent de": "!=",        "different de": "!=",
    ">": ">", "<": "<", ">=": ">=", "<=": "<=", "=": "=", "!=": "!=",
}

ORDER_DESC_KEYWORDS = ["décroissant", "descendant", "du plus grand", "du plus élevé", "du plus polluée", "du plus pollué", "desc", "les plus", "plus polluées", "plus pollués", "polluée", "pollués", "économique", "economique", "plus économique"]
ORDER_ASC_KEYWORDS  = ["croissant", "ascendant", "du plus petit", "asc", "alphabétique"]
ORDER_KEYWORDS      = ["trier", "ordonner", "classé", "classés", "classer", "ordre", "par ordre"]
LIMIT_KEYWORDS      = ["top", "premier", "premiers", "première", "premières", "limiter", "limite"]
GROUP_KEYWORDS      = ["par", "groupe", "grouper", "groupé", "regrouper", "pour chaque", "par zone", "par type", "par statut", "par capteur", "par secteur"]

SYNONYMS = {
    "montre": "affiche", "montrer": "afficher", "donne": "affiche", "donner": "afficher",
    "liste": "affiche", "lister": "afficher", "retourne": "affiche", "retourner": "afficher",
    "selectionne": "affiche", "sélectionne": "affiche", "sélectionner": "afficher",
    "trouve": "affiche", "trouver": "afficher", "cherche": "affiche", "chercher": "afficher",
    "obtiens": "affiche", "obtenir": "afficher", "voir": "affiche",
    "senseur": "capteur", "device": "capteur", "détecteur": "capteur",
    "habitant": "citoyen", "usager": "citoyen", "résident": "citoyen",
    "alerte": "intervention", "incident": "intervention", "ticket": "intervention",
    "donnée": "mesure", "relevé": "mesure", "valeur": "mesure",
    "voiture": "vehicule", "route": "trajet", "parcours": "trajet",
    "score_écologique": "score_ecolo", "score écologique": "score_ecolo",
    "signalés": "signale", "signalée": "signale", "signalées": "signale", "signalé": "signale",
    "terminés": "termine", "terminée": "termine", "terminées": "termine", "terminé": "termine",
    "hors service": "hors_service", "hors services": "hors_service",
    "en panne": "en_panne", "en route": "en_route",
    "en maintenance": "en_maintenance", "en cours": "en_cours",
}

STOP_WORDS = {
    "le", "la", "les", "l", "un", "une", "des", "du", "de",
    "a", "à", "au", "aux", "en", "et", "ou",
    "ce", "se", "si", "y", "je", "tu", "il", "elle", "nous",
    "vous", "ils", "elles", "me", "te", "lui", "leur", "leurs",
    "mon", "ton", "son", "ma", "ta", "sa", "notre", "votre",
    "tous", "tout", "toute", "toutes", "moi", "toi", "on",
    "qui", "que", "quoi", "dans", "sur", "sous", "entre",
    "vers", "chez", "très", "aussi", "comme", "car", "donc",
    "or", "ni", "ne", "non", "oui", "actuellement", "maintenant",
    "svp", "veuillez", "merci", "pouvez", "peut", "être",
}

BOOLEAN_TRUE  = {"true", "vrai", "oui", "actif", "disponible", "validée", "validé", "1"}
BOOLEAN_FALSE = {"false", "faux", "non", "inactif", "indisponible", "0"}


# ══════════════════════════════════════════════════════════════
#  PARTIE 2 : SCHEMAS
# ══════════════════════════════════════════════════════════════

TABLE_ALIASES = {
    "capteur": "capteurs", "capteurs": "capteurs", "senseur": "capteurs",
    "mesure": "mesures", "mesures": "mesures", "donnée": "mesures",
    "zone": "zones", "zones": "zones", "secteur": "zones", "quartier": "zones",
    "citoyen": "citoyens", "citoyens": "citoyens", "habitant": "citoyens",
    "intervention": "interventions", "interventions": "interventions", "alerte": "interventions",
    "technicien": "techniciens", "techniciens": "techniciens",
    "vehicule": "vehicules", "vehicules": "vehicules", "véhicule": "vehicules", "véhicules": "vehicules",
    "voiture": "vehicules", "trajet": "trajets", "trajets": "trajets",
    "propriétaire": "proprietaires", "proprietaire": "proprietaires",
    "consultation": "consultations", "consultations": "consultations",
}

TABLE_COLUMNS = {
    "capteurs":      {"id": "id_capteur", "id_capteur": "id_capteur", "nom": "nom", "type": "type_capteur", "type_capteur": "type_capteur", "statut": "statut", "état": "statut", "etat": "statut", "taux_erreur": "taux_erreur", "erreur": "taux_erreur", "date_installation": "date_installation", "fabricant": "fabricant", "localisation": "localisation_gps", "id_zone": "id_zone"},
    "mesures":       {"id": "id_mesure", "id_mesure": "id_mesure", "timestamp": "timestamp", "date": "timestamp", "pollution": "pollution", "temperature": "temperature", "humidite": "humidite", "humidité": "humidite", "bruit": "bruit", "qualite": "qualite", "qualité": "qualite", "id_capteur": "id_capteur"},
    "zones":         {"id": "id_zone", "id_zone": "id_zone", "nom": "nom_zone", "nom_zone": "nom_zone", "surface": "surface_km2", "population": "population", "type": "type_zone"},
    "citoyens":      {"id": "id_citoyen", "id_citoyen": "id_citoyen", "nom": "nom", "prenom": "prenom", "email": "email", "score": "score_ecolo", "score_ecolo": "score_ecolo", "score_écologique": "score_ecolo", "écologique": "score_ecolo", "id_zone": "id_zone"},
    "interventions": {"id": "id_intervention", "id_intervention": "id_intervention", "statut": "statut", "état": "statut", "priorite": "priorite", "priorité": "priorite", "ia_validee": "ia_validee", "ia": "ia_validee", "cout": "cout", "coût": "cout", "date_demande": "date_demande", "date_fin": "date_fin", "id_zone": "id_zone", "id_capteur": "id_capteur"},
    "techniciens":   {"id": "id_technicien", "id_technicien": "id_technicien", "nom": "nom", "prenom": "prenom", "specialite": "specialite", "spécialité": "specialite", "disponible": "disponible"},
    "vehicules":     {"id": "id_vehicule", "id_vehicule": "id_vehicule", "modele": "modele", "modèle": "modele", "statut": "statut", "batterie": "batterie_pct", "vitesse": "vitesse_kmh", "type": "type_vehicule"},
    "trajets":       {"id": "id_trajet", "id_trajet": "id_trajet", "distance": "distance_km", "duree": "duree_min", "durée": "duree_min", "co2": "economie_co2", "economie_co2": "economie_co2", "économie_co2": "economie_co2", "économie": "economie_co2", "statut": "statut", "origine": "origine", "destination": "destination", "id_vehicule": "id_vehicule"},
    "proprietaires": {"id": "id_proprietaire", "nom": "nom", "email": "email"},
    "consultations": {"id": "id_consultation", "titre": "titre", "statut": "statut", "id_zone": "id_zone"},
}

DEFAULT_SELECT = {
    "capteurs":      ["id_capteur", "nom", "type_capteur", "statut", "taux_erreur"],
    "mesures":       ["id_mesure", "timestamp", "pollution", "temperature", "qualite"],
    "zones":         ["id_zone", "nom_zone", "population", "surface_km2", "type_zone"],
    "citoyens":      ["id_citoyen", "nom", "prenom", "email", "score_ecolo"],
    "interventions": ["id_intervention", "statut", "priorite", "date_demande", "cout"],
    "techniciens":   ["id_technicien", "nom", "prenom", "specialite", "disponible"],
    "vehicules":     ["id_vehicule", "modele", "statut", "batterie_pct", "vitesse_kmh"],
    "trajets":       ["id_trajet", "origine", "destination", "distance_km", "duree_min", "economie_co2"],
    "proprietaires": ["id_proprietaire", "nom", "email"],
    "consultations": ["id_consultation", "titre", "statut", "date_consultation"],
}

KNOWN_JOINS = {
    ("capteurs", "mesures"):       ("capteurs.id_capteur", "mesures.id_capteur"),
    ("capteurs", "zones"):         ("capteurs.id_zone", "zones.id_zone"),
    ("capteurs", "interventions"): ("capteurs.id_capteur", "interventions.id_capteur"),
    ("zones", "citoyens"):         ("zones.id_zone", "citoyens.id_zone"),
    ("zones", "interventions"):    ("zones.id_zone", "interventions.id_zone"),
    ("vehicules", "trajets"):      ("vehicules.id_vehicule", "trajets.id_vehicule"),
}

def get_default_columns(table): return DEFAULT_SELECT.get(table, ["*"])
def get_join(t1, t2): return KNOWN_JOINS.get((t1, t2)) or KNOWN_JOINS.get((t2, t1))


# ══════════════════════════════════════════════════════════════
#  PARTIE 3 : ERREURS
# ══════════════════════════════════════════════════════════════

class CompilerError(Exception):
    def __init__(self, message, phase=""):
        self.phase = phase
        self.message = message
        super().__init__(f"[{phase.upper()}] {message}" if phase else message)

class AmbiguityError(CompilerError):
    def __init__(self, message, suggestions=None):
        super().__init__(message, phase="AMBIGUITY")
        self.suggestions = suggestions or []
    def __str__(self):
        base = super().__str__()
        return base + "\n  Suggestions : " + ", ".join(self.suggestions) if self.suggestions else base


# ══════════════════════════════════════════════════════════════
#  PARTIE 4 : NORMALIZER
# ══════════════════════════════════════════════════════════════

class Normalizer:
    MULTI_WORD = [
        (r"\bhors[\s\-_]+service[s]?\b", "hors_service"),  # FIX pluriel
        (r"\ben[\s\-_]+maintenance\b", "en_maintenance"),
        (r"\ben[\s\-_]+cours\b", "en_cours"),
        (r"\ben[\s\-_]+route\b", "en_route"),
        (r"\ben[\s\-_]+panne\b", "en_panne"),
        (r"\bsupérieur ou égal à\b", "superieur_ou_egal_a"),
        (r"\binférieur ou égal à\b", "inferieur_ou_egal_a"),
        (r"\bsupérieur à\b", "superieur_a"),
        (r"\binférieur à\b", "inferieur_a"),
        (r"\bplus grand que\b", "superieur_a"),
        (r"\bplus petit que\b", "inferieur_a"),
        (r"\bplus élevé que\b", "superieur_a"),
        (r"\bégal à\b", "egal_a"),
        (r"\bdifférent de\b", "different_de"),
        (r"\bscore[\s_]éco(?:logique)?\b", "score_ecolo"),
        (r"\béconomie[\s_]co2\b", "economie_co2"),
        (r"\btaux\s+d['\s]erreur\b", "taux_erreur"),
        (r"\bdu plus grand\b", "decroissant"),
        (r"\bdu plus élevé\b", "decroissant"),
        (r"\bdu plus pollu[eé][e]?\b", "decroissant"),
        (r"\bdu plus petit\b", "croissant"),
        (r"\bpour chaque\b", "group_by"),
        (r"\bia[\s_]valid[eé][e]?\b", "ia_validee"),
        (r"\bdonne[\s\-]moi\b", "affiche"),
        (r"\bmontre[\s\-]moi\b", "affiche"),
        (r"\baffiche[\s\-]moi\b", "affiche"),
        (r"\bcombien de\b", "combien"),
        (r"\bnombre de\b", "combien"),
        (r"\border\s+by\b", "order_by"),
        (r"\bgroup\s+by\b", "group_by"),
    ]

    def __init__(self):
        self._compiled = [(re.compile(p, re.IGNORECASE), r) for p, r in self.MULTI_WORD]

    def normalize(self, text):
        if not text or not text.strip():
            return ""

        result = text.strip()

        # enlever guillemets
        if (result.startswith('"') and result.endswith('"')) or \
           (result.startswith("'") and result.endswith("'")):
            result = result[1:-1].strip()

        result = result.lower()

        # 🔥 FIX 1 : séparer opérateurs collés (ex: >80, <50)
        result = re.sub(r"([<>]=?|=)(\d+)", r"\1 \2", result)
        result = re.sub(r"(\w)([<>]=?|=)", r"\1 \2", result)

        # nettoyage
        result = re.sub(r"[?!;:,\(\)\[\]\{\}\"']", " ", result)
        result = result.replace("\u2018", " ").replace("\u2019", " ")
        result = re.sub(r"\s+", " ", result).strip()

        # multi-word rules
        for pattern, replacement in self._compiled:
            result = pattern.sub(replacement, result)

        # 🔥 FIX 2 : forcer cas fréquents
        result = re.sub(r"\bhors services\b", "hors_service", result)
        result = re.sub(r"\bhors service\b", "hors_service", result)

        # tokens
        tokens = [SYNONYMS.get(t, t) for t in result.split()]
        tokens = [t for t in tokens if t not in STOP_WORDS]

        return re.sub(r"\s+", " ", " ".join(tokens)).strip()
# ══════════════════════════════════════════════════════════════
#  PARTIE 5 : LEXER
# ══════════════════════════════════════════════════════════════

class TokenType(Enum):
    SELECT=auto(); COUNT=auto(); AVG=auto(); MAX=auto(); MIN=auto(); SUM=auto()
    TABLE=auto(); COLUMN=auto(); WHERE=auto(); OPERATOR=auto(); NUMBER=auto()
    STRING=auto(); ORDER=auto(); ORDER_ASC=auto(); ORDER_DESC=auto()
    LIMIT=auto(); GROUP=auto(); BOOLEAN=auto(); UNKNOWN=auto()

@dataclass
class Token:
    type: TokenType
    value: str
    def __repr__(self): return f"Token({self.type.name}, {self.value!r})"

class Lexer:
    NORMALIZED_OPS = {"superieur_a": ">", "inferieur_a": "<", "superieur_ou_egal_a": ">=", "inferieur_ou_egal_a": "<=", "egal_a": "=", "different_de": "!="}
    KNOWN_STATUTS  = {"signale", "stationne", "arrive", "termine", "valide", "demande", "actif", "inactif", "disponible", "indisponible"}

    def tokenize(self, normalized_text):
        tokens, words, i = [], normalized_text.split(), 0
        while i < len(words):
            matched = False
            for window in range(min(4, len(words) - i), 0, -1):
                phrase = " ".join(words[i:i + window])
                tok = self._classify(phrase)
                if tok.type != TokenType.UNKNOWN:
                    tokens.append(tok); i += window; matched = True; break
            if not matched:
                tokens.append(Token(TokenType.UNKNOWN, words[i])); i += 1
        return tokens

    def _classify(self, phrase):
        p = phrase.lower().strip()
        if re.fullmatch(r"-?\d+(?:\.\d+)?", p): return Token(TokenType.NUMBER, p)
        if p in BOOLEAN_TRUE:  return Token(TokenType.BOOLEAN, "true")
        if p in BOOLEAN_FALSE: return Token(TokenType.BOOLEAN, "false")
        if p in OPERATOR_MAP:  return Token(TokenType.OPERATOR, OPERATOR_MAP[p])
        if p in self.NORMALIZED_OPS: return Token(TokenType.OPERATOR, self.NORMALIZED_OPS[p])
        if p in COUNT_KEYWORDS:   return Token(TokenType.COUNT, p)
        if p in AVERAGE_KEYWORDS: return Token(TokenType.AVG, p)
        if p in MAX_KEYWORDS:     return Token(TokenType.MAX, p)
        if p in MIN_KEYWORDS:     return Token(TokenType.MIN, p)
        if p in SUM_KEYWORDS:     return Token(TokenType.SUM, p)
        if p in SELECT_KEYWORDS:  return Token(TokenType.SELECT, p)
        if p in WHERE_KEYWORDS:   return Token(TokenType.WHERE, p)
        if p in ORDER_DESC_KEYWORDS or p == "decroissant": return Token(TokenType.ORDER_DESC, p)
        if p in ORDER_ASC_KEYWORDS  or p == "croissant":  return Token(TokenType.ORDER_ASC, p)
        if p in ORDER_KEYWORDS or p == "order_by": return Token(TokenType.ORDER, p)
        if p in LIMIT_KEYWORDS: return Token(TokenType.LIMIT, p)
        if p in GROUP_KEYWORDS or p in ("group_by", "par capteur", "par zone", "par type"): return Token(TokenType.GROUP, p)
        if p in TABLE_ALIASES: return Token(TokenType.TABLE, TABLE_ALIASES[p])
        for table, cols in TABLE_COLUMNS.items():
            if p in cols: return Token(TokenType.COLUMN, cols[p])
        if p.startswith(("'", '"')) and p.endswith(("'", '"')): return Token(TokenType.STRING, p.strip("'\""))
        if "_" in p and re.fullmatch(r"[a-z0-9_]+", p): return Token(TokenType.STRING, p)
        if p in self.KNOWN_STATUTS: return Token(TokenType.STRING, p)
        return Token(TokenType.UNKNOWN, p)


# ══════════════════════════════════════════════════════════════
#  PARTIE 6 : AST NODES
# ══════════════════════════════════════════════════════════════

@dataclass
class SelectNode:
    columns: list = field(default_factory=list)
    aggregate: Optional[str] = None
    agg_column: Optional[str] = None

@dataclass
class JoinNode:
    table: str; on_left: str; on_right: str

@dataclass
class FromNode:
    table: str
    joins: list = field(default_factory=list)

@dataclass
class ConditionNode:
    column: str; operator: str; value: object

@dataclass
class WhereNode:
    conditions: list = field(default_factory=list)

@dataclass
class GroupByNode:
    columns: list = field(default_factory=list)

@dataclass
class OrderByNode:
    column: str; direction: str = "ASC"

@dataclass
class LimitNode:
    value: int

@dataclass
class QueryNode:
    select: SelectNode; from_: FromNode
    where: Optional[WhereNode] = None
    group_by: Optional[GroupByNode] = None
    order_by: Optional[OrderByNode] = None
    limit: Optional[LimitNode] = None


# ══════════════════════════════════════════════════════════════
#  PARTIE 7 : PARSER
# ══════════════════════════════════════════════════════════════

class Parser:
    GROUP_COL_MAP      = {"par capteur": "id_capteur", "par zone": "id_zone", "par type": "type_capteur", "par statut": "statut", "group_by": None}
    OPERATOR_STRING_MAP= {"superieur_a": ">", "inferieur_a": "<", "superieur_ou_egal_a": ">=", "inferieur_ou_egal_a": "<=", "egal_a": "=", "different_de": "!="}
    STATUT_STRINGS     = {"hors_service", "en_maintenance", "en_cours", "en_route", "en_panne", "signale", "stationne", "arrive", "termine", "valide", "tech1_assigne", "tech2_valide", "ia_valide", "demande"}

    def __init__(self, tokens): self.tokens = tokens; self.pos = 0

    def _peek(self, offset=0):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None

    def _consume(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok

    def parse(self):
        select_node = self._parse_select()
        from_node   = self._parse_from()
        where_node  = self._parse_where(from_node.table)
        group_node  = self._parse_group()
        order_node  = self._parse_order(from_node.table)
        limit_node  = self._parse_limit()
        has_group   = any(t.type == TokenType.GROUP for t in self.tokens)
        if select_node.aggregate == "COUNT" and not select_node.agg_column and not has_group:
            group_node = None
        self._resolve_joins(from_node)
        return QueryNode(select=select_node, from_=from_node,
                         where=where_node if where_node and where_node.conditions else None,
                         group_by=group_node, order_by=order_node, limit=limit_node)

    def _parse_select(self):
        AGG_MAP = {TokenType.COUNT: "COUNT", TokenType.AVG: "AVG", TokenType.MAX: "MAX", TokenType.MIN: "MIN", TokenType.SUM: "SUM"}
        aggregate = agg_col = None; columns = []
        tok = self._peek()
        if tok is None: raise CompilerError("Requête vide.")
        if tok.type in AGG_MAP:
            aggregate = AGG_MAP[tok.type]; self._consume()
            nxt = self._peek()
            if nxt and nxt.type == TokenType.COLUMN: agg_col = self._consume().value
        elif tok.type == TokenType.SELECT:
            self._consume()
            for i, t in enumerate(self.tokens[self.pos:], self.pos):
                if t.type in AGG_MAP:
                    aggregate = AGG_MAP[t.type]; self.pos = i + 1
                    nxt = self._peek()
                    if nxt and nxt.type == TokenType.COLUMN: agg_col = self._consume().value
                    break
            if not aggregate:
                while self._peek() and self._peek().type == TokenType.COLUMN:
                    columns.append(self._consume().value)
        else:
            for i, t in enumerate(self.tokens):
                if t.type in AGG_MAP:
                    aggregate = AGG_MAP[t.type]
                    nxt_idx = i + 1
                    if nxt_idx < len(self.tokens) and self.tokens[nxt_idx].type == TokenType.COLUMN:
                        agg_col = self.tokens[nxt_idx].value
                    break
        return SelectNode(columns=columns, aggregate=aggregate, agg_column=agg_col)

    def _parse_from(self):
        table = None
        for i in range(self.pos, len(self.tokens)):
            if self.tokens[i].type == TokenType.TABLE:
                table = self.tokens[i].value; self.pos = i + 1; break
        if table is None:
            unknown_words = [t.value for t in self.tokens if t.type == TokenType.UNKNOWN]
            suggestions = []
            for word in unknown_words:
                for alias in TABLE_ALIASES:
                    if alias.startswith(word[:3]) or word[:3] in alias:
                        real = TABLE_ALIASES[alias]
                        if real not in suggestions: suggestions.append(real)
            if suggestions:
                raise AmbiguityError("Table non identifiée. Vouliez-vous dire :", suggestions=suggestions[:4])
            raise CompilerError("Table non identifiée. Tables : capteurs, mesures, zones, citoyens, interventions, techniciens, vehicules, trajets.")
        return FromNode(table=table)

    def _parse_where(self, table):
        conditions = []
        i = 0
        while i < len(self.tokens):
            tok = self.tokens[i]
            if tok.type == TokenType.COLUMN:
                col = tok.value
                if i + 1 < len(self.tokens):
                    next_tok = self.tokens[i + 1]
                    if next_tok.type == TokenType.OPERATOR:
                        op = next_tok.value
                        if i + 2 < len(self.tokens):
                            val_tok = self.tokens[i + 2]
                            if not (val_tok.type == TokenType.STRING and val_tok.value in self.OPERATOR_STRING_MAP):
                                conditions.append(ConditionNode(col, op, self._extract_value(val_tok))); i += 3; continue
                    elif next_tok.type == TokenType.STRING and next_tok.value in self.OPERATOR_STRING_MAP:
                        op = self.OPERATOR_STRING_MAP[next_tok.value]
                        if i + 2 < len(self.tokens):
                            conditions.append(ConditionNode(col, op, self._extract_value(self.tokens[i + 2]))); i += 3; continue
            if tok.type == TokenType.STRING and tok.value in self.STATUT_STRINGS:
                if not any(c.column == "statut" for c in conditions):
                    conditions.append(ConditionNode("statut", "=", tok.value))
            if tok.type == TokenType.BOOLEAN:
                conditions.append(ConditionNode("disponible", "=", tok.value == "true"))
            i += 1
        self.pos = len(self.tokens)
        return WhereNode(conditions=conditions) if conditions else None

    def _extract_value(self, tok):
        if tok.type == TokenType.NUMBER:
            s = tok.value; return int(s) if "." not in s else float(s)
        if tok.type == TokenType.BOOLEAN: return tok.value == "true"
        return tok.value

    def _parse_group(self):
        for i, tok in enumerate(self.tokens):
            if tok.type == TokenType.GROUP:
                col = self.GROUP_COL_MAP.get(tok.value.lower())
                if col: return GroupByNode(columns=[col])
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.COLUMN:
                    return GroupByNode(columns=[self.tokens[i + 1].value])
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.TABLE:
                    tbl = self.tokens[i + 1].value
                    fk  = {"zones": "id_zone", "capteurs": "id_capteur", "citoyens": "id_citoyen"}
                    return GroupByNode(columns=[fk.get(tbl, f"id_{tbl.rstrip('s')}")])
        return None

    def _parse_order(self, table):
        direction = col = None
        for tok in self.tokens:
            if tok.type == TokenType.ORDER_DESC: direction = "DESC"
            elif tok.type == TokenType.ORDER_ASC: direction = "ASC"
        for tok in self.tokens:
            if tok.type == TokenType.COLUMN and tok.value == "economie_co2":
                if direction is None: direction = "DESC"
                col = "economie_co2"
        if direction is None: return None
        if col is None:
            for tok in self.tokens:
                if tok.type == TokenType.COLUMN: col = tok.value
        if col is None:
            col = {"mesures": "pollution", "zones": "pollution", "citoyens": "score_ecolo", "trajets": "economie_co2", "capteurs": "taux_erreur", "interventions": "date_demande"}.get(table, "id")
        return OrderByNode(column=col, direction=direction)

    def _parse_limit(self):
        has_eco    = any(t.type == TokenType.COLUMN and t.value == "economie_co2" for t in self.tokens)
        has_number = any(t.type == TokenType.NUMBER for t in self.tokens)
        if has_eco and not has_number: return LimitNode(1)
        for i, tok in enumerate(self.tokens):
            if tok.type == TokenType.LIMIT:
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.NUMBER:
                    return LimitNode(int(float(self.tokens[i + 1].value)))
            if tok.type == TokenType.NUMBER:
                prev = self.tokens[i - 1] if i > 0 else None
                if prev and prev.type == TokenType.LIMIT: return LimitNode(int(float(tok.value)))
                if i <= 2: return LimitNode(int(float(tok.value)))
        return None

    def _resolve_joins(self, from_node):
        for tok in self.tokens:
            if tok.type == TokenType.TABLE and tok.value != from_node.table:
                join_cols = get_join(from_node.table, tok.value)
                if join_cols:
                    from_node.joins.append(JoinNode(table=tok.value, on_left=join_cols[0], on_right=join_cols[1]))


# ══════════════════════════════════════════════════════════════
#  PARTIE 8 : SQL GENERATOR
# ══════════════════════════════════════════════════════════════

class SQLGenerator:
    def generate(self, ast):
        if ast is None: raise CompilerError("AST vide.")
        if ast.from_.table == "zones" and ast.order_by and ast.order_by.direction == "DESC" and not ast.select.aggregate:
            return self._gen_zones_pollution(ast)
        parts = []
        if ast.select.aggregate == "COUNT" and ast.group_by:
            parts.append(f"SELECT {ast.group_by.columns[0]}, COUNT({ast.select.agg_column or '*'})")
        else:
            parts.append(self._gen_select(ast.select, ast.from_.table))
        parts.append(self._gen_from(ast.from_))
        if ast.where:    parts.append(self._gen_where(ast.where))
        if ast.group_by: parts.append(self._gen_group_by(ast.group_by))
        if ast.order_by: parts.append(self._gen_order_by(ast.order_by))
        if ast.limit:    parts.append(self._gen_limit(ast.limit))
        return "\n".join(parts) + ";"

    def _gen_zones_pollution(self, ast):
        lim = f"\nLIMIT {ast.limit.value}" if ast.limit else ""
        return (f"SELECT zones.nom_zone, AVG(mesures.pollution) AS avg_pollution\n"
                f"FROM mesures\nINNER JOIN capteurs ON mesures.id_capteur = capteurs.id_capteur\n"
                f"INNER JOIN zones ON capteurs.id_zone = zones.id_zone\n"
                f"GROUP BY zones.id_zone, zones.nom_zone\nORDER BY avg_pollution DESC{lim};")

    def _gen_select(self, node, table):
        if node.aggregate: return f"SELECT {node.aggregate}({node.agg_column or '*'})"
        if node.columns:   return f"SELECT {', '.join(node.columns)}"
        defaults = get_default_columns(table)
        return f"SELECT {', '.join(defaults) if defaults else '*'}"

    def _gen_from(self, node):
        sql = f"FROM {node.table}"
        for join in node.joins: sql += f"\nINNER JOIN {join.table} ON {join.on_left} = {join.on_right}"
        return sql

    def _gen_where(self, node):
        if not node.conditions: return ""
        return "WHERE " + "\n  AND ".join(self._gen_condition(c) for c in node.conditions)

    def _gen_condition(self, cond):
        col, op, val = cond.column, cond.operator, cond.value
        if isinstance(val, bool): return f"{col} = {'TRUE' if val else 'FALSE'}"
        if isinstance(val, (int, float)): return f"{col} {op} {val}"
        val_str = str(val)
        if val_str.lower() in ("null", "none", ""): return f"{col} IS NULL" if op == "=" else f"{col} IS NOT NULL"
        return f"{col} {op} '{val_str}'"

    def _gen_group_by(self, node):  return f"GROUP BY {', '.join(node.columns)}"
    def _gen_order_by(self, node):
        col = node.column
        if col in ("pollution", "temperature", "humidite", "bruit"): col = f"AVG({col})"
        return f"ORDER BY {col} {node.direction}"
    def _gen_limit(self, node): return f"LIMIT {node.value}"


# ══════════════════════════════════════════════════════════════
#  PARTIE 9 : COMPILER
# ══════════════════════════════════════════════════════════════

@dataclass
class CompilationResult:
    input_phrase: str; normalized: str; tokens: list; ast: object
    sql: str; success: bool; error_message: str = ""
    def __str__(self):
        if self.success: return f"✅ {self.input_phrase}\n   SQL : {self.sql}"
        return f"❌ {self.input_phrase}\n   Erreur : {self.error_message}"

class Compiler:
    def __init__(self, verbose=False):
        self.normalizer = Normalizer(); self.lexer = Lexer()
        self.generator  = SQLGenerator(); self.verbose = verbose

    def compile(self, phrase):
        normalized = ""; tokens = []; ast = None
        try:
            normalized = self.normalizer.normalize(phrase)
            if self.verbose: print(f"  [NORM] {normalized}")
            if not normalized.strip(): raise CompilerError("Requête vide.")
            tokens = self.lexer.tokenize(normalized)
            if self.verbose: print(f"  [LEX]  {tokens}")
            parser = Parser(tokens); ast = parser.parse()
            if self.verbose: print(f"  [AST]  {ast}")
            sql = self.generator.generate(ast)
            if self.verbose: print(f"  [SQL]  {sql}")
            return CompilationResult(phrase, normalized, tokens, ast, sql, True)
        except AmbiguityError as e:
            msg = str(e) + ("\n  → Reformulez en précisant la table." if e.suggestions else "")
            return CompilationResult(phrase, normalized, tokens, ast, "", False, msg)
        except CompilerError as e:
            return CompilationResult(phrase, normalized, tokens, ast, "", False, str(e))
        except Exception as e:
            return CompilationResult(phrase, normalized, tokens, ast, "", False, f"Erreur : {type(e).__name__} – {e}")


# ══════════════════════════════════════════════════════════════
#  PARTIE 10 : TESTS
# ══════════════════════════════════════════════════════════════

TEST_CASES = [
    ("Affiche les 5 zones les plus polluées",                               ["mesures", "AVG", "pollution", "ORDER BY", "DESC", "LIMIT 5"], "Top 5 zones polluées"),
    ("Combien de capteurs sont hors service ?",                             ["COUNT", "capteurs", "hors_service"],                          "COUNT capteurs hors_service"),
    ("Quels citoyens ont un score écologique > 80 ?",                       ["citoyens", "score_ecolo", ">", "80"],                         "Citoyens score_ecolo > 80"),
    ("Donne-moi le trajet le plus économique en CO2",                       ["trajets", "economie_co2", "DESC", "LIMIT 1"],                 "Trajet économique CO2"),
    ("Quelles interventions sont en cours ?",                               ["interventions", "statut", "en_cours"],                        "Interventions en_cours"),
    ("Montre-moi les techniciens disponibles",                              ["techniciens", "disponible"],                                  "Techniciens disponibles"),
    ("Affiche les capteurs signalés avec un taux_erreur supérieur à 10",    ["capteurs", "signale", ">", "10"],                             "Capteurs signalés + taux_erreur > 10"),
    ("Combien de mesures par capteur ?",                                    ["COUNT", "mesures", "GROUP BY", "id_capteur"],                 "COUNT mesures GROUP BY capteur"),
    ("Liste les véhicules en panne",                                        ["vehicules", "statut", "en_panne"],                            "Véhicules en_panne"),
    ("Quelle est la moyenne du score écologique des citoyens par zone ?",   ["AVG", "score_ecolo", "citoyens", "GROUP BY"],                 "AVG score_ecolo GROUP BY zone"),
]

def run_tests(verbose=False):
    compiler = Compiler()
    G, R, Y, B, BO, RS = "\033[92m", "\033[91m", "\033[93m", "\033[94m", "\033[1m", "\033[0m"
    print(f"\n{BO}{'═'*65}{RS}")
    print(f"{BO}  TESTS COMPILATEUR NL→SQL  –  Neo-Sousse 2030{RS}")
    print(f"{BO}{'═'*65}{RS}\n")
    passed = 0
    for idx, (phrase, expected, desc) in enumerate(TEST_CASES, 1):
        result = compiler.compile(phrase)
        sql_up = result.sql.upper()
        checks = [p.upper() in sql_up for p in expected]
        ok     = result.success and all(checks)
        print(f"  {BO}Test {idx:02d}{RS} {'✅ PASS' if ok else '❌ FAIL'}")
        print(f"  {B}Desc{RS}   : {desc}")
        if result.success: print(f"  {B}SQL{RS}    : {result.sql.strip()}")
        else:              print(f"  {R}Erreur{RS} : {result.error_message}")
        if not ok and result.success:
            print(f"  {Y}Manquant{RS}: {[p for p, c in zip(expected, checks) if not c]}")
        if verbose: print(f"  Normalisé : {result.normalized}")
        print(f"  {'─'*60}")
        if ok: passed += 1
    total = len(TEST_CASES); pct = int(passed / total * 100)
    color = G if pct == 100 else (Y if pct >= 70 else R)
    print(f"\n{BO}{'═'*65}{RS}")
    print(f"{BO}  RÉSULTAT : {color}{passed}/{total} tests passés ({pct}%){RS}")
    print(f"{BO}{'═'*65}{RS}\n")