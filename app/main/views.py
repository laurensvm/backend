from flask import redirect, url_for
from . import main
from ..api import api



@main.route("/")
def index():
    return redirect(url_for('api.index'))