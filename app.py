from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import pandas as pd
import os
import uuid
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from werkzeug.utils import secure_filename

# import your existing processors (edit module names if needed)
import Code.jewishhome_processor as jewishhome_processor
import Code.njveterans_processor as njveterans_processor
import Code.uhc_processor as uhc_processor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'tmp_uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'Output')

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'Code', 'templates'))
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development-key')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def read_uploaded_file(path):
    try:
        return pd.read_excel(path)
    except Exception:
        return pd.read_csv(path)


def create_invoice_pdf(result, choice, output_path):
    page_size = landscape(letter) if len(result.columns) > 5 else letter
    document = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle', parent=styles['Title'], fontName='Helvetica-Bold',
        fontSize=18, leading=22, textColor=colors.HexColor('#17324d'),
        alignment=TA_LEFT, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'InvoiceBody', parent=styles['BodyText'], fontName='Helvetica',
        fontSize=9, leading=11, textColor=colors.HexColor('#17324d'),
    )
    header_style = ParagraphStyle(
        'InvoiceHeader', parent=body_style, fontName='Helvetica-Bold',
        textColor=colors.white,
    )
    amount_style = ParagraphStyle(
        'InvoiceAmount', parent=body_style, alignment=TA_RIGHT,
    )

    program_names = {
        'jewishhome': 'JEWISH HOME BILLING INVOICE',
        'njveterans': 'NJ VETERANS BILLING INVOICE',
        'uhc': 'UHC BILLING INVOICE',
    }
    story = [
        Paragraph('Fourline Travels LLC', title_style),
        Paragraph('645 Stelton St, Teaneck, NJ 07666 | Phone: 551-313-8500 | Email: info@fourlinetravels.com', body_style),
        Spacer(1, 0.22 * inch),
        Paragraph(program_names[choice], title_style),
        Spacer(1, 0.1 * inch),
    ]

    table_data = [[Paragraph(str(column).replace('_', ' ').title(), header_style) for column in result.columns]]
    for row in result.itertuples(index=False, name=None):
        table_data.append([
            Paragraph(f'${value:,.2f}', amount_style) if column == 'calculated_cost'
            else Paragraph(str(value), body_style)
            for column, value in zip(result.columns, row)
        ])

    column_count = len(result.columns)
    column_width = (page_size[0] - 1.1 * inch) / column_count
    table = Table(table_data, repeatRows=1, colWidths=[column_width] * column_count)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#087f8c')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d9e4e9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f8f9')]),
    ]))
    story.append(table)
    story.extend([
        Spacer(1, 0.18 * inch),
        Paragraph(f'<b>TOTAL: ${result["calculated_cost"].sum():,.2f}</b>', amount_style),
    ])
    document.build(story)
processors = {
    'jewishhome': (jewishhome_processor.calculate_jewishhome_cost, 'miles'),
    'njveterans': (njveterans_processor.calculate_njveterans_cost, 'hours'),
    'uhc': (uhc_processor.calculate_uhc_cost, 'miles'),
}


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/process', methods=['POST'])
def process():
    upload = request.files.get('datafile')
    choice = request.form.get('processor')
    if not upload or not upload.filename:
        flash('Choose a CSV or Excel file first.')
        return redirect(url_for('index'))
    if choice not in processors:
        flash('Choose a valid processor.')
        return redirect(url_for('index'))

    filename = secure_filename(upload.filename)
    tmp_path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4().hex}_{filename}')
    try:
        upload.save(tmp_path)
        df = read_uploaded_file(tmp_path)
        calculator, column = processors[choice]
        if column not in df.columns:
            raise ValueError(f"The uploaded file must contain a '{column}' column.")
        result = df.copy()
        result['calculated_cost'] = pd.to_numeric(
            result[column], errors='raise'
        ).map(calculator)
        output_name = f'invoice_{choice}_{uuid.uuid4().hex}.pdf'
        create_invoice_pdf(result, choice, os.path.join(OUTPUT_FOLDER, output_name))
    except (ValueError, KeyError, TypeError, pd.errors.ParserError) as error:
        flash(f'Could not process the file: {error}')
        return redirect(url_for('index'))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return render_template('result.html', filename=output_name)


@app.route('/download')
def download():
    filename = secure_filename(request.args.get('filename', ''))
    if not filename:
        flash('Invalid download path')
        return redirect(url_for('index'))
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)