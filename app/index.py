from flask import jsonify
from app import app

from .utilities import extract_excel_contents

@app.route('/api/')
def api_get_list():
    objects = extract_excel_contents()
    return jsonify([o.serialize() for o in objects])

@app.route('/api/<int:id>')
def api_get_by_id(id):
    pass