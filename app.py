from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import psycopg2
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from random import shuffle

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'your-secret-key-here'

# Configurações
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET')
)

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

# Inicialização do Banco de Dados
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                nome_responsavel VARCHAR(100) NOT NULL,
                senha VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS estabelecimentos (
                id SERIAL PRIMARY KEY,
                id_usuario INTEGER NOT NULL,
                nome VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE (id_usuario)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS midias (
                id SERIAL PRIMARY KEY,
                id_usuario INTEGER NOT NULL,
                id_estabelecimento INTEGER NOT NULL,
                url VARCHAR(255) NOT NULL,
                tipo_midia VARCHAR(20) CHECK (tipo_midia IN ('imagem', 'video')),
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (id_estabelecimento) REFERENCES estabelecimentos(id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            INSERT INTO usuarios (username, nome_responsavel, senha, role)
            VALUES ('santosmidia', 'Admin', '123456', 'admin')
            ON CONFLICT (username) DO NOTHING
        """)

        cur.execute("""
            INSERT INTO estabelecimentos (id_usuario, nome, tipo)
            VALUES (
                (SELECT id FROM usuarios WHERE username = 'santosmidia'),
                'Admin Central',
                'admin'
            ) ON CONFLICT (id_usuario) DO NOTHING
        """)

        conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

init_db()

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT u.id, u.role, e.tipo 
            FROM usuarios u
            JOIN estabelecimentos e ON u.id = e.id_usuario
            WHERE u.username = %s AND u.senha = %s
        """, (username, password))
        
        result = cur.fetchone()
        
        if result:
            session['user_id'] = result[0]
            session['username'] = username
            session['role'] = result[1]
            session['tipo_estabelecimento'] = result[2]
            
            if result[1] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('user'))
        
        flash('Credenciais inválidas', 'error')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/user')
def user():
    if 'user_id' not in session or session.get('role') == 'admin':
        return redirect(url_for('index'))
    
    return render_template('user.html')

@app.route('/midias_user', methods=['GET'])
def midias_user():
    if 'user_id' not in session or session.get('role') == 'admin':
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT m.url 
            FROM midias m
            JOIN estabelecimentos e ON m.id_estabelecimento = e.id
            WHERE e.tipo = %s
        """, (session['tipo_estabelecimento'],))
        
        midias = cur.fetchall()
        midias_urls = [midia[0] for midia in midias]
        shuffle(midias_urls)
        
        return jsonify(midias_urls)
    finally:
        cur.close()
        conn.close()

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)