import os
from flask import Flask
from config import Config
from extensions import db, bcrypt, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from models import User, HealthData, Notification
        try:
            db.create_all()
            print("Tables créées avec succès !")
        except Exception as e:
            print(f"Erreur création tables: {e}")

        from routes.auth import auth
        from routes.dashboard import dashboard
        from routes.collecte import collecte
        from routes.analyse import analyse
        from routes.admin import admin

        app.register_blueprint(auth)
        app.register_blueprint(dashboard)
        app.register_blueprint(collecte)
        app.register_blueprint(analyse)
        app.register_blueprint(admin)

    return app


app = create_app()


@app.route("/init-db")
def init_db():
    from models import User, HealthData, Notification
    try:
        db.create_all()
        return "Tables créées avec succès !"
    except Exception as e:
        return f"Erreur : {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)