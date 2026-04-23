import pandas as pd
import numpy as np
from database import get_all_etudiants

UES_DISPONIBLES = [
    "Mathématiques", "Algorithmique", "Programmation Python",
    "Bases de données", "Réseaux informatiques", "Analyse",
    "Probabilités & Statistiques", "Systèmes d'exploitation",
    "Génie logiciel", "Intelligence artificielle",
    "Anglais technique", "Communication & Expression",
    "Architecture des ordinateurs", "Web & Internet",
    "Sécurité informatique"
]

FILIERES = [
    "Informatique", "Génie Civil", "Électronique",
    "Gestion", "Droit", "Médecine", "Économie",
    "Lettres modernes", "Physique", "Chimie"
]

def calculer_score(data):
    score = 0

    # Moyenne académique → 40 pts
    moy = float(data.get('moyenne', 0))
    if moy >= 16:
        score += 40
    elif moy >= 14:
        score += 33
    elif moy >= 12:
        score += 25
    elif moy >= 10:
        score += 15
    else:
        score += 5

    # Conditions d'études → 25 pts
    internet = data.get('acces_internet', 'Non')
    ordi = data.get('possede_ordi', 'Non')
    lieu = data.get('lieu_etude', 'Autre')
    cond = 0
    if internet == 'Oui': cond += 10
    elif internet == 'Parfois': cond += 5
    if ordi == 'Oui': cond += 10
    if lieu in ['Bibliothèque', 'Domicile calme']: cond += 5
    elif lieu == 'Campus': cond += 3
    score += min(cond, 25)

    # Satisfaction cours → 20 pts
    sat = int(data.get('satisfaction_cours', 1))
    score += round((sat / 5) * 20)

    # Distance campus → 15 pts
    dist = data.get('distance_campus', 'Plus de 10 km')
    dist_pts = {'Moins de 1 km': 15, '1 à 5 km': 12, '5 à 10 km': 7, 'Plus de 10 km': 3}
    score += dist_pts.get(dist, 3)

    score = min(score, 100)

    if score >= 80:
        badge = 'Excellence'
    elif score >= 60:
        badge = 'Bon profil'
    else:
        badge = 'À encourager'

    return round(score, 2), badge

def get_stats_globales():
    data = get_all_etudiants()
    if not data:
        return None
    df = pd.DataFrame(data)

    stats = {
        'total': len(df),
        'moyenne_generale': round(df['moyenne'].mean(), 2),
        'mediane_moyenne': round(df['moyenne'].median(), 2),
        'ecart_type': round(df['moyenne'].std(), 2),
        'min_moyenne': round(df['moyenne'].min(), 2),
        'max_moyenne': round(df['moyenne'].max(), 2),
        'score_moyen': round(df['score_profil'].mean(), 2),
    }

    stats['repartition_sexe'] = df['sexe'].value_counts().to_dict()
    stats['repartition_niveau'] = df['niveau'].value_counts().to_dict()
    stats['repartition_filiere'] = df['filiere'].value_counts().to_dict()
    stats['repartition_badge'] = df['badge'].value_counts().to_dict()

    ue_facile_counts = df['ue_facile'].value_counts()
    stats['top_ue_faciles'] = ue_facile_counts.head(5).to_dict()

    ue_difficile_counts = df['ue_difficile'].value_counts()
    stats['top_ue_difficiles'] = ue_difficile_counts.head(5).to_dict()

    stats['satisfaction_moyenne'] = round(df['satisfaction_cours'].mean(), 2)
    stats['ambiance_moyenne'] = round(df['ambiance_classe'].mean(), 2)

    return stats

def get_classement_filieres():
    data = get_all_etudiants()
    if not data:
        return []
    df = pd.DataFrame(data)
    classement = df.groupby('filiere').agg(
        score_moyen=('score_profil', 'mean'),
        nb_etudiants=('id', 'count'),
        moyenne_academique=('moyenne', 'mean'),
        satisfaction_moyenne=('satisfaction_cours', 'mean')
    ).reset_index()
    classement = classement.sort_values('score_moyen', ascending=False).reset_index(drop=True)
    classement['rang'] = classement.index + 1
    classement['score_moyen'] = classement['score_moyen'].round(2)
    classement['moyenne_academique'] = classement['moyenne_academique'].round(2)
    classement['satisfaction_moyenne'] = classement['satisfaction_moyenne'].round(2)
    return classement.to_dict(orient='records')

def get_evolution_scores():
    data = get_all_etudiants()
    if not data:
        return []
    df = pd.DataFrame(data)
    df['date_soumission'] = pd.to_datetime(df['date_soumission'])
    df = df.sort_values('date_soumission')
    result = df[['date_soumission', 'score_profil', 'nom', 'filiere']].copy()
    result['date_soumission'] = result['date_soumission'].dt.strftime('%d/%m %H:%M')
    return result.to_dict(orient='records')