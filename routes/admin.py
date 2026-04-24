from flask import Blueprint, render_template, session, redirect, request
from extensions import db
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        if session.get("role") != "admin":
            return redirect("/dashboard")
        return f(*args, **kwargs)
    return decorated


@admin.route("/admin")
@admin_required
def index():
    from models import User, HealthData, Notification
    from services.stats import calculer_stats
    users = User.query.order_by(User.date_inscription.desc()).all()
    total_donnees = HealthData.query.count()
    total_notifs = Notification.query.count()
    toutes_donnees = HealthData.query.all()
    stats_globales = calculer_stats(toutes_donnees) if toutes_donnees else None
    il_y_a_7j = datetime.utcnow() - timedelta(days=7)
    nouveaux = User.query.filter(User.date_inscription >= il_y_a_7j).count()

    return render_template("admin/index.html",
        users=users, total_users=len(users),
        total_donnees=total_donnees, total_notifs=total_notifs,
        stats_globales=stats_globales, nouveaux=nouveaux
    )


@admin.route("/admin/user/<int:user_id>")
@admin_required
def voir_user(user_id):
    from models import User, HealthData
    from services.stats import calculer_stats
    user = User.query.get(user_id)
    donnees = HealthData.query.filter_by(user_id=user_id).all()
    stats = calculer_stats(donnees) if donnees else None
    return render_template("admin/user.html",
        user=user, donnees=donnees, stats=stats, total=len(donnees))


@admin.route("/admin/user/<int:user_id>/supprimer")
@admin_required
def supprimer_user(user_id):
    from models import User, HealthData, Notification
    HealthData.query.filter_by(user_id=user_id).delete()
    Notification.query.filter_by(user_id=user_id).delete()
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect("/admin")


@admin.route("/admin/user/<int:user_id>/promouvoir")
@admin_required
def promouvoir_user(user_id):
    from models import User
    user = User.query.get(user_id)
    if user:
        user.role = "admin"
        db.session.commit()
    return redirect("/admin")


@admin.route("/admin/notifier", methods=["POST"])
@admin_required
def notifier_tous():
    from models import User, Notification
    message = request.form.get("message")
    type_notif = request.form.get("type", "info")
    users = User.query.all()
    for user in users:
        notif = Notification(user_id=user.id, message=message, type=type_notif)
        db.session.add(notif)
    db.session.commit()
    return redirect("/admin")