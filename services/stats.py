import numpy as np
from scipy import stats as scipy_stats


def calculer_stats(donnees):
    if not donnees:
        return None

    def safe_mean(values):
        vals = [v for v in values if v is not None and v > 0]
        return round(float(np.mean(vals)), 2) if vals else 0

    def safe_std(values):
        vals = [v for v in values if v is not None and v > 0]
        return round(float(np.std(vals)), 2) if vals else 0

    def safe_median(values):
        vals = [v for v in values if v is not None and v > 0]
        return round(float(np.median(vals)), 2) if vals else 0

    def safe_min(values):
        vals = [v for v in values if v is not None and v > 0]
        return round(float(np.min(vals)), 2) if vals else 0

    def safe_max(values):
        vals = [v for v in values if v is not None and v > 0]
        return round(float(np.max(vals)), 2) if vals else 0

    def safe_quartiles(values):
        vals = [v for v in values if v is not None and v > 0]
        if len(vals) < 2:
            return 0, 0
        q1 = round(float(np.percentile(vals, 25)), 2)
        q3 = round(float(np.percentile(vals, 75)), 2)
        return q1, q3

    def tendance(values):
        vals = [v for v in values if v is not None and v > 0]
        if len(vals) < 2:
            return "stable"
        diff = vals[-1] - vals[0]
        if diff > 0.5:
            return "hausse"
        elif diff < -0.5:
            return "baisse"
        return "stable"

    # Extraction des valeurs
    poids = [d.poids for d in donnees]
    imc = [d.imc for d in donnees]
    stress = [d.niveau_stress for d in donnees]
    sommeil = [d.heures_sommeil for d in donnees]
    humeur = [d.niveau_humeur for d in donnees]
    energie = [d.niveau_energie for d in donnees]
    fc = [d.frequence_cardiaque for d in donnees]
    tension_sys = [d.tension_systolique for d in donnees]
    eau = [d.verres_eau for d in donnees]
    activite = [d.activite_physique for d in donnees]

    # Quartiles
    q1_stress, q3_stress = safe_quartiles(stress)
    q1_sommeil, q3_sommeil = safe_quartiles(sommeil)
    q1_imc, q3_imc = safe_quartiles(imc)

    # Corrélation stress/sommeil
    stress_vals = [v for v in stress if v is not None and v > 0]
    sommeil_vals = [v for v in sommeil if v is not None and v > 0]
    correlation_stress_sommeil = 0
    if len(stress_vals) >= 3 and len(sommeil_vals) >= 3:
        min_len = min(len(stress_vals), len(sommeil_vals))
        corr, _ = scipy_stats.pearsonr(
            stress_vals[:min_len],
            sommeil_vals[:min_len]
        )
        correlation_stress_sommeil = round(corr, 2)

    return {
        # Poids & IMC
        "poids_moyen": safe_mean(poids),
        "poids_min": safe_min(poids),
        "poids_max": safe_max(poids),
        "imc_moyen": safe_mean(imc),
        "imc_min": safe_min(imc),
        "imc_max": safe_max(imc),
        "imc_std": safe_std(imc),

        # Stress
        "stress_moyen": safe_mean(stress),
        "stress_median": safe_median(stress),
        "stress_std": safe_std(stress),
        "stress_min": safe_min(stress),
        "stress_max": safe_max(stress),
        "q1_stress": q1_stress,
        "q3_stress": q3_stress,
        "tendance_stress": tendance(stress),

        # Sommeil
        "sommeil_moyen": safe_mean(sommeil),
        "sommeil_median": safe_median(sommeil),
        "sommeil_std": safe_std(sommeil),
        "sommeil_min": safe_min(sommeil),
        "sommeil_max": safe_max(sommeil),
        "q1_sommeil": q1_sommeil,
        "q3_sommeil": q3_sommeil,
        "tendance_sommeil": tendance(sommeil),

        # Humeur & Energie
        "humeur_moyenne": safe_mean(humeur),
        "energie_moyenne": safe_mean(energie),
        "tendance_humeur": tendance(humeur),

        # Cardiaque
        "fc_moyenne": safe_mean(fc),
        "tension_moyenne": safe_mean(tension_sys),

        # Hydratation & Activité
        "eau_moyenne": safe_mean(eau),
        "activite_moyenne": safe_mean(activite),

        # Corrélations
        "correlation_stress_sommeil": correlation_stress_sommeil,

        # Total
        "total": len(donnees)
    }