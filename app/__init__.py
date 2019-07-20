from flask import Flask
# from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Background task
# move code
# from .tasks import test, get_test, get_liked_tracks
import sys
import os
import threading
import atexit

POOL_TIME = 5
thread = threading.Thread()



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

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/')


    # Threading
    # move code

    # @atexit.register
    # def interrupt():
    #     global thread
    #     print("SHUTTING DOWN THREAD")
    #     thread.cancel()

    # def background_tasks():
    #     get_test()

    #     # Set the next thread to happen
    #     thread = threading.Timer(POOL_TIME, background_tasks, ())
    #     thread.start()

    # def run_background_tasks():
    #     # Do initialisation stuff here
    #     global thread
    #     # Create your thread
    #     thread = threading.Timer(POOL_TIME, background_tasks, ())
    #     thread.start()

    # # Initiate
    # run_background_tasks()


    return app

