from flask import Flask, jsonify, request
from main import app, con, senha_secreta
import os
import jwt

def remover_bearer(token):
    if token.startswith('Bearer '):
        return token[len('Bearer: '):]
    else:
        return token

@app.route('/livros', methods=['GET'])
def livros():
    search = request.args.get('s')

    cursor = con.cursor()

    if search:
        cursor.execute('SELECT titulo, autor, ano_publicacao FROM LIVROS WHERE titulo LIKE ?', (f"%{search}%",))
        resultados = cursor.fetchall()
        return jsonify({
            "success": f"{len(resultados)} livro(s) encontrado(s)",
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

    return jsonify({
        'success': 'Lista encontrada.',
        'lista': livros_dic
    }), 200
@app.route('/livro', methods=['POST'])
def livro_post():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token de autenticação necessário'}), 401

    token = remover_bearer(token)
    try:
        payload = jwt.decode(token, senha_secreta, algorithms=['HS256'])
        id_usuario = payload['id_usuario']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    # Recebendo os dados do formulário (não JSON)
    titulo = request.form.get('titulo')
    autor = request.form.get('autor')
    ano_publicacao = request.form.get('ano_publicacao')
    imagem = request.files.get('imagem')  # Arquivo enviado

    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM livros WHERE TITULO = ?", (titulo,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro já cadastrado"}), 400

    cursor.execute('''
        INSERT INTO livros (TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?) RETURNING ID_livro
    ''', (titulo, autor, ano_publicacao))

    livro_id = cursor.fetchone()[0]

    con.commit()

    imagem_path = None
    if imagem:
        nome_imagem = f"{livro_id}.jpeg"  # Define o nome fixo com .jpeg
        pasta_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Livros")
        os.makedirs(pasta_destino, exist_ok=True)
        imagem_path = os.path.join(pasta_destino, nome_imagem)
        imagem.save(imagem_path)

    cursor.close()

    return jsonify({
        'success': "Livro cadastrado com sucesso!",
        'livro': {
            'id': livro_id,
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao,
            'imagem_path': imagem_path
        }
    }), 201

@app.route('/livros/<int:id>', methods=['PUT'])
def editar_livro(id):
    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE ID_LIVRO = ?', (id,))

    if not cursor.fetchone():
        cursor.close()
        return jsonify({'error': 'Livro não encontrado.'}), 404

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute('UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?',
                   (titulo, autor, ano_publicacao, id))

    con.commit()
    cursor.close()

    return jsonify({
        "success": "Livro editado com sucesso",
        "livro": {
            "titulo": titulo,
            "autor": autor,
            "ano_publicacao": ano_publicacao
        }
    }), 200

@app.route('/livros/<int:id>', methods=['DELETE'])
def apagar_livro(id):
    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE ID_LIVRO = ?', (id,))

    if not cursor.fetchone():
        cursor.close()
        return jsonify({'error': 'Nenhum livro não encontrado.'}), 404

    cursor.execute('SELECT titulo, autor, ano_publicacao FROM LIVROS WHERE ID_LIVRO = ?', (id,))
    livro = cursor.fetchone()

    cursor.execute('DELETE FROM LIVROS WHERE ID_LIVRO = ?', (id,))

    con.commit()

    cursor.close()

    return jsonify({
        "success": "Livro excluído com sucesso",
        "livro": {
            "titulo": livro[0],
            "autor": livro[1],
            "ano_publicacao": livro[2]
        }
    }), 200