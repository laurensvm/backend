from flask import Blueprint

directory = Blueprint('directory', __name__)

from . import routes