from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g, request, current_app

from . import authentication
from ..statuscodes import unauthorized, success, bad_request
from ...models import User

auth = HTTPBasicAuth()

@authentication.before_app_first_request
def create_user():
    # Create superuser
    email = current_app.config["ADMIN_EMAIL"]
    user =  User.query.filter_by(email=email).first()

    if not user:
        User.create_superuser()


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
            return unauthorized("Unconfirmed Account")
    except AttributeError as e:
        print(e)

@authentication.route('/token/')
@auth.login_required
def get_token():
    expiration = int(current_app["TOKEN_EXPIRATION"]) or 3600

    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=expiration),
        'expiration': expiration
        })

@authentication.route('/users/', methods=["GET"])
@auth.login_required
def get_users():
    users = User.query.all()
    return jsonify({ 'users': [ user.json() for user in users ] })

@authentication.route('/users/create/', methods=["POST"])
@auth.login_required
def create_user():
    if not g.current_user.admin:
        return unauthorized()

    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    if not User.unique(username, email):
        return bad_request("User with this username or email already exists")

    u = User(username=username, email=email, password=password)
    u.save()

    return success("User successfully created")

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
    return unauthorized()

# @authentication.route('/users/update/<int:id>/', methods=["POST"])
# @auth.login_required
# def update_user(id):
#     if g.current_user.admin:
#         u = User.query.filter_by(id=id).first()
#         if u:
#             attr = request.json.get("attribute")
#             value = request.json.get("value")
#             print(list(u.__dict__.keys()))
#             # FIX
#
#             return success("User attribute {0} succesfully updates to {1}".format(attr, value))
#         return bad_request("User does not exist")
#     return unauthorized()