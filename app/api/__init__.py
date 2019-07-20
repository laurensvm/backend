from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication
from . import tracks
from . import images
from . import filesystem