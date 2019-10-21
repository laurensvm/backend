from flask import Blueprint

controllers = Blueprint('controllers', __name__)

from .authentication import authentication
from . import images
from . import videos
from . import filesystem