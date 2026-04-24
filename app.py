from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import init_db, insert_etudiant, get_all_etudiants, get_etudiant_by_id
from analytics import calculer_score, get_stats_globales, get_classement_filieres, get_evolution_scores, UES_DISPONIBLES, FILIERES
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'edupulse_secret_2024')

@app.before_request
def setup():
    init_db()

@app.route('/')
def index():
    stats = get_stats_globales()
    return render_template('index.html', stats=stats)

@app.route('/formulaire')
def formulaire():
    return render_template('formulaire.html', ues=UES_DISPONIBLES, filieres=FILIERES)

@app.route('/soumettre', methods=['POST'])
def soumettre():
    try:
        data = {
            'nom': request.form.get('nom', '').strip(),
            'age': int(request.form.get('age', 0)),
            'sexe': request.form.get('sexe', ''),
            'filiere': request.form.get('filiere', ''),
            'niveau': request.form.get('niveau', ''),
            'acces_internet': request.form.get('acces_internet', ''),
            'possede_ordi': request.form.get('possede_ordi', ''),
            'lieu_etude': request.form.get('lieu_etude', ''),
            'moyenne': float(request.form.get('moyenne', 0)),
            'matiere_preferee': request.form.get('matiere_preferee', ''),
            'ue_facile': request.form.get('ue_facile', ''),
            'ue_difficile': request.form.get('ue_difficile', ''),
            'emploi_etudiant': request.form.get('emploi_etudiant', ''),
            'distance_campus': request.form.get('distance_campus', ''),
            'satisfaction_cours': int(request.form.get('satisfaction_cours', 1)),
            'ambiance_classe': int(request.form.get('ambiance_classe', 1)),
        }

        if not data['nom'] or data['age'] < 15 or data['moyenne'] < 0 or data['moyenne'] > 20:
            return render_template('formulaire.html', ues=UES_DISPONIBLES, filieres=FILIERES,
                                   erreur="Veuillez remplir correctement tous les champs.")

        score, badge = calculer_score(data)
        data['score_profil'] = score
        data['badge'] = badge

        eid = insert_etudiant(data)
        return redirect(url_for('profil', eid=eid))

    except Exception as e:
        return render_template('formulaire.html', ues=UES_DISPONIBLES, filieres=FILIERES,
                               erreur=f"Erreur : {str(e)}")

@app.route('/profil/<int:eid>')
def profil(eid):
    etudiant = get_etudiant_by_id(eid)
    if not etudiant:
        return redirect(url_for('index'))
    return render_template('profil.html', e=etudiant)

@app.route('/dashboard')
def dashboard():
    try:
        stats = get_stats_globales()
        classement = get_classement_filieres()
        evolution = get_evolution_scores()
        etudiants = get_all_etudiants()

        max_easy = 1
        max_hard = 1

        if stats and stats.get('top_ue_faciles'):
            max_easy = max(stats['top_ue_faciles'].values())
        if stats and stats.get('top_ue_difficiles'):
            max_hard = max(stats['top_ue_difficiles'].values())

        return render_template('dashboard.html',
            stats=stats,
            classement=classement,
            evolution=evolution,
            etudiants=etudiants,
            max_easy=max_easy,
            max_hard=max_hard
        )
    except Exception as e:
        return f"<h2>Erreur détectée :</h2><pre>{str(e)}</pre>", 500

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats_globales())

@app.route('/api/classement')
def api_classement():
    return jsonify(get_classement_filieres())

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
