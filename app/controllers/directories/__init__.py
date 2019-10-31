from flask import Blueprint

directories = Blueprint('directories', __name__)

from . import routes