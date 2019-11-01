from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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

    from .controllers import authentication
    app.register_blueprint(authentication, url_prefix='/auth')

    from .controllers import directory
    app.register_blueprint(directory, url_prefix='/directory')

    from .controllers import controllers
    app.register_blueprint(controllers, url_prefix='')

    return app

