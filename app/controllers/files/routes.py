from flask import jsonify, g, request

from . import files
from ..authentication import auth
from ...models import File

@files.route("/", methods=["POST"])
@auth.login_required
def get_files_in_directory():
    pass
