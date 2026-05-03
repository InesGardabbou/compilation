import io
import re
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from services.ia_generative import MoteurIA, TypeRapport

router = APIRouter(prefix="/ia", tags=["IA"])
ia = MoteurIA()


# ══════════════════════════════════════════════════════════════
#  UTILITAIRE : nettoyage texte pour ReportLab
# ══════════════════════════════════════════════════════════════

# Mapping émojis → texte court (ReportLab/Helvetica ne supporte pas Unicode étendu)
_EMOJI_MAP = {
    "📊": "[KPI]", "📈": "[EVOL]", "📉": "[BAISSE]", "📋": "[LISTE]",
    "📄": "[DOC]",  "📡": "[CAPTEUR]", "🔧": "[OUTIL]", "🔴": "[CRITIQUE]",
    "🟠": "[ELEVE]","🟡": "[MODERE]", "🟢": "[OK]",    "⚪": "[?]",
    "✅": "[OK]",   "⚠️": "[ALERTE]", "❌": "[ERREUR]","💡": "[RECO]",
    "🚗": "[VEHIC]","🚘": "[FLOTTE]", "🌱": "[ECO]",   "🏆": "[TOP]",
    "👥": "[CITOY]","🤖": "[IA]",     "🔑": "[CLE]",   "🏙️": "",
    "═": "=",       "—": "-",         "→": "->",        "•": "-",
    "\u2713": "OK", "\u26a0": "!",    "\u2019": "'",    "\u00b5": "ug",
}

def _clean(text: str) -> str:
    """Retire/remplace les caractères non supportés par Helvetica."""
    if not text:
        return ""
    # Appliquer le mapping
    for emoji, replacement in _EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    # Supprimer tout caractère hors Latin-1 restant (émojis non mappés)
    text = text.encode("latin-1", errors="ignore").decode("latin-1")
    # Échapper les caractères XML spéciaux pour ReportLab
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.strip()


# ══════════════════════════════════════════════════════════════
#  REQUEST SCHEMA
# ══════════════════════════════════════════════════════════════

class PdfRapportRequest(BaseModel):
    type: str = "complet"


# ══════════════════════════════════════════════════════════════
#  COULEURS & STYLES
# ══════════════════════════════════════════════════════════════

HEADER_BG    = colors.HexColor("#1a3c5e")
LIGHT_BG     = colors.HexColor("#eaf1f8")
LIGHTER_BG   = colors.HexColor("#f5f9fc")
BORDER_COLOR = colors.HexColor("#dde3ea")

SEV_COLORS = {
    "critique": colors.HexColor("#c0392b"),
    "elevee":   colors.HexColor("#e67e22"),
    "moderee":  colors.HexColor("#f1c40f"),
    "faible":   colors.HexColor("#27ae60"),
}
PRIO_COLORS = {
    "critique": colors.HexColor("#c0392b"),
    "elevee":   colors.HexColor("#e67e22"),
    "moderee":  colors.HexColor("#f39c12"),
    "faible":   colors.HexColor("#27ae60"),
}

def _sev_color(sev: str):
    return SEV_COLORS.get(sev.lower().replace("é","e").replace("è","e"), colors.grey)

def _prio_color(prio: str):
    return PRIO_COLORS.get(prio.lower().replace("é","e").replace("è","e"), colors.grey)


def _styles():
    s = getSampleStyleSheet()

    def safe_add(name, **kwargs):
        """Ajoute un style seulement s'il n'existe pas"""
        if name not in s:
            s.add(ParagraphStyle(name=name, **kwargs))

    safe_add(
        "CoverTitle",
        fontSize=26, leading=32, alignment=TA_CENTER,
        textColor=colors.HexColor("#1a3c5e"),
        fontName="Helvetica-Bold", spaceAfter=6
    )

    safe_add(
        "CoverSub",
        fontSize=13, leading=18, alignment=TA_CENTER,
        textColor=colors.HexColor("#4a7fa5"),
        fontName="Helvetica", spaceAfter=4
    )

    safe_add(
        "SecTitle",
        fontSize=12, leading=16, alignment=TA_LEFT,
        textColor=colors.white,
        fontName="Helvetica-Bold", spaceAfter=4
    )

    safe_add(
        "Body",
        fontSize=9, leading=13, alignment=TA_LEFT,
        textColor=colors.HexColor("#333333"),
        fontName="Helvetica", spaceAfter=3
    )

    # ✅ IMPORTANT : renommé pour éviter conflit
    safe_add(
        "BulletCustom",
        fontSize=9, leading=13, alignment=TA_LEFT,
        textColor=colors.HexColor("#333333"),
        fontName="Helvetica", spaceAfter=2,
        leftIndent=14
    )

    safe_add(
        "TableHdr",
        fontSize=8, leading=11, alignment=TA_CENTER,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )

    safe_add(
        "TableCell",
        fontSize=8, leading=12, alignment=TA_LEFT,
        textColor=colors.HexColor("#333333"),
        fontName="Helvetica"
    )

    safe_add(
        "KpiLabel",
        fontSize=8, leading=11, alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        fontName="Helvetica"
    )

    safe_add(
        "KpiValue",
        fontSize=16, leading=20, alignment=TA_CENTER,
        textColor=colors.HexColor("#1a3c5e"),
        fontName="Helvetica-Bold"
    )

    safe_add(
        "Footer",
        fontSize=7, leading=10, alignment=TA_CENTER,
        textColor=colors.HexColor("#888888"),
        fontName="Helvetica"
    )

    return s


# ══════════════════════════════════════════════════════════════
#  COMPOSANTS PDF
# ══════════════════════════════════════════════════════════════

def _section(title: str, S):
    t = Table([[Paragraph(_clean(title), S["SecTitle"])]], colWidths=[18*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HEADER_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ]))
    return t


def _kpis(kpis: dict, S):
    items = [
        (_clean(k.replace("_", " ").title()), _clean(str(v)))
        for k, v in kpis.items()
        if not isinstance(v, dict)
    ][:8]
    if not items:
        return None
    rows = []
    for i in range(0, len(items), 4):
        chunk = items[i:i+4]
        while len(chunk) < 4:
            chunk.append(("", ""))
        rows.append([Paragraph(lbl, S["KpiLabel"]) for lbl, _ in chunk])
        rows.append([Paragraph(val, S["KpiValue"]) for _, val in chunk])
    t = Table(rows, colWidths=[4.5*cm]*4)
    t.setStyle(TableStyle([
        ("ALIGN",          (0,0), (-1,-1), "CENTER"),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("GRID",           (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT_BG, LIGHTER_BG]),
        ("TOPPADDING",     (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 6),
    ]))
    return t


def _table_anomalies(anomalies: list, S):
    if not anomalies:
        return Paragraph("Aucune anomalie detectee.", S["Body"])

    col_w   = [2.2*cm, 2.5*cm, 1.8*cm, 6*cm, 5.5*cm]
    headers = ["Entite", "Identifiant", "Severite", "Message", "Recommandation"]
    rows    = [[Paragraph(f"<b>{h}</b>", S["TableHdr"]) for h in headers]]
    cmds    = [
        ("BACKGROUND",    (0,0), (-1,0), HEADER_BG),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LIGHTER_BG]),
    ]
    for i, a in enumerate(anomalies, start=1):
        if isinstance(a, dict):
            entite = _clean(a.get("entite",""))
            ident  = _clean(str(a.get("identifiant","")))
            sev    = a.get("severite","faible")
            msg    = _clean(a.get("message",""))
            reco   = _clean(a.get("recommandation",""))
        else:
            entite = _clean(a.entite)
            ident  = _clean(str(a.identifiant))
            sev    = a.severite
            msg    = _clean(a.message)
            reco   = _clean(a.recommandation)

        rows.append([
            Paragraph(entite,      S["TableCell"]),
            Paragraph(ident,       S["TableCell"]),
            Paragraph(sev.upper(), S["TableCell"]),
            Paragraph(msg,         S["TableCell"]),
            Paragraph(reco,        S["TableCell"]),
        ])
        cmds += [
            ("TEXTCOLOR", (2,i), (2,i), _sev_color(sev)),
            ("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"),
        ]

    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return t


def _table_suggestions(suggestions: list, S):
    if not suggestions:
        return Paragraph("Aucune action urgente requise.", S["Body"])

    col_w   = [2*cm, 3*cm, 5.5*cm, 5.5*cm, 2*cm]
    headers = ["Priorite", "Entite", "Message", "Action", "Delai"]
    rows    = [[Paragraph(f"<b>{h}</b>", S["TableHdr"]) for h in headers]]
    cmds    = [
        ("BACKGROUND",    (0,0), (-1,0), HEADER_BG),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LIGHTER_BG]),
    ]
    for i, s in enumerate(suggestions, start=1):
        prio = s.get("priorite","faible")
        rows.append([
            Paragraph(_clean(prio.upper()),        S["TableCell"]),
            Paragraph(_clean(s.get("entite","")),  S["TableCell"]),
            Paragraph(_clean(s.get("message","")), S["TableCell"]),
            Paragraph(_clean(s.get("action","")),  S["TableCell"]),
            Paragraph(_clean(s.get("delai","")),   S["TableCell"]),
        ])
        cmds += [
            ("TEXTCOLOR", (0,i), (0,i), _prio_color(prio)),
            ("FONTNAME",  (0,i), (0,i), "Helvetica-Bold"),
        ]

    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return t


def _table_recommandations(recommandations: list, S):
    if not recommandations:
        return Paragraph("Aucune recommandation.", S["Body"])

    col_w   = [2.5*cm, 7*cm, 5.5*cm, 3*cm]
    headers = ["Priorite", "Action", "Impact", "Delai"]
    rows    = [[Paragraph(f"<b>{h}</b>", S["TableHdr"]) for h in headers]]
    cmds    = [
        ("BACKGROUND",    (0,0), (-1,0), HEADER_BG),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LIGHTER_BG]),
    ]
    for i, r in enumerate(recommandations, start=1):
        prio = r.get("priorite","faible")
        rows.append([
            Paragraph(_clean(prio.upper()),       S["TableCell"]),
            Paragraph(_clean(r.get("action","")), S["TableCell"]),
            Paragraph(_clean(r.get("impact","")), S["TableCell"]),
            Paragraph(_clean(r.get("delai","")),  S["TableCell"]),
        ])
        cmds += [
            ("TEXTCOLOR", (0,i), (0,i), _prio_color(prio)),
            ("FONTNAME",  (0,i), (0,i), "Helvetica-Bold"),
        ]

    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return t


# ══════════════════════════════════════════════════════════════
#  CONSTRUCTION DU PDF
# ══════════════════════════════════════════════════════════════

def _construire_pdf(rapport, suggestions: list) -> bytes:
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm,    bottomMargin=2*cm,
        title=f"Rapport {rapport.type_rapport}",
        author="MoteurIA v2.0",
    )
    S     = _styles()
    story = []

    # ── 1. COUVERTURE ────────────────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Smart City Neo-Sousse 2030", S["CoverTitle"]))
    story.append(Paragraph(
        f"Rapport IA - {_clean(rapport.type_rapport.upper().replace('_', ' '))}",
        S["CoverSub"],
    ))
    story.append(Paragraph(f"Genere le : {_clean(rapport.genere_le)}", S["CoverSub"]))
    story.append(Paragraph(f"Periode   : {_clean(rapport.periode)}",   S["CoverSub"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=HEADER_BG))
    story.append(Spacer(1, 0.4*cm))

    score = rapport.score_global
    score_color = (
        colors.HexColor("#27ae60") if score >= 70
        else colors.HexColor("#e67e22") if score >= 40
        else colors.HexColor("#c0392b")
    )
    badge = Table([[
        Paragraph("Score Global", S["KpiLabel"]),
        Paragraph(f"{score}/100", ParagraphStyle(
            "SC", fontSize=22, leading=26, alignment=TA_CENTER,
            textColor=score_color, fontName="Helvetica-Bold",
        )),
        Paragraph("Moteur IA", S["KpiLabel"]),
        Paragraph(_clean(rapport.moteur), S["KpiLabel"]),
    ]], colWidths=[3*cm, 3.5*cm, 2.5*cm, 9*cm])
    badge.setStyle(TableStyle([
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND",   (0,0), (-1,-1), LIGHT_BG),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
    ]))
    story.append(badge)
    story.append(Spacer(1, 0.6*cm))

    # ── 2. RÉSUMÉ ────────────────────────────────────────────
    story.append(_section("Resume Executif", S))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(_clean(rapport.resume), S["Body"]))
    story.append(Spacer(1, 0.5*cm))

    # ── 3. KPIs ──────────────────────────────────────────────
    story.append(_section("Indicateurs Cles de Performance", S))
    story.append(Spacer(1, 0.3*cm))
    kpi_t = _kpis(rapport.kpis, S)
    if kpi_t:
        story.append(kpi_t)
    story.append(Spacer(1, 0.5*cm))

    # ── 4. DÉTAILS ───────────────────────────────────────────
    story.append(_section("Analyse Detaillee", S))
    story.append(Spacer(1, 0.2*cm))
    for line in rapport.details.split("\n"):
        line_clean = _clean(line.strip())
        if not line_clean:
            story.append(Spacer(1, 0.1*cm))
        elif line.strip().startswith(("•", "-", "*", "  •")):
            story.append(Paragraph(f"- {line_clean.lstrip('-').strip()}", S["BulletCustom"]))
        elif line.strip().startswith("="):
            story.append(HRFlowable(width="100%", thickness=0.8,
                                    color=colors.HexColor("#aec6cf")))
        else:
            story.append(Paragraph(line_clean, S["Body"]))
    story.append(Spacer(1, 0.5*cm))

    # ── 5. RECOMMANDATIONS ───────────────────────────────────
    story.append(_section(f"Recommandations ({len(rapport.recommandations)})", S))
    story.append(Spacer(1, 0.3*cm))
    story.append(_table_recommandations(rapport.recommandations, S))
    story.append(Spacer(1, 0.5*cm))

    # ── 6. ANOMALIES (nouvelle page) ─────────────────────────
    story.append(PageBreak())
    story.append(_section(f"Anomalies Detectees ({len(rapport.anomalies)})", S))
    story.append(Spacer(1, 0.3*cm))
    story.append(_table_anomalies(rapport.anomalies, S))
    story.append(Spacer(1, 0.7*cm))

    # ── 7. SUGGESTIONS ───────────────────────────────────────
    story.append(_section(f"Suggestions d'Actions IA ({len(suggestions)})", S))
    story.append(Spacer(1, 0.3*cm))
    story.append(_table_suggestions(suggestions, S))
    story.append(Spacer(1, 0.7*cm))

    # ── Pied de page ─────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#aec6cf")))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Document genere par {_clean(rapport.moteur)} | "
        f"Neo-Sousse Smart City Platform | {_clean(rapport.genere_le)}",
        S["Footer"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ══════════════════════════════════════════════════════════════
#  ROUTE   POST /ia/rapport/pdf
# ══════════════════════════════════════════════════════════════

@router.post(
    "/rapport/pdf",
    response_class=StreamingResponse,
    summary="Generer un rapport PDF (generer_rapport + suggerer_actions)",
    responses={200: {"content": {"application/pdf": {}}}},
)
def rapport_pdf(req: PdfRapportRequest):
    try:
        rapport     = ia.generer_rapport(req.type)
        suggestions = ia.suggerer_actions()
        pdf_bytes   = _construire_pdf(rapport, suggestions)

        filename = f"rapport_{req.type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        traceback.print_exc()   # affiche le détail complet dans le terminal
        raise HTTPException(status_code=500, detail=str(e))