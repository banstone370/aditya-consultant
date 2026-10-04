#!/usr/bin/env python3
"""Generate Aditya Consultant company profile PDF matching Magwin Solar layout."""

from __future__ import annotations

import io
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "company-profile.pdf"
LOGO = ROOT / "img" / "Adity_Consultant_Logo.png"
IMG = ROOT / "img"

# Brand colors
PRIMARY = (197, 165, 114)  # #c5a572 gold
DARK = (26, 42, 54)  # #1a2a36 navy
ACCENT = (45, 95, 130)  # complementary blue for two-tone name
LIGHT_BOX = (235, 240, 245)
BODY = (70, 80, 95)
WHITE = (255, 255, 255)

COMPANY_A = "ADITYA"
COMPANY_B = "CONSULTANT"
FULL_NAME = "Aditya Consultant"
TAGLINE = "Solar Energy & Security Systems"
WEBSITE = "https://aditya-consultant.vercel.app"
EMAIL = "manishabhatt8168@gmail.com"
PHONES = "+91 83568 77637"
ADDRESS = "Vijay Park Opp BRNC Garden, Mira Road East - 401107"
HOURS = "Mon - Fri: 09:00 AM - 09:00 PM"

MARGIN = 14
HEADER_Y = 12
HEADER_TOP = 9
LOGO_SIZE = 14  # fits inside header band above divider lines
LINE_Y = 26
CONTENT_TOP = 44
FOOTER_Y = 272


def safe(text: str) -> str:
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "-")
        .replace("\uf0b7", "-")
        .replace("\u2713", "-")
    )


def thumb(path: Path, max_w: int = 420) -> str:
    """Return temp JPEG path resized for PDF embedding."""
    if not path.exists():
        return ""
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=78, optimize=True)
    tmp = ROOT / "scripts" / f".tmp_{path.stem}.jpg"
    tmp.write_bytes(buf.getvalue())
    return str(tmp)


class MagwinStylePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.set_margins(MARGIN, MARGIN, MARGIN)

    def brand_header(self):
        """Logo top-right inside header band, company name top-left, accent lines below."""
        # Company name (left)
        self.set_xy(MARGIN, HEADER_Y)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*PRIMARY)
        w_a = self.get_string_width(COMPANY_A)
        self.cell(w_a, 9, COMPANY_A)
        self.set_text_color(*DARK)
        self.cell(0, 9, f" {COMPANY_B}")

        # Logo (right) - sized to sit fully above the divider lines
        if LOGO.exists():
            logo_x = 196 - LOGO_SIZE
            self.image(str(LOGO), x=logo_x, y=HEADER_TOP, w=LOGO_SIZE, h=LOGO_SIZE)

        # Divider lines span full width below header band
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.5)
        self.line(MARGIN, LINE_Y, 196, LINE_Y)
        self.set_draw_color(*DARK)
        self.line(MARGIN, LINE_Y + 1.2, 196, LINE_Y + 1.2)

    def brand_footer(self):
        """Centered contact block at page bottom like Magwin."""
        y = FOOTER_Y
        self.set_draw_color(*DARK)
        self.set_line_width(0.5)
        self.line(MARGIN, y, 196, y)
        self.set_draw_color(*PRIMARY)
        self.line(MARGIN, y + 1.2, 196, y + 1.2)

        self.set_xy(MARGIN, y + 4)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*PRIMARY)
        w_a = self.get_string_width("Aditya ")
        self.cell(MARGIN + 93 - w_a, 5, "Aditya ", align="R")
        self.set_text_color(*DARK)
        self.cell(0, 5, "Consultant", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(40, 40, 40)
        for line in [
            f"Contact: {PHONES}",
            f"Website: {WEBSITE}, email: {EMAIL}",
            f"Address: {ADDRESS}  |  {HOURS}",
        ]:
            self.set_x(MARGIN)
            self.cell(0, 3.8, safe(line), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def new_content_page(self):
        self.add_page()
        self.brand_header()
        self.set_y(CONTENT_TOP)

    def section_title(self, title: str, underline: bool = True):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*PRIMARY)
        self.cell(0, 7, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if underline:
            y = self.get_y()
            self.set_draw_color(*PRIMARY)
            self.line(MARGIN, y, MARGIN + 38, y)
        self.ln(4)

    def section_title_blue(self, title: str):
        """Magwin-style blue italic service heading."""
        self.set_font("Helvetica", "BI", 11)
        self.set_text_color(*ACCENT)
        self.cell(0, 6, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        y = self.get_y()
        self.set_draw_color(*ACCENT)
        self.line(MARGIN, y, MARGIN + 72, y)
        self.ln(3)

    def body_para(self, text: str, italic: bool = False, bold_lead: str | None = None):
        self.set_font("Helvetica", "I" if italic else "", 9.5)
        self.set_text_color(*BODY)
        text = safe(text)
        if bold_lead and text.startswith(bold_lead):
            self.set_font("Helvetica", "BI" if italic else "B", 9.5)
            self.write(4.8, bold_lead)
            self.set_font("Helvetica", "I" if italic else "", 9.5)
            self.write(4.8, text[len(bold_lead) :])
            self.ln(4.8)
        else:
            self.multi_cell(0, 4.8, text)
        self.ln(1.5)

    def diamond_bullet(self, text: str):
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*BODY)
        self.set_x(MARGIN + 4)
        self.set_text_color(*ACCENT)
        self.cell(5, 4.8, "-")
        self.set_text_color(*BODY)
        self.multi_cell(0, 4.8, safe(text))
        self.ln(0.5)

    def check_bullet(self, text: str):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*BODY)
        self.set_x(MARGIN + 4)
        self.set_text_color(*ACCENT)
        self.cell(5, 4.8, "-")
        self.set_text_color(*BODY)
        self.multi_cell(0, 4.8, safe(text))
        self.ln(0.5)

    def epc_columns(self, columns: list[tuple[str, list[str]]]):
        col_w = 58
        gap = 4
        y0 = self.get_y()

        for i, (title, items) in enumerate(columns):
            x = MARGIN + i * (col_w + gap)
            # trapezoid-like header bar
            self.set_fill_color(*DARK)
            self.set_xy(x, y0)
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*WHITE)
            self.cell(col_w, 7, safe(title), align="C", fill=True)

            box_y = y0 + 8
            box_h = 6 + len(items) * 5.5
            self.set_fill_color(*LIGHT_BOX)
            self.rect(x, box_y, col_w, box_h, "F")

            for j, item in enumerate(items):
                self.set_xy(x + 2, box_y + 2 + j * 5.5)
                self.set_font("Helvetica", "", 7)
                self.set_text_color(*BODY)
                self.multi_cell(col_w - 4, 4, safe(f"- {item}"))

        self.set_y(y0 + 8 + max(6 + len(c[1]) * 5.5 for c in columns) + 4)

    def flow_steps(self, steps: list[str]):
        """Simple horizontal process steps like Magwin flowchart."""
        n = len(steps)
        box_w = min(22, (182 - (n - 1) * 3) / n)
        y0 = self.get_y()
        x = MARGIN

        for i, step in enumerate(steps):
            self.set_fill_color(*LIGHT_BOX)
            self.rect(x, y0, box_w, 14, "F")
            self.set_draw_color(*ACCENT)
            self.rect(x, y0, box_w, 14, "D")
            self.set_xy(x + 1, y0 + 2)
            self.set_font("Helvetica", "", 5.5)
            self.set_text_color(*DARK)
            self.multi_cell(box_w - 2, 3, safe(step), align="C")
            x += box_w
            if i < n - 1:
                self.set_xy(x, y0 + 5)
                self.set_font("Helvetica", "B", 8)
                self.set_text_color(*ACCENT)
                self.cell(3, 4, ">")
                x += 3

        self.set_y(y0 + 18)

    def image_grid(self, items: list[tuple[str, str]], cols: int = 3, img_h: float = 38):
        col_w = (182 - (cols - 1) * 4) / cols
        x0 = MARGIN
        y0 = self.get_y()
        row = 0
        col = 0

        for label, img_name in items:
            x = x0 + col * (col_w + 4)
            y = y0 + row * (img_h + 14)

            self.set_xy(x, y)
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*DARK)
            self.cell(col_w, 5, safe(label), align="C")

            img_path = IMG / img_name
            self.set_draw_color(*ACCENT)
            self.set_line_width(0.4)
            self.rect(x, y + 6, col_w, img_h, "D")
            if img_path.exists():
                t = thumb(img_path)
                if t:
                    self.image(t, x + 0.5, y + 6.5, w=col_w - 1, h=img_h - 1)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        rows = (len(items) + cols - 1) // cols
        self.set_y(y0 + rows * (img_h + 14) + 2)

    def project_grid(self, items: list[tuple[str, str]], cols: int = 2, img_h: float = 42):
        self.image_grid(items, cols=cols, img_h=img_h)


def build_pdf() -> Path:
    pdf = MagwinStylePDF()

    # --- PAGE 1: About Us, Mission, Vision ---
    pdf.new_content_page()
    pdf.section_title("About us")

    pdf.body_para(
        "ADITYA CONSULTANT is an EPC (Engineering, Procurement and Construction) company that "
        "delivers integrated solar energy solutions and end-to-end security systems with a focus on "
        "quality, effectiveness, environmental sustainability and cost saving.",
        italic=True,
        bold_lead="ADITYA CONSULTANT",
    )
    pdf.body_para(
        "We install, operate and maintain solar systems for Industrial, Residential and Commercial "
        "sectors. We are operational in the solar and security industry for over 5 years, offering "
        "the best services to our customers. Aditya Consultant is a renewable energy and security "
        "firm that specializes in solar powered energy solutions including on-grid systems, off-grid "
        "systems, solar water heaters, street lights, EV chargers, CCTV, access control, and more.",
        italic=True,
    )
    pdf.body_para(
        "We are based at Vijay Park Opp BRNC Garden, Mira Road East - 401107 with PAN India service and installation. Our "
        "network of engineers and installers across India gives us collective expertise of new "
        "developments in our industry, making Aditya Consultant one of the most reliable solar and "
        "security system designing and EPC firms in India.",
        italic=True,
    )
    pdf.body_para(
        "Aditya Consultant has a dedicated team to provide Technical services for Solar and Security "
        "Projects from the initial project idea to the installation and Maintenance, using the best "
        "available materials and components with highly qualified professionals.",
        italic=True,
    )
    pdf.body_para(
        "As an association, we have 20+ MW experience in solar industry as consulting, "
        "manufacturing, Installation, AMC and liaisoning work. Our approach ensures that the client "
        "continues to generate the highest yield from their solar PV plant, and the plant is able "
        "to offer high performance throughout the period of 25 years.",
        italic=True,
        bold_lead="20+ MW",
    )

    pdf.section_title("Mission")
    pdf.body_para(
        "At Aditya Consultant, our mission is to drive the adoption of renewable energy and reliable "
        "security systems through cutting-edge technology and innovative design. We aim to provide "
        "our clients with tailored solar and security solutions that not only meet their energy and "
        "safety needs but also contribute to a greener and more secure future.",
    )

    pdf.section_title("Vision")
    pdf.body_para(
        "We envision a world where clean and renewable energy and dependable security are accessible "
        "to all, reducing our carbon footprint and protecting people and property. Our goal is to be "
        "at the forefront of the solar and security industry, delivering excellence in every project "
        "and fostering long-term partnerships with our clients.",
    )
    pdf.brand_footer()

    # --- PAGE 2: Products & Services + Benefits ---
    pdf.new_content_page()
    pdf.section_title_blue("We provide following Product & Services")

    solar_services = [
        "On Grid solar system",
        "Off Grid solar system",
        "Solar Panels Installation",
        "Solar Water Heaters",
        "Solar street lights and home lights",
        "Solar Water Pumps",
        "Solar EV Car Chargers",
        "Solar AMC and Maintenance Services",
    ]
    for s in solar_services:
        pdf.diamond_bullet(s)

    pdf.ln(2)
    pdf.section_title_blue("Security Products & Services")
    security_services = [
        "CCTV and IP Surveillance Systems",
        "HD Cameras and IP Cameras",
        "Digital Video Recorders (DVR)",
        "Access Control and Attendance Systems",
        "Fire and Intrusion Protection",
        "Video Door Phones and Monitors",
        "Structured Cabling and Networking",
    ]
    for s in security_services:
        pdf.diamond_bullet(s)

    pdf.ln(2)
    pdf.section_title("Benefits of Solar")
    for b in [
        "Renewable source of energy",
        "Reduces electricity bills",
        "Low maintenance cost",
        "Earn from surplus generation",
        "Strong return on investment",
        "Environment friendly",
        "Life Span of 25 Years",
        "Tax benefit and subsidy available",
        "No Unit price escalation",
        "Loans, Subsidy and Insurance",
    ]:
        pdf.check_bullet(b)

    pdf.section_title("Benefits of Security Systems")
    for b in [
        "24/7 monitoring and protection",
        "Deter theft and unauthorized access",
        "Remote viewing via IP cameras",
        "Fire and intrusion early warning",
        "Controlled entry and attendance tracking",
        "Peace of mind for homes and businesses",
        "Professional installation and support",
    ]:
        pdf.check_bullet(b)
    pdf.brand_footer()

    # --- PAGE 3: EPC Solutions ---
    pdf.new_content_page()
    pdf.section_title("End to End EPC Solutions")
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 5, "From Concept to Execution:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.flow_steps(
        [
            "Bill analysis",
            "Site Survey",
            "System Design",
            "Engineering",
            "Procurement",
            "Installation",
            "Commissioning",
            "Maintenance",
        ]
    )
    pdf.ln(2)

    pdf.epc_columns(
        [
            (
                "Engineering",
                [
                    "Yield assessment",
                    "Preliminary design",
                    "Selection of components",
                    "Finalization of design",
                    "Construction design",
                    "Detailed engineering",
                ],
            ),
            (
                "Procurement",
                [
                    "Specifications",
                    "Tendering/bid comparison",
                    "Contract preparation",
                    "Purchase of modules",
                    "Equipment sourcing",
                    "Quality verification",
                ],
            ),
            (
                "Construction",
                [
                    "Installation documentation",
                    "Specialist site management",
                    "Logistics co-ordination",
                    "Safety co-ordination",
                    "Commissioning and testing",
                    "Performance verification",
                ],
            ),
        ]
    )

    pdf.section_title("Financial model based classification")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 5, "CAPEX:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_para(
        "CAPEX (Capital Expenditure) is a common business model for solar deployment in India where "
        "the consumer purchases the solar PV system, by making 100% of the payment upfront or "
        "financing the system, often through a bank.",
    )
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 5, "OPEX:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_para(
        "OPEX (Operational Expenditure) model is where the RESCO (Renewable Energy Service Company) "
        "developer invests in solar rooftop asset and sells the generated power to the building owner "
        "in favour of a lower solar power tariff. The excess power may be sold by the building owner "
        "to the utility according to the power purchase agreement through net metering system.",
    )
    pdf.brand_footer()

    # --- PAGE 4: Solar Solutions ---
    pdf.new_content_page()
    pdf.section_title("Solar Solutions")
    pdf.image_grid(
        [
            ("Rooftop System", "SolarInstallation.jpg"),
            ("Solar Water Heater", "SolarWaterHeater.jpg"),
            ("Solar Street Light", "SolarStreetLight.jpg"),
            ("Solar Water Pump", "SolarWaterPump.jpe"),
            ("Solar On Grid", "SolarOnGrid.jpg"),
            ("Solar Off Grid", "SolarOffGrid.jpg"),
            ("Solar EV Charger", "SolarEVCarCharger.jpg"),
            ("Solar AMC Services", "SolarAMCServices.jpg"),
        ],
        cols=3,
        img_h=36,
    )
    pdf.brand_footer()

    # --- PAGE 5: Security Solutions ---
    pdf.new_content_page()
    pdf.section_title("Security Solutions")
    pdf.image_grid(
        [
            ("HD Cameras", "HD-Cameras.jpg"),
            ("IP Cameras", "IP-Cameras.jpg"),
            ("Digital Video Recorder", "DVR.jpg"),
            ("Monitors", "High-Quality-Monitors.jpg"),
            ("Video Door Phones", "Video-Door-Phones.jpg"),
            ("Access Control Systems", "IP-Cameras.jpg"),
        ],
        cols=3,
        img_h=36,
    )
    pdf.brand_footer()

    # --- PAGE 6: Project Execution ---
    pdf.new_content_page()
    pdf.section_title("Project Execution")
    pdf.project_grid(
        [
            ("Solar Panel Installation", "Solar_Panel.jpg"),
            ("Railway Station Solar", "Solar_Power_Railway_Station.jpg"),
            ("Rural Solar Power", "Rural_Solar_Power.jpg"),
            ("Security System Setup", "HD-Cameras.jpg"),
        ],
        cols=2,
        img_h=48,
    )
    pdf.brand_footer()

    # --- PAGE 7: Projects Executed ---
    pdf.new_content_page()
    pdf.section_title("Projects Executed")
    pdf.project_grid(
        [
            ("Mumbai - Solar Installation", "gallery-1.jpg"),
            ("Maharashtra - Rooftop Solar", "gallery-2.jpg"),
            ("Commercial Solar Plant", "gallery-3.jpg"),
            ("Industrial Solar Project", "gallery-4.jpg"),
            ("Security Surveillance", "gallery-5.jpg"),
            ("Integrated Solar & Security", "gallery-6.jpg"),
        ],
        cols=2,
        img_h=44,
    )
    pdf.brand_footer()

    pdf.output(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = build_pdf()
    print(f"Created: {path} ({path.stat().st_size / 1024:.1f} KB)")
