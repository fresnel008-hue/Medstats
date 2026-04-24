from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_verified = db.Column(db.Boolean, default=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    donnees = db.relationship('HealthData', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)


class HealthData(db.Model):
    __tablename__ = 'health_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    poids = db.Column(db.Float, default=0)
    taille = db.Column(db.Float, default=0)
    imc = db.Column(db.Float, default=0)
    tension_systolique = db.Column(db.Integer, default=0)
    tension_diastolique = db.Column(db.Integer, default=0)
    frequence_cardiaque = db.Column(db.Integer, default=0)
    heures_sommeil = db.Column(db.Float, default=0)
    qualite_sommeil = db.Column(db.Integer, default=3)
    activite_physique = db.Column(db.Integer, default=0)
    verres_eau = db.Column(db.Integer, default=0)
    calories = db.Column(db.Integer, default=0)
    niveau_stress = db.Column(db.Integer, default=3)
    niveau_humeur = db.Column(db.Integer, default=3)
    niveau_energie = db.Column(db.Integer, default=3)
    maux_tete = db.Column(db.Boolean, default=False)
    fatigue = db.Column(db.Boolean, default=False)
    douleurs = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default='')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(300))
    type = db.Column(db.String(50), default='info')
    lu = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)