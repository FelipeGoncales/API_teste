from flask import Flask, jsonify, request
from main import app, con

@app.route('/livros', methods=['GET'])
def livros():
    search = request.args.get('s')

    cursor = con.cursor()

    if search:
        cursor.execute('SELECT titulo, autor, ano_publicacao FROM LIVROS WHERE titulo LIKE ?', (f"%{search}%",))
        resultados = cursor.fetchall()
        return jsonify({
            "mensagem": f"{len(resultados)} livro(s) encontrado(s)",
            "livros": [{
                "titulo": row[0],
                "autor": row[1],
                "ano_publicacao": row[2]
            } for row in resultados]
        })

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


@app.route('/livros', methods=['POST'])
def mostrar_livro():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE TITULO = ?', (titulo,))

    if cursor.fetchone():
        return jsonify(mensagem='Livro já cadastrado')

    cursor.execute('INSERT INTO LIVROS(TITULO, AUTOR, ANO_PUBLICACAO) VALUES(?, ?, ?)', (titulo, autor, ano_publicacao))

    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': 'Livro cadastrado com sucesso',
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })

@app.route('/livros/<int:id>', methods=['PUT'])
def editar_livro(id):
    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE ID_LIVRO = ?', (id,))

    if not cursor.fetchone():
        cursor.close()
        return jsonify(mensagem='Livro não encontrado')

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute('UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?',
                   (titulo, autor, ano_publicacao, id))

    con.commit()
    cursor.close()

    return jsonify({
        "mensagem": "Livro editado com sucesso",
        "livro": {
            "titulo": titulo,
            "autor": autor,
            "ano_publicacao": ano_publicacao
        }
    })

@app.route('/livros/<int:id>', methods=['DELETE'])
def apagar_livro(id):
    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE ID_LIVRO = ?', (id,))

    if not cursor.fetchone():
        cursor.close()
        return jsonify(mensagem='Nenhum livro não encontrado')

    cursor.execute('SELECT titulo, autor, ano_publicacao FROM LIVROS WHERE ID_LIVRO = ?', (id,))
    livro = cursor.fetchone()

    cursor.execute('DELETE FROM LIVROS WHERE ID_LIVRO = ?', (id,))

    con.commit()

    cursor.close()

    return jsonify({
        "mensagem": "Livro excluído com sucesso",
        "livro": {
            "titulo": livro[0],
            "autor": livro[1],
            "ano_publicacao": livro[2]
        }
    })