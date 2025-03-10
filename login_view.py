from flask import Flask, request, jsonify
from main import app, con, senha_secreta
from flask_bcrypt import check_password_hash
import jwt

def generate_token(user_id):
    payload = {'id_usuario': user_id}
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')
    return token

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute('SELECT SENHA, ID_USUARIO FROM USUARIOS WHERE EMAIL = ?', (email,))

    usuario = cursor.fetchone()

    if not usuario:
        return jsonify({'error': 'Email não encontrado.'}), 404

    if not check_password_hash(usuario[0], senha):
        return jsonify({'error': 'Senha inválida.'}), 404

    token = generate_token(usuario[1])
    return jsonify({
        'success': 'Login realizado com sucesso',
        'token': token
    }), 200