from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash import os import psycopg2 import cloudinary import cloudinary.uploader from dotenv import load_dotenv from fpdf import FPDF import random import string

load_dotenv()

app = Flask(name) app.secret_key = os.getenv('SECRET_KEY') or 'your-secret-key-here'

Configurações

cloudinary.config( cloud_name=os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), api_secret=os.getenv('API_SECRET') )

def get_db_connection(): return psycopg2.connect(os.getenv('DATABASE_URL'))

def generate_random_filename(): return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.pdf'

@app.route('/generate_report', methods=['GET', 'POST']) def generate_report(): if session.get('role') != 'admin': return redirect(url_for('index'))

conn = get_db_connection()
cur = conn.cursor()

try:
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Consulta filtrada de mídias
        cur.execute('''
            SELECT m.id, m.url, m.tipo_midia, u.username, m.data_upload
            FROM midias m
            JOIN usuarios u ON m.id_usuario = u.id
            WHERE (%s IS NULL OR m.id_usuario = %s)
            AND (%s IS NULL OR m.data_upload >= %s)
            AND (%s IS NULL OR m.data_upload <= %s)
        ''', (user_id, user_id, start_date, start_date, end_date, end_date))

        midias = cur.fetchall()

        # Geração do relatório em PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Relatório de Mídias', 0, 1, 'C')

        pdf.set_font('Arial', '', 12)
        for midia in midias:
            pdf.cell(0, 10, f'Usuário: {midia[3]}', 0, 1)
            pdf.cell(0, 10, f'URL: {midia[1]}', 0, 1)
            pdf.cell(0, 10, f'Tipo: {midia[2]}', 0, 1)
            pdf.cell(0, 10, f'Data de Upload: {midia[4]}', 0, 1)
            pdf.ln(10)

        filename = generate_random_filename()
        file_path = os.path.join('static/reports', filename)
        pdf.output(file_path)

        flash('Relatório gerado com sucesso!', 'success')
        return redirect(url_for('admin'))
except Exception as e:
    print(f'Erro ao gerar relatório: {e}')
    flash('Erro ao gerar relatório', 'error')
finally:
    cur.close()
    conn.close()

return render_template('generate_report.html')

Rotas para gerenciamento de usuários

@app.route('/admin/users') def list_users(): if session.get('role') != 'admin': return redirect(url_for('index'))

conn = get_db_connection()
cur = conn.cursor()
cur.execute('SELECT * FROM usuarios')
users = cur.fetchall()
cur.close()
conn.close()

return render_template('list_users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST']) def create_user(): if session.get('role') != 'admin': return redirect(url_for('index'))

if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO usuarios (username, password, role) VALUES (%s, %s, %s)', (username, password, role))
    conn.commit()
    cur.close()
    conn.close()

    flash('Usuário criado com sucesso!', 'success')
    return redirect(url_for('list_users'))

return render_template('create_user.html')

@app.route('/admin/users/edit/int:id', methods=['GET', 'POST']) def edit_user(id): if session.get('role') != 'admin': return redirect(url_for('index'))

conn = get_db_connection()
cur = conn.cursor()

if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    cur.execute('UPDATE usuarios SET username = %s, password = %s, role = %s WHERE id = %s', (username, password, role, id))
    conn.commit()
    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('list_users'))

cur.execute('SELECT * FROM usuarios WHERE id = %s', (id,))
user = cur.fetchone()
cur.close()
conn.close()

return render_template('edit_user.html', user=user)

if name == 'main': app.run(debug=True)

