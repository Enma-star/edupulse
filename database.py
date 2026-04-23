import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'edupulse.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS etudiants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            age INTEGER NOT NULL,
            sexe TEXT NOT NULL,
            filiere TEXT NOT NULL,
            niveau TEXT NOT NULL,
            acces_internet TEXT NOT NULL,
            possede_ordi TEXT NOT NULL,
            lieu_etude TEXT NOT NULL,
            moyenne REAL NOT NULL,
            matiere_preferee TEXT NOT NULL,
            ue_facile TEXT NOT NULL,
            ue_difficile TEXT NOT NULL,
            emploi_etudiant TEXT NOT NULL,
            distance_campus TEXT NOT NULL,
            satisfaction_cours INTEGER NOT NULL,
            ambiance_classe INTEGER NOT NULL,
            score_profil REAL NOT NULL,
            badge TEXT NOT NULL,
            date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_etudiant(data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO etudiants 
        (nom, age, sexe, filiere, niveau, acces_internet, possede_ordi,
         lieu_etude, moyenne, matiere_preferee, ue_facile, ue_difficile,
         emploi_etudiant, distance_campus, satisfaction_cours, ambiance_classe,
         score_profil, badge)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        data['nom'], data['age'], data['sexe'], data['filiere'], data['niveau'],
        data['acces_internet'], data['possede_ordi'], data['lieu_etude'],
        data['moyenne'], data['matiere_preferee'], data['ue_facile'],
        data['ue_difficile'], data['emploi_etudiant'], data['distance_campus'],
        data['satisfaction_cours'], data['ambiance_classe'],
        data['score_profil'], data['badge']
    ))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_all_etudiants():
    conn = get_db()
    rows = conn.execute('SELECT * FROM etudiants ORDER BY date_soumission DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_etudiant_by_id(eid):
    conn = get_db()
    row = conn.execute('SELECT * FROM etudiants WHERE id=?', (eid,)).fetchone()
    conn.close()
    return dict(row) if row else None