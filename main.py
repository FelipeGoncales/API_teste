from flask import Flask
import fdb

app = Flask(__name__)

app.config.from_pyfile('config.py')

host = app.config['DB_HOST']
database = app.config['DB_NAME']
user = app.config['DB_USER']
password = app.config['DB_PASSWORD']
senha_secreta = app.config['SECRET_KEY']

try:
    con = fdb.connect(host=host, database=database, user=user, password=password)
    print('Conexão estabelecida com sucesso')
except Exception as e:
    print(f'Error: {e}')

from book_view import *
from user_view import *
from login_view import *
from pdf_view import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
