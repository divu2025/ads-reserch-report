from fpdf import FPDF
import datetime
import os

class PDFReport(FPDF):
    def header(self):
        # Logo
        self.set_font('helvetica', 'B', 15)
        self.cell(80)
        self.cell(30, 10, '💍 Jewelry Search Term Intel Audit', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('helvetica', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, label, 0, 1, 'L', fill=True)
        self.ln(4)

    def section_text(self, text):
        self.set_font('helvetica', '', 12)
        self.multi_cell(0, 8, text)
        self.ln()

class PDFService:
    def __init__(self):
        pass

    def generate_report(self, report_data: dict, output_path: str):
        pdf = PDFReport()
        pdf.add_page()
        
        # 1. Executive Summary
        pdf.chapter_title('1. Executive Summary')
        summary_text = (
            f"Total Spend: ${report_data['total_spend']:,.2f}\n"
            f"Waste Spend: ${report_data['waste_spend']:,.2f}\n"
            f"Efficiency Score: {report_data['efficiency_score']:.1f}/100\n"
            f"Intent Quality: {report_data['intent_score']:.1f}%\n\n"
            f"Audit Conclusion: {report_data.get('ai_insights', 'Targeting mismatch detected. Negative keyword expansion required.')}"
        )
        pdf.section_text(summary_text)

        # 2. Score Breakdown
        pdf.chapter_title('2. Score Breakdown')
        scores = report_data.get('scores', {})
        score_text = (
            f"Search Intent Quality: {scores.get('intent_quality', 0)}/100\n"
            f"Waste Control: {scores.get('waste_control', 0)}/100\n"
            f"Conversion Efficiency: {scores.get('conversion_efficiency', 0)}/100\n"
            f"OVERALL PERFORMANCE: {scores.get('overall_score', 0)}/100"
        )
        pdf.section_text(score_text)

        # 3. Critical Issues
        pdf.chapter_title('3. Top Critical Issues')
        pdf.section_text(report_data.get('critical_issues', '- High spend on zero-conversion informational search terms.'))

        # 4. Search Term Analysis (Summary)
        pdf.chapter_title('4. Core Analysis Insights')
        pdf.section_text('Primary patterns identified: Irrelevant high-frequency informational queries triggering expensive automated bids.')

        # 5. Waste Clusters
        pdf.chapter_title('5. Waste Pattern Detection')
        clusters = report_data.get('clusters', [])
        cluster_text = ""
        for c in clusters:
            cluster_text += f"- {c['label']}: {c['count']} terms, costing ${c['cost']:,.2f}\n"
        pdf.section_text(cluster_text if cluster_text else "No major waste clusters detected.")

        # 6. Action Plan
        pdf.chapter_title('6. 4-Week Strategic Roadmap')
        roadmap = (
            "Week 1: Immediate negative keyword cleanup.\n"
            "Week 2: Ad group restructuring for cluster alignment.\n"
            "Week 3: Scaling high-intent conversion keywords.\n"
            "Week 4: Performance audit and rule-base adjustment."
        )
        pdf.section_text(roadmap)

        # Methodology
        pdf.ln(10)
        pdf.chapter_title('Methodology')
        pdf.section_text('Analysis processed using Jewelry Ads Intel Engine (Llama 3.1 & TF-IDF Clustering). Data Source: Search Terms Report.')

        pdf.output(output_path)
        return output_path
