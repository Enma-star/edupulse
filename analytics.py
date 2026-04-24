from statistics import mean, median, stdev
from collections import Counter
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

    moy = float(data.get('moyenne', 0))
    if moy >= 16:      score += 40
    elif moy >= 14:    score += 33
    elif moy >= 12:    score += 25
    elif moy >= 10:    score += 15
    else:              score += 5

    internet = data.get('acces_internet', 'Non')
    ordi = data.get('possede_ordi', 'Non')
    lieu = data.get('lieu_etude', 'Autre')
    cond = 0
    if internet == 'Oui':    cond += 10
    elif internet == 'Parfois': cond += 5
    if ordi == 'Oui':        cond += 10
    if lieu in ['Bibliothèque', 'Domicile calme']: cond += 5
    elif lieu == 'Campus':   cond += 3
    score += min(cond, 25)

    sat = int(data.get('satisfaction_cours', 1))
    score += round((sat / 5) * 20)

    dist = data.get('distance_campus', 'Plus de 10 km')
    dist_pts = {
        'Moins de 1 km': 15,
        '1 à 5 km': 12,
        '5 à 10 km': 7,
        'Plus de 10 km': 3
    }
    score += dist_pts.get(dist, 3)
    score = min(score, 100)

    if score >= 80:    badge = 'Excellence'
    elif score >= 60:  badge = 'Bon profil'
    else:              badge = 'À encourager'

    return round(score, 2), badge

def get_stats_globales():
    data = get_all_etudiants()
    if not data:
        return None

    moyennes = [d['moyenne'] for d in data]
    scores = [d['score_profil'] for d in data]
    satisfactions = [d['satisfaction_cours'] for d in data]
    ambiances = [d['ambiance_classe'] for d in data]

    stats = {
        'total': len(data),
        'moyenne_generale': round(mean(moyennes), 2),
        'mediane_moyenne': round(median(moyennes), 2),
        'ecart_type': round(stdev(moyennes), 2) if len(moyennes) > 1 else 0.0,
        'min_moyenne': round(min(moyennes), 2),
        'max_moyenne': round(max(moyennes), 2),
        'score_moyen': round(mean(scores), 2),
        'satisfaction_moyenne': round(mean(satisfactions), 2),
        'ambiance_moyenne': round(mean(ambiances), 2),
    }

    stats['repartition_sexe'] = dict(Counter(d['sexe'] for d in data))
    stats['repartition_niveau'] = dict(Counter(d['niveau'] for d in data))
    stats['repartition_filiere'] = dict(Counter(d['filiere'] for d in data))
    stats['repartition_badge'] = dict(Counter(d['badge'] for d in data))

    ue_faciles = Counter(d['ue_facile'] for d in data)
    ue_difficiles = Counter(d['ue_difficile'] for d in data)
    stats['top_ue_faciles'] = dict(ue_faciles.most_common(5))
    stats['top_ue_difficiles'] = dict(ue_difficiles.most_common(5))

    return stats

def get_classement_filieres():
    data = get_all_etudiants()
    if not data:
        return []

    filieres = {}
    for d in data:
        f = d['filiere']
        if f not in filieres:
            filieres[f] = {'scores': [], 'moyennes': [], 'satisfactions': [], 'nb': 0}
        filieres[f]['scores'].append(d['score_profil'])
        filieres[f]['moyennes'].append(d['moyenne'])
        filieres[f]['satisfactions'].append(d['satisfaction_cours'])
        filieres[f]['nb'] += 1

    classement = []
    for filiere, val in filieres.items():
        classement.append({
            'filiere': filiere,
            'score_moyen': round(mean(val['scores']), 2),
            'moyenne_academique': round(mean(val['moyennes']), 2),
            'satisfaction_moyenne': round(mean(val['satisfactions']), 2),
            'nb_etudiants': val['nb'],
        })

    classement.sort(key=lambda x: x['score_moyen'], reverse=True)
    for i, f in enumerate(classement):
        f['rang'] = i + 1

    return classement

def get_evolution_scores():
    data = get_all_etudiants()
    if not data:
        return []
    return [
        {
            'date_soumission': d['date_soumission'],
            'score_profil': d['score_profil'],
            'nom': d['nom'],
            'filiere': d['filiere']
        }
        for d in data
    ]