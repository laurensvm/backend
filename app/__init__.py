from flask import Flask
# from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config


# mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    # mail.init_app(app)

    with app.app_context():
        db.init_app(app)    
    
    @app.before_first_request
    def initialize_database():
        db.create_all()

    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    migrate.init_app(app, db)
    login_manager.init_app(app)


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')


    return app

