from flask import Blueprint, render_template, session, redirect
from extensions import db
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__)


@dashboard.route("/dashboard")
def index():
    from models import User, HealthData, Notification
    from services.stats import calculer_stats
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    donnees = HealthData.query.filter_by(
        user_id=session["user_id"]
    ).order_by(HealthData.date.desc()).all()

    notifs = Notification.query.filter_by(
        user_id=session["user_id"], lu=False
    ).order_by(Notification.date.desc()).all()

    stats = calculer_stats(donnees) if donnees else None

    il_y_a_7j = datetime.utcnow() - timedelta(days=7)
    donnees_7j = HealthData.query.filter(
        HealthData.user_id == session["user_id"],
        HealthData.date >= il_y_a_7j
    ).order_by(HealthData.date.asc()).all()

    derniere = donnees[0] if donnees else None

    return render_template("dashboard/index.html",
        user=user, donnees=donnees, stats=stats,
        notifs=notifs, donnees_7j=donnees_7j,
        derniere=derniere, total=len(donnees)
    )


@dashboard.route("/notif/lire/<int:notif_id>")
def lire_notif(notif_id):
    from models import Notification
    if "user_id" not in session:
        return redirect("/login")

    notif = Notification.query.get(notif_id)
    if notif and notif.user_id == session["user_id"]:
        notif.lu = True
        db.session.commit()

    return redirect("/dashboard")