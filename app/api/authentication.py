import sys

from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g
from . import api
from .statuscodes import unauthorized, forbidden
from ..models import User

from .. import db

auth = HTTPBasicAuth()


@api.before_app_first_request
def create_user():
    # Create superuser
    user =  User.query.filter_by(email="theexission@gmail.com").first()
    if not user:
        u = User(username="Laurens", email="theexission@gmail.com", password="passwd01")
        db.session.add(u)
        db.session.commit()

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.before_request
@auth.login_required
def before_request():
    try:
        if g.current_user.is_anonymous:
            return forbidden("Unconfirmed Account")
    except AttributeError as e:
        print(e)

@api.route('/token/')
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600),
        'expiration': 3600
        })
