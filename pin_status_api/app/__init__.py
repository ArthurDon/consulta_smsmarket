from flask import Flask
from pin_status_api.routes.routes import return_status_blueprint, health_check_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(return_status_blueprint)
    app.register_blueprint(health_check_blueprint)
    return app
