from flask import jsonify
from ..exceptions import ValidationError
from . import controllers


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 403
    return response

def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response

def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def forbidden():
    response = jsonify({'error': 'forbidden', 'message': 'You have insufficient rights to perform this operation'})
    response.status_code = 403
    return response

def already_exists(message):
    response = jsonify({'error': 'already_exists', 'message': message })
    response.status_code = 409
    return response

def success(message):
    response = jsonify({'success': 'OK', 'message': message})
    response.status_code = 200
    return response

@controllers.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])