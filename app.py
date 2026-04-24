from flask import Flask
from config import Config
from extensions import db, bcrypt, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

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

    with app.app_context():
        db.create_all()

    return app

app = create_app()
@app.route("/init-db")
def init_db():
    with app.app_context():
        db.create_all()
    return "Tables créées avec succès !"

if __name__ == "__main__":
    app.run(debug=True)