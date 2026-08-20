import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_resume_pdf(resume_data: Dict[str, Any]) -> bytes:
    """
    Generate professional, machine-readable ATS PDF using ReportLab with horizontal section divider lines.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_LEFT
    )
    
    contact_style = ParagraphStyle(
        'DocContact',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        alignment=TA_LEFT
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=3,
        alignment=TA_LEFT
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_LEFT
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        leftIndent=12,
        firstLineIndent=-8,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_LEFT
    )

    story = []

    personal = resume_data.get("personal_info", {})
    name = personal.get("name") or "CANDIDATE NAME"
    role = personal.get("target_role") or "SOFTWARE ENGINEER"
    email = personal.get("email", "")
    phone = personal.get("phone", "")
    location = personal.get("location", "")
    linkedin = personal.get("linkedin", "")
    github = personal.get("github", "")

    # Header Name
    story.append(Paragraph(name.upper(), title_style))
    story.append(Spacer(1, 2))

    # Contact & Links line
    contact_bits = [p for p in [role, email, phone, location, linkedin, github] if p]
    if contact_bits:
        story.append(Paragraph(" • ".join(contact_bits), contact_style))

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceBefore=2, spaceAfter=8))

    def add_section_divider():
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=6, spaceAfter=6))

    # Summary
    summary = resume_data.get("summary")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(summary, body_style))
        add_section_divider()

    # Skills
    skills = resume_data.get("skills", [])
    if skills:
        story.append(Paragraph("CORE TECHNICAL SKILLS", heading_style))
        story.append(Paragraph(" • ".join(skills), body_style))
        add_section_divider()

    # Experience
    experience = resume_data.get("experience", [])
    if experience:
        story.append(Paragraph("WORK EXPERIENCE", heading_style))
        for exp in experience:
            if isinstance(exp, dict):
                r = exp.get("role") or exp.get("title") or "Software Engineer"
                c = exp.get("company") or ""
                d = exp.get("duration") or ""
                desc = exp.get("description") or ""

                exp_header = f"<b>{r}</b>"
                if c:
                    exp_header += f" — <i>{c}</i>"
                if d:
                    exp_header += f" ({d})"

                story.append(Paragraph(exp_header, body_style))
                if desc:
                    story.append(Paragraph(f"• {desc}", bullet_style))
            elif isinstance(exp, str):
                story.append(Paragraph(f"• {exp}", bullet_style))
            story.append(Spacer(1, 4))
        add_section_divider()

    # Projects
    projects = resume_data.get("projects", [])
    if projects:
        story.append(Paragraph("KEY PROJECTS", heading_style))
        for proj in projects:
            if isinstance(proj, dict):
                pname = proj.get("name", "Project")
                ptech = proj.get("technologies") or []
                pdesc = proj.get("description", "")
                
                tech_str = (", ".join(ptech) if isinstance(ptech, list) else str(ptech)) if ptech else ""
                proj_header = f"<b>{pname}</b>"
                if tech_str:
                    proj_header += f" <font color='#4F46E5'>[{tech_str}]</font>"
                
                story.append(Paragraph(proj_header, body_style))
                if pdesc:
                    story.append(Paragraph(f"• {pdesc}", bullet_style))
            elif isinstance(proj, str):
                story.append(Paragraph(f"• {proj}", bullet_style))
            story.append(Spacer(1, 4))
        add_section_divider()

    # Education
    education = resume_data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get("degree") or edu.get("title") or "Degree"
                inst = edu.get("institution") or edu.get("school") or ""
                year = edu.get("year") or edu.get("duration") or ""
                story.append(Paragraph(f"• <b>{degree}</b> {('— ' + inst) if inst else ''} {('(' + year + ')') if year else ''}", body_style))
            elif isinstance(edu, str):
                story.append(Paragraph(f"• {edu}", body_style))
        add_section_divider()

    # Certifications & Achievements
    certs = resume_data.get("certifications", [])
    achieve = resume_data.get("achievements", [])
    combined = certs + achieve
    if combined:
        story.append(Paragraph("CERTIFICATIONS & ACHIEVEMENTS", heading_style))
        story.append(Paragraph(" • ".join(combined), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
