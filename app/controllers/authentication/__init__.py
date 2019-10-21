from flask import Blueprint

authentication = Blueprint('auth', __name__)

from .routes import auth
