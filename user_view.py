from flask import Flask, jsonify, request
from main import app, con
import re
from flask_bcrypt import generate_password_hash

@app.route('/user', methods=['GET'])
def get_user():
    cursor = con.cursor()

    cursor.execute('SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS')

    resultado = cursor.fetchall()

    user_dic = []
    for user in resultado:
        user_dic.append({
            'id_usuario': user[0],
            'nome': user[1],
            'email': user[2],
            'senha': user[3]
        })

    cursor.close()

    return jsonify({'usuarios': user_dic}), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    if not nome or not email or not senha:
        return jsonify({'error': 'Informações faltando.'}), 404

    cursor.execute('SELECT EMAIL FROM USUARIOS')
    emails_existentes = [email[0] for email in cursor.fetchall()]

    for verificar in emails_existentes:
        if verificar == email:
            return jsonify({'error': 'Email já cadastrado.'}), 404

    if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', senha):
        return jsonify(
            {'error': 'A senha deve ter ao menos 8 caracteres, uma letra maiúscula, um número e um caractere especial.'}), 404

    senha = generate_password_hash(senha).decode('utf8')
    cursor.execute('''
        INSERT INTO USUARIOS (NOME, EMAIL, SENHA)
        VALUES (?, ?, ?)
    ''', (nome, email, senha))

    con.commit()
    cursor.close()

    return jsonify({'sucess': 'Usuário cadastrado com sucesso',
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })

@app.route('/user', methods=['PUT'])
def edit_user():
    data = request.get_json()
    id_usuario = data.get('id_usuario')
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    if not id_usuario or not nome or not email or not senha:
        return jsonify({'error': 'Erro ao editar usuário.'}), 404

    cursor.execute('SELECT EMAIL FROM USUARIOS WHERE id_usuario != ?', (id_usuario,))
    emails_existentes = [email[0] for email in cursor.fetchall()]
    for email_verificar in emails_existentes:
        if email_verificar == email:
            return jsonify({'error': 'Email já cadastrado.'}), 404

    if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', senha):
        return jsonify({'error': 'A senha deve ter ao menos 8 caracteres, uma letra maiúscula, um número e um caractere especial.'}), 404

    cursor.execute('SELECT ID_USUARIO FROM USUARIOS')
    ids_existentes = [row[0] for row in cursor.fetchall()]
    for id_verificar in ids_existentes:
        if id_verificar == id_usuario:
            senha = generate_password_hash(senha).decode('utf8')
            cursor.execute('UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIO = ?', (nome, email, senha, id_usuario))
            con.commit()
            cursor.close()

            return jsonify({
                'sucess': 'Usuário editado com sucesso.',
                'usuario': {
                    'id_usuario': id_usuario,
                    'nome': nome,
                    'email': email,
                    'senha': senha
                }
            }), 200

    return jsonify({'error': 'Usuário não encontrado.'}), 404

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    cursor = con.cursor()

    cursor.execute('SELECT ID_USUARIO FROM USUARIOS')
    ids_existentes = [user[0] for user in cursor.fetchall()]

    for id_verificar in ids_existentes:
        if id_verificar == id:
            cursor.execute('SELECT NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIO = ?', (id,))
            data = cursor.fetchone()

            cursor.execute('DELETE FROM USUARIOS WHERE ID_USUARIO = ?', (id,))
            con.commit()
            cursor.close()

            return jsonify({
                'success': 'Usuário excluído com sucesso.',
                'usuario': {
                    'nome': data[0],
                    'email': data[1],
                    'senha': data[2]
                }
            }), 200

    return jsonify({'error': 'Usuário não encontrado.'}), 404