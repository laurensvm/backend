from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g, request, current_app

from . import authentication
from ..statuscodes import unauthorized, forbidden, success, bad_request
from ...models import User
from ... import db

auth = HTTPBasicAuth()


@authentication.before_app_first_request
def create_user():
    # Create superuser

    # Get the email from the config file
    email = current_app.config["ADMIN_EMAIL"]

    user =  User.query.filter_by(email=email).first()
    if not user:

        # Get the environment variables from config
        username = current_app.config["ADMIN_USERNAME"]
        password = current_app.config["ADMIN_PASSWORD"]

        u = User(username=username, email=email, password=password)
        u.admin = True
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


@authentication.before_request
@auth.login_required
def before_request():
    try:
        if g.current_user.is_anonymous:
            return forbidden("Unconfirmed Account")
    except AttributeError as e:
        print(e)

@authentication.route('/token/')
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600),
        'expiration': 3600
        })

@authentication.route('/users/', methods=["GET"])
@auth.login_required
def get_users():
    users = User.query.all()
    return jsonify({ 'users': [ user.to_json() for user in users ] })

@authentication.route('/users/create/', methods=["POST"])
@auth.login_required
def create_user():
    if g.current_user.admin:
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")

        if not User.exists(username, email):
            u = User(username=username, email=email, password=password)
            db.session.add(u)
            db.session.commit()
            return success("User successfully created")
        return bad_request("User with this username or email already exists")
    return forbidden()

@authentication.route('/users/delete/', methods=["POST"])
@auth.login_required
def delete_user():
    if g.current_user.admin:
        username = request.json.get("username")

        u = User.query.filter_by(username=username).first()
        if u:
            u.remove()
            return success("User with username {0} is successfully deleted".format(username))
        return bad_request("User does not exist")
    return forbidden()
