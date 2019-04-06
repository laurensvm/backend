from flask import jsonify
from app import app

from .utilities import extract_excel_contents

@app.route('/')
@app.route('/index')
def index():
    objects = extract_excel_contents()
    return jsonify([o.serialize() for o in objects])