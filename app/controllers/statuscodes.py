from flask import jsonify


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response

def _unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 403
    return response

def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response

def _not_found():
    response = jsonify({'error': 'not found', 'message': 'Your request did not match any data'})
    response.status_code = 404
    return response

def unauthorized():
    response = jsonify({'error': 'unauthorized', 'message': 'You have insufficient rights to perform this operation'})
    response.status_code = 403
    return response

def already_exists(message):
    response = jsonify({'error': 'already_exists', 'message': message })
    response.status_code = 409
    return response

def internal_error(message):
    response = jsonify({'error': 'internal_server_error', 'message': message})
    response.status_code = 500
    return response

def success(message):
    response = jsonify({'success': 'OK', 'message': message})
    response.status_code = 200
    return response
