from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            date_applied TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        company = request.form['company']
        role = request.form['role']
        status = request.form['status']
        date_applied = request.form['date_applied']
        
        cursor.execute('INSERT INTO jobs (company, role, status, date_applied) VALUES (?, ?, ?, ?)',
                       (company, role, status, date_applied))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM jobs')
    jobs = cursor.fetchall()
    
    cursor.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
    status_counts = cursor.fetchall()
    
    labels = [row['status'] for row in status_counts]
    data = [row['count'] for row in status_counts]

    conn.close()
    return render_template('index.html', jobs=jobs, labels=labels, data=data)

@app.route('/delete/<int:job_id>')
def delete_job(job_id):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if request.method == 'POST':
        company = request.form['company']
        role = request.form['role']
        status = request.form['status']
        date_applied = request.form['date_applied']
        
        cursor.execute('''
            UPDATE jobs SET company = ?, role = ?, status = ?, date_applied = ?
            WHERE id = ?
        ''', (company, role, status, date_applied, job_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    return render_template('edit.html', job=job)

if __name__ == '_main_':
    app.run(debug=True)