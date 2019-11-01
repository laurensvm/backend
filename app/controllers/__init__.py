from flask import Blueprint

controllers = Blueprint('controllers', __name__)

from .authentication import authentication
from .directories import directories
from .files import files
from . import images
from . import videos
from . import filesystem