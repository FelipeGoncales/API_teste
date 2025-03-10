from flask import Flask, request, jsonify
from main import app, con
from flask_bcrypt import check_password_hash
import jwt

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute('SELECT EMAIL, SENHA FROM USUARIOS WHERE EMAIL = ?', (email,))

    usuario = cursor.fetchone()

    if not usuario:
        return jsonify({'error': 'Email não encontrado.'}), 404

    if not check_password_hash(usuario[1], senha):
        return jsonify({'error': 'Senha inválida.'}), 404

    return jsonify({'success': 'Login realizado com sucesso'}), 200