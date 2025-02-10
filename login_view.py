from flask import Flask, request, jsonify
from main import app, con

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute('SELECT EMAIL, SENHA FROM USUARIOS WHERE EMAIL = ?', (email,))

    usuario = cursor.fetchone()

    if not usuario:
        return jsonify(mensagem='Email não encontrado.')

    if usuario[1] != senha:
        return jsonify(mensagem='Senha inválida.')

    return jsonify(mensagem='Login realizado com sucesso!')