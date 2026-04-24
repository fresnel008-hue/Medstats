from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import io


def generer_pdf(user, donnees, stats):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Styles personnalisés
    titre_style = ParagraphStyle(
        'titre',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=5
    )

    sous_titre_style = ParagraphStyle(
        'sous_titre',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333'),
        spaceBefore=15,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        'normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#444'),
        spaceAfter=5
    )

    # ===== EN-TETE =====
    elements.append(Paragraph("MedStats", titre_style))
    elements.append(Paragraph("Rapport de Santé Personnel", sous_titre_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#667eea')))
    elements.append(Spacer(1, 15))

    # Infos utilisateur
    elements.append(Paragraph(f"<b>Utilisateur :</b> {user.username}", normal_style))
    elements.append(Paragraph(f"<b>Email :</b> {user.email}", normal_style))
    elements.append(Paragraph(f"<b>Date du rapport :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
    elements.append(Paragraph(f"<b>Nombre de collectes :</b> {len(donnees)}", normal_style))
    elements.append(Spacer(1, 20))

    if stats and donnees:

        # ===== STATISTIQUES DESCRIPTIVES =====
        elements.append(Paragraph("📊 Statistiques Descriptives", section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
        elements.append(Spacer(1, 10))

        stats_data = [
            ["Indicateur", "Moyenne", "Médiane", "Écart-type", "Min", "Max"],
            [
                "IMC",
                str(stats["imc_moyen"]),
                "-",
                str(stats["imc_std"]),
                str(stats["imc_min"]),
                str(stats["imc_max"])
            ],
            [
                "Stress (1-5)",
                str(stats["stress_moyen"]),
                str(stats["stress_median"]),
                str(stats["stress_std"]),
                str(stats["stress_min"]),
                str(stats["stress_max"])
            ],
            [
                "Sommeil (h)",
                str(stats["sommeil_moyen"]),
                str(stats["sommeil_median"]),
                str(stats["sommeil_std"]),
                str(stats["sommeil_min"]),
                str(stats["sommeil_max"])
            ],
            [
                "Fréq. Cardiaque",
                str(stats["fc_moyenne"]),
                "-", "-", "-", "-"
            ],
            [
                "Eau (verres)",
                str(stats["eau_moyenne"]),
                "-", "-", "-", "-"
            ],
            [
                "Activité (min)",
                str(stats["activite_moyenne"]),
                "-", "-", "-", "-"
            ],
        ]

        table_stats = Table(stats_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm])
        table_stats.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table_stats)
        elements.append(Spacer(1, 20))

        # ===== TENDANCES =====
        elements.append(Paragraph("📈 Tendances", section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
        elements.append(Spacer(1, 10))

        def fleche(tendance):
            if tendance == "hausse":
                return "↑ En hausse"
            elif tendance == "baisse":
                return "↓ En baisse"
            return "→ Stable"

        tendances_data = [
            ["Indicateur", "Tendance", "Corrélation Stress/Sommeil"],
            ["Stress", fleche(stats["tendance_stress"]), f"{stats['correlation_stress_sommeil']}"],
            ["Sommeil", fleche(stats["tendance_sommeil"]), ""],
            ["Humeur", fleche(stats["tendance_humeur"]), ""],
        ]

        table_tendances = Table(tendances_data, colWidths=[5*cm, 4*cm, 6*cm])
        table_tendances.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')]),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('SPAN', (2, 1), (2, 3)),
        ]))
        elements.append(table_tendances)
        elements.append(Spacer(1, 20))

        # ===== HISTORIQUE =====
        elements.append(Paragraph("📋 Historique des collectes", section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
        elements.append(Spacer(1, 10))

        historique = [["Date", "IMC", "Stress", "Sommeil", "Humeur", "Énergie", "FC"]]
        for d in donnees[:20]:  # Max 20 lignes
            historique.append([
                d.date.strftime('%d/%m/%Y'),
                str(d.imc),
                f"{d.niveau_stress}/5",
                f"{d.heures_sommeil}h",
                f"{d.niveau_humeur}/5",
                f"{d.niveau_energie}/5",
                str(d.frequence_cardiaque)
            ])

        table_hist = Table(historique, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm])
        table_hist.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table_hist)

    else:
        elements.append(Paragraph("Aucune donnée collectée.", normal_style))

    # ===== PIED DE PAGE =====
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ddd')))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"<i>Rapport généré automatiquement par MedStats — {datetime.now().strftime('%d/%m/%Y')}</i>",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer