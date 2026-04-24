from flask import Blueprint, render_template, request, redirect, session
from extensions import db
from datetime import datetime

collecte = Blueprint('collecte', __name__)


@collecte.route("/collecte", methods=["GET", "POST"])
def index():
    from models import HealthData, Notification
    from services.scoring import calculer_score
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        try:
            poids = float(request.form.get("poids") or 0)
            taille = float(request.form.get("taille") or 0)
            imc = round(poids / ((taille / 100) ** 2), 2) if taille > 0 else 0

            data = HealthData(
                user_id=session["user_id"],
                poids=poids, taille=taille, imc=imc,
                tension_systolique=int(request.form.get("tension_systolique") or 0),
                tension_diastolique=int(request.form.get("tension_diastolique") or 0),
                frequence_cardiaque=int(request.form.get("frequence_cardiaque") or 0),
                heures_sommeil=float(request.form.get("heures_sommeil") or 0),
                qualite_sommeil=int(request.form.get("qualite_sommeil") or 3),
                activite_physique=int(request.form.get("activite_physique") or 0),
                verres_eau=int(request.form.get("verres_eau") or 0),
                calories=int(request.form.get("calories") or 0),
                niveau_stress=int(request.form.get("niveau_stress") or 3),
                niveau_humeur=int(request.form.get("niveau_humeur") or 3),
                niveau_energie=int(request.form.get("niveau_energie") or 3),
                maux_tete=request.form.get("maux_tete") == "oui",
                fatigue=request.form.get("fatigue") == "oui",
                douleurs=request.form.get("douleurs") == "oui",
                notes=request.form.get("notes")
            )
            db.session.add(data)
            db.session.commit()

            alertes = []
            if imc >= 30:
                alertes.append("⚠️ IMC indique une obésité. Consultez un médecin.")
            elif imc >= 25:
                alertes.append("⚠️ IMC indique un surpoids.")
            elif 0 < imc < 18.5:
                alertes.append("⚠️ IMC indique une insuffisance pondérale.")
            if data.tension_systolique > 140:
                alertes.append("⚠️ Tension artérielle élevée !")
            if data.heures_sommeil < 6:
                alertes.append("😴 Sommeil insuffisant. Visez 7-8h.")
            if data.niveau_stress >= 4:
                alertes.append("😰 Stress élevé. Reposez-vous.")
            if data.verres_eau < 6:
                alertes.append("💧 Buvez plus d'eau !")

            for alerte in alertes:
                notif = Notification(
                    user_id=session["user_id"],
                    message=alerte,
                    type="alerte"
                )
                db.session.add(notif)
            db.session.commit()

            return redirect(f"/analyse/{data.id}")

        except Exception as e:
            return render_template("collecte/index.html", error=str(e))

    return render_template("collecte/index.html")