from flask import redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return "login auth"



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():  
    return "/register"