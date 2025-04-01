from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import psycopg2
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

app = Flask(__name__)
app.secret_key = 'secreta_chave'

# Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET')
)

# Conexão com o PostgreSQL
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Criação das tabelas no banco de dados
def init_db():
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS media (
                        id SERIAL PRIMARY KEY,
                        url TEXT NOT NULL
                    )''')
    cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'senhaadmin', 'admin') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO users (username, password, role) VALUES ('user', 'senhauser', 'user') ON CONFLICT DO NOTHING")
    conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    cur.execute("SELECT role FROM users WHERE username = %s AND password = %s", (username, password))
    result = cur.fetchone()
    
    if result:
        session['role'] = result[0]
        if result[0] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('user'))
    return "Credenciais inválidas"

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/user')
def user():
    if session.get('role') != 'user':
        return redirect(url_for('index'))
    return render_template('user.html')

@app.route('/get_files')
def get_files():
    cur.execute("SELECT url FROM media")
    files = [row[0] for row in cur.fetchall()]
    return jsonify(files)

@app.route('/upload', methods=['POST'])
def upload():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file:
        upload_result = cloudinary.uploader.upload(file, resource_type="auto")
        cur.execute("INSERT INTO media (url) VALUES (%s)", (upload_result['secure_url'],))
        conn.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
