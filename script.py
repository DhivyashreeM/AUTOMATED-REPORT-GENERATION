import csv
from datetime import datetime
from fpdf import FPDF, XPos, YPos
import matplotlib.pyplot as plt
import numpy as np
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", 'B', 15)
        self.cell(0, 10, 'Data Analysis Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font("helvetica", '', 10)
        self.cell(0, 10, datetime.now().strftime('%Y-%m-%d'), align='R')
        self.ln(20)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
    
    def chapter_title(self, title):
        self.set_font("helvetica", 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(4)
    
    def chapter_body(self, body):
        self.set_font("helvetica", '', 12)
        self.multi_cell(0, 5, body)
        self.ln()
    
    def add_table(self, data, headers):
        self.set_fill_color(63, 119, 191)
        self.set_text_color(255)
        self.set_draw_color(63, 119, 191)
        self.set_line_width(0.3)
        self.set_font("helvetica", 'B', 10)
        
        col_widths = [self.get_string_width(header) + 6 for header in headers]
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, border=1, align='C', fill=True)
        self.ln()
        
        self.set_fill_color(224, 235, 255)
        self.set_text_color(0)
        self.set_font("helvetica", '', 10)
        
        fill = False
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 6, str(item), border='LR', align='L', fill=fill)
            self.ln()
            fill = not fill
        
        self.cell(sum(col_widths), 0, '', border='T')

def analyze_data(data):
    analysis = {}
    
    numeric_data = []
    for row in data[1:]:
        try:
            numeric_row = [float(x) if x.replace('.', '').isdigit() else x for x in row]
            numeric_data.append(numeric_row)
        except:
            pass
    
    if not numeric_data:
        return analysis
    
    numeric_cols = []
    for i in range(len(numeric_data[0])):
        if isinstance(numeric_data[0][i], float):
            numeric_cols.append(i)
    
    for col in numeric_cols:
        col_name = data[0][col]
        values = [row[col] for row in numeric_data]
        analysis[col_name] = {
            'mean': np.mean(values),
            'median': np.median(values),
            'min': min(values),
            'max': max(values),
            'std': np.std(values)
        }
    
    return analysis

def create_plot(data, analysis, filename='plot.png'):
    if not analysis:
        return False
    
    metrics = list(analysis.keys())
    means = [analysis[m]['mean'] for m in metrics]
    
    plt.figure(figsize=(8, 5))
    plt.bar(metrics, means)
    plt.title('Mean Values by Metric')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return True

def generate_report(input_file, output_file):
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    
    if len(data) < 2:
        print("Not enough data to generate report")
        return
    
    analysis = analyze_data(data)
    
    plot_created = create_plot(data, analysis)
    
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, 'Data Analysis Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", '', 12)
    pdf.multi_cell(0, 5, f"This report analyzes data from {input_file}. The dataset contains {len(data)-1} records with {len(data[0])} fields each.")
    pdf.ln()
    
    pdf.chapter_title('Data Summary')
    
    if analysis:
        summary_text = "The dataset contains the following numeric fields with these characteristics:\n"
        for field, stats in analysis.items():
            summary_text += f"\n- {field}: Mean = {stats['mean']:.2f}, Median = {stats['median']:.2f}, Range = {stats['min']:.2f} to {stats['max']:.2f}"
        pdf.chapter_body(summary_text)
    else:
        pdf.chapter_body("No numeric data found for analysis.")
    
    if plot_created:
        pdf.chapter_title('Data Visualization')
        pdf.image('plot.png', x=10, w=180)
        pdf.ln()

    pdf.chapter_title('Sample Data')
    pdf.add_table(data[1:min(11, len(data))], data[0])
    
    pdf.output(output_file)
    
    if plot_created and os.path.exists('plot.png'):
        os.remove('plot.png')

def create_sample_data():
    """Create sample data file if it doesn't exist"""
    if not os.path.exists('sample_data.csv'):
        with open('sample_data.csv', 'w') as f:
            f.write("""Date,Product,Category,Units Sold,Revenue
2023-01-01,Product A,Electronics,150,7500.50
2023-01-02,Product B,Furniture,30,4500.00
2023-01-03,Product C,Electronics,85,4250.75
2023-01-04,Product A,Electronics,90,4500.00
2023-01-05,Product D,Clothing,120,3600.00
2023-01-06,Product B,Furniture,25,3750.00
2023-01-07,Product E,Electronics,200,10000.25
2023-01-08,Product C,Electronics,60,3000.50
2023-01-09,Product D,Clothing,80,2400.00
2023-01-10,Product A,Electronics,110,5500.75""")

if __name__ == '__main__':
    create_sample_data()
    
    input_csv = 'sample_data.csv'
    output_pdf = 'analysis_report.pdf'
    
    generate_report(input_csv, output_pdf)
    print(f"Report generated successfully: {output_pdf}")
