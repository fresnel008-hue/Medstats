def calculer_score(d):
    score = 100

    # IMC
    if d.imc > 0:
        if d.imc >= 30:
            score -= 20
        elif d.imc >= 25:
            score -= 10
        elif d.imc < 18.5:
            score -= 10

    # Tension artérielle
    if d.tension_systolique > 140:
        score -= 20
    elif d.tension_systolique > 120:
        score -= 10

    # Fréquence cardiaque
    if d.frequence_cardiaque > 100:
        score -= 10
    elif d.frequence_cardiaque < 50:
        score -= 5

    # Sommeil
    if d.heures_sommeil < 5:
        score -= 20
    elif d.heures_sommeil < 6:
        score -= 10
    elif d.heures_sommeil < 7:
        score -= 5

    # Stress
    if d.niveau_stress == 5:
        score -= 20
    elif d.niveau_stress == 4:
        score -= 10
    elif d.niveau_stress == 3:
        score -= 5

    # Humeur
    if d.niveau_humeur == 1:
        score -= 10
    elif d.niveau_humeur == 2:
        score -= 5

    # Hydratation
    if d.verres_eau < 4:
        score -= 10
    elif d.verres_eau < 6:
        score -= 5

    # Activité physique
    if d.activite_physique < 15:
        score -= 10
    elif d.activite_physique < 30:
        score -= 5

    # Symptômes
    if d.maux_tete:
        score -= 5
    if d.fatigue:
        score -= 5
    if d.douleurs:
        score -= 5

    # Score final
    score = max(0, min(100, score))

    # Niveau
    if score >= 80:
        niveau = "Excellent"
        couleur = "#28a745"
        emoji = "🟢"
    elif score >= 60:
        niveau = "Bon"
        couleur = "#17a2b8"
        emoji = "🔵"
    elif score >= 40:
        niveau = "Moyen"
        couleur = "#ffc107"
        emoji = "🟡"
    elif score >= 20:
        niveau = "Faible"
        couleur = "#fd7e14"
        emoji = "🟠"
    else:
        niveau = "Critique"
        couleur = "#dc3545"
        emoji = "🔴"

    return score, niveau, couleur, emoji