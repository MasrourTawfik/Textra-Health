from fpdf import FPDF
import io

from fpdf import FPDF

class ReportService:
    def __init__(self, logo_path: str, company_name: str, footer_text: str):
        self.logo_path = logo_path
        self.company_name = company_name
        self.footer_text = footer_text

    def generate_report(self, organized_text: str, analysis_text: str, output_path: str):
        pdf = FPDF()

        # Page setup
        pdf.add_page()

        # Adding logo
        if self.logo_path:
            pdf.image(self.logo_path, 10, 8, 33)

        # Set font for title and add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, self.company_name, ln=True, align='C')

        # Line break
        pdf.ln(20)

        # Section for organized text
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Texte Organisé:", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 10, organized_text)

        # Line break
        pdf.ln(10)

        # Section for analysis text
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Analyse:", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 10, analysis_text)

        # Footer
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, self.footer_text, ln=True, align='C')

        # Output the PDF
        pdf.output(output_path)

        return output_path
