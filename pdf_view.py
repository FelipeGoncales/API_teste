from flask import Flask, request, jsonify, send_file
from main import app, con
from fpdf import FPDF

@app.route('/livros/relatorio', methods=['GET'])
def criar_pdf():

    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    #Criação do PDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')

    #Adicionando uma Linha Separadora:
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    #Inserindo os Dados dos Livros:
    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)

    #Adicionando o Total de Livros Cadastrados:
    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')
