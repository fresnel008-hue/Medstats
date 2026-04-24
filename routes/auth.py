from flask import Blueprint, render_template, request, redirect, session
from extensions import db, bcrypt, mail
from flask_mail import Message
from datetime import datetime
import secrets

auth = Blueprint('auth', __name__)


@auth.route("/")
def index():
    return redirect("/login")


@auth.route("/register", methods=["GET", "POST"])
def register():
    from models import User, Notification
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            return render_template("auth/register.html", error="Les mots de passe ne correspondent pas !")

        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template("auth/register.html", error="Cet email est déjà utilisé !")

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        notif = Notification(
            user_id=user.id,
            message=f"Bienvenue sur MedStats, {username} !",
            type="succes"
        )
        db.session.add(notif)
        db.session.commit()

        return redirect("/login")

    return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    from models import User
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            user.derniere_connexion = datetime.utcnow()
            db.session.commit()

            if user.role == "admin":
                return redirect("/admin")
            return redirect("/dashboard")

        return render_template("auth/login.html", error="Email ou mot de passe incorrect")

    return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    from models import User
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            token = secrets.token_urlsafe(32)
            session[f"reset_{token}"] = user.id
            reset_url = f"http://127.0.0.1:5000/reset-password/{token}"
            try:
                msg = Message(
                    subject="MedStats - Réinitialisation mot de passe",
                    recipients=[email],
                    body=f"Lien de réinitialisation :\n\n{reset_url}"
                )
                mail.send(msg)
            except:
                pass
        return render_template("auth/forgot_password.html",
            success="Si cet email existe, un lien a été envoyé.")

    return render_template("auth/forgot_password.html")


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    from models import User
    user_id = session.get(f"reset_{token}")
    if not user_id:
        return redirect("/login")

    user = User.query.get(user_id)

    if request.method == "POST":
        new_password = request.form.get("password")
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        session.pop(f"reset_{token}", None)
        return redirect("/login")

    return render_template("auth/reset_password.html")


@auth.route("/profil", methods=["GET", "POST"])
def profil():
    from models import User
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        nouveau_mdp = request.form.get("password")
        if nouveau_mdp:
            user.password = bcrypt.generate_password_hash(nouveau_mdp).decode('utf-8')
        db.session.commit()
        session["username"] = user.username
        return redirect("/profil")

    return render_template("auth/profil.html", user=user)