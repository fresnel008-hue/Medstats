from flask import Blueprint, render_template, session, redirect, send_file
from extensions import db

analyse = Blueprint('analyse', __name__)


@analyse.route("/analyse/<int:data_id>")
def detail(data_id):
    from models import User, HealthData
    from services.stats import calculer_stats
    from services.scoring import calculer_score
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    d = HealthData.query.get(data_id)
    toutes = HealthData.query.filter_by(user_id=session["user_id"]).all()

    score, niveau, couleur, emoji = calculer_score(d)
    recommandations = generer_recommandations(d)
    stats = calculer_stats(toutes) if toutes else None

    stress_historique = [x.niveau_stress for x in toutes]
    sommeil_historique = [x.heures_sommeil for x in toutes]
    imc_historique = [x.imc for x in toutes]
    humeur_historique = [x.niveau_humeur for x in toutes]
    labels = [x.date.strftime('%d/%m') for x in toutes]

    return render_template("analyse/index.html",
        user=user, d=d, score=score, niveau=niveau,
        couleur=couleur, emoji=emoji,
        recommandations=recommandations, stats=stats,
        stress_historique=stress_historique,
        sommeil_historique=sommeil_historique,
        imc_historique=imc_historique,
        humeur_historique=humeur_historique,
        labels=labels, total=len(toutes)
    )


@analyse.route("/analyse")
def globale():
    from models import User, HealthData
    from services.stats import calculer_stats
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    donnees = HealthData.query.filter_by(
        user_id=session["user_id"]
    ).order_by(HealthData.date.asc()).all()

    if not donnees:
        return render_template("analyse/globale.html", user=user, donnees=[])

    stats = calculer_stats(donnees)
    labels = [x.date.strftime('%d/%m/%Y') for x in donnees]

    return render_template("analyse/globale.html",
        user=user, donnees=donnees, stats=stats,
        labels=labels,
        stress=[x.niveau_stress for x in donnees],
        sommeil=[x.heures_sommeil for x in donnees],
        imc=[x.imc for x in donnees],
        humeur=[x.niveau_humeur for x in donnees],
        energie=[x.niveau_energie for x in donnees],
        poids=[x.poids for x in donnees],
        total=len(donnees)
    )


@analyse.route("/export-pdf")
def export_pdf():
    from models import User, HealthData
    from services.stats import calculer_stats
    from services.pdf import generer_pdf
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    donnees = HealthData.query.filter_by(user_id=session["user_id"]).all()
    stats = calculer_stats(donnees) if donnees else None
    buffer = generer_pdf(user, donnees, stats)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"rapport_{user.username}.pdf",
        mimetype='application/pdf'
    )


@analyse.route("/export-csv")
def export_csv():
    from models import User, HealthData
    import csv, io
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    donnees = HealthData.query.filter_by(user_id=session["user_id"]).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date','Poids','Taille','IMC','Tension Sys','Tension Dia',
        'FC','Sommeil','Qualite Sommeil','Activite','Eau','Calories',
        'Stress','Humeur','Energie','Maux tete','Fatigue','Douleurs','Notes'])

    for d in donnees:
        writer.writerow([
            d.date.strftime('%d/%m/%Y'), d.poids, d.taille, d.imc,
            d.tension_systolique, d.tension_diastolique, d.frequence_cardiaque,
            d.heures_sommeil, d.qualite_sommeil, d.activite_physique,
            d.verres_eau, d.calories, d.niveau_stress, d.niveau_humeur,
            d.niveau_energie, d.maux_tete, d.fatigue, d.douleurs, d.notes
        ])

    bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
    return send_file(bytes_output, as_attachment=True,
        download_name=f"donnees_{user.username}.csv", mimetype='text/csv')


def generer_recommandations(d):
    recommandations = []
    if d.imc > 0:
        if d.imc >= 30:
            recommandations.append({"type": "danger", "icon": "⚠️", "texte": f"IMC {d.imc} — Obésité. Consultez un médecin."})
        elif d.imc >= 25:
            recommandations.append({"type": "warning", "icon": "⚠️", "texte": f"IMC {d.imc} — Surpoids."})
        elif d.imc < 18.5:
            recommandations.append({"type": "warning", "icon": "⚠️", "texte": f"IMC {d.imc} — Insuffisance pondérale."})
        else:
            recommandations.append({"type": "success", "icon": "✅", "texte": f"IMC {d.imc} — Poids normal !"})
    if d.tension_systolique > 140:
        recommandations.append({"type": "danger", "icon": "❤️", "texte": "Tension élevée. Réduisez le sel."})
    elif d.tension_systolique > 0:
        recommandations.append({"type": "success", "icon": "❤️", "texte": "Tension normale !"})
    if d.heures_sommeil < 6:
        recommandations.append({"type": "danger", "icon": "😴", "texte": "Sommeil insuffisant. Visez 7-8h."})
    elif d.heures_sommeil >= 7:
        recommandations.append({"type": "success", "icon": "😴", "texte": "Bonne durée de sommeil !"})
    if d.niveau_stress >= 4:
        recommandations.append({"type": "danger", "icon": "😰", "texte": "Stress élevé. Méditez ou faites du sport."})
    if d.verres_eau < 6:
        recommandations.append({"type": "warning", "icon": "💧", "texte": f"{d.verres_eau} verres d'eau. Buvez 8 verres/jour."})
    if d.activite_physique < 30:
        recommandations.append({"type": "warning", "icon": "🏃", "texte": "Activité insuffisante. Visez 30min/jour."})
    else:
        recommandations.append({"type": "success", "icon": "🏃", "texte": "Bonne activité physique !"})
    return recommandations