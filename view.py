from flask import Flask, jsonify
from main import app, con

@app.route('/livros', methods=['GET'])
def livros():
    cursor = con.cursor()
    cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM LIVROS')

    livros = cursor.fetchall()

    livros_dic = []

    for livro in livros:
        livros_dic.append({
            'id_livro': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3]
        })

    return jsonify(mensagem='Lista de livros', livros=livros_dic)

