"""
Reporting and data export module.
Generates structured CSV exports and downloadable PDF analytical summaries using ReportLab.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import io
import pandas as pd

from src.config import REPORTS_DIR


def export_dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """
    Serialize DataFrame to CSV bytes with UTF-8 encoding.
    """
    return df.to_csv(index=False, encoding="utf-8").encode("utf-8")


def generate_pdf_report(
    summary_kpis: Dict[str, any],
    cluster_profiles: Optional[pd.DataFrame] = None,
    model_metadata: Optional[Dict[str, any]] = None,
    insights: Optional[List[str]] = None
) -> bytes:
    """
    Build a PDF executive analytics report using ReportLab.
    Falls back gracefully if ReportLab is not available.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#E23744")
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748B")
        )
        section_style = ParagraphStyle(
            "ReportSection",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0B0E14"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1E293B")
        )
        
        story = []
        
        # 1. Header
        story.append(Paragraph("Zomato Restaurant Intelligence Platform", title_style))
        story.append(Paragraph("Executive Market Analytics & Cost Clustering Report • Author: Priya Sharma", subtitle_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        story.append(Spacer(1, 14))
        
        # 2. Executive KPIs Table
        story.append(Paragraph("1. Executive Market Summary", section_style))
        kpi_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Restaurants", str(summary_kpis.get("total_restaurants", "N/A")), "Avg Dining Cost (2)", f"INR {summary_kpis.get('avg_cost', 0):,.0f}"],
            ["Median Dining Cost", f"INR {summary_kpis.get('median_cost', 0):,.0f}", "Avg Customer Rating", f"{summary_kpis.get('avg_rating', 0.0):.2f} / 5.0"],
            ["Total Cuisines", str(summary_kpis.get("total_cuisines", "N/A")), "Active Localities", str(summary_kpis.get("total_localities", "N/A"))]
        ]
        kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))
        
        # 3. Model Metadata
        if model_metadata:
            story.append(Paragraph("2. Machine Learning Model Specifications", section_style))
            mod_data = [["Parameter", "Configured Value"]]
            for k, v in model_metadata.items():
                mod_data.append([str(k).replace("_", " ").title(), str(v)])
            mod_table = Table(mod_data, colWidths=[200, 320])
            mod_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(mod_table)
            story.append(Spacer(1, 14))
            
        # 4. Cluster Profiles
        if cluster_profiles is not None and not cluster_profiles.empty:
            story.append(Paragraph("3. Discovered Cluster Profiles", section_style))
            cols_to_use = [c for c in ["Segment Name", "Restaurant Count", "Mean Cost (INR)", "Avg Rating", "Top Cuisines"] if c in cluster_profiles.columns]
            sub_df = cluster_profiles[cols_to_use]
            cluster_table_data = [cols_to_use]
            for _, row in sub_df.iterrows():
                cluster_table_data.append([str(val) for val in row.values])
                
            cl_table = Table(cluster_table_data, colWidths=[120, 70, 80, 70, 180])
            cl_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E23744")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(cl_table)
            story.append(Spacer(1, 14))
            
        # 5. Strategic Insights
        if insights:
            story.append(Paragraph("4. Data-Driven Strategic Findings", section_style))
            for item in insights:
                story.append(Paragraph(f"• {item}", body_style))
                story.append(Spacer(1, 4))
                
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        # Fallback to plain text if ReportLab encounters any issues
        fallback_text = (
            f"Zomato Restaurant Intelligence Platform Report\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Author: Priya Sharma\n\n"
            f"Summary KPIs:\n{summary_kpis}\n\n"
            f"Model Metadata:\n{model_metadata}\n\n"
            f"Insights:\n" + "\n".join(insights or [])
        )
        return fallback_text.encode("utf-8")
