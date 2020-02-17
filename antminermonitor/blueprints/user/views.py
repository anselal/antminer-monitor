from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from antminermonitor.blueprints.user.forms import LoginForm, PasswordResetForm
from antminermonitor.blueprints.user.models import User
from antminermonitor.database import db_session
from lib.util_url import is_safe_url

user = Blueprint('user', __name__, template_folder='templates')


@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                print(form.remember.data)
                login_user(user, remember=form.remember.data)
                if 'next' in session:
                    next = session['next']
                    if is_safe_url(next):
                        return redirect(next)
                return redirect(url_for('antminer.miners'))
        flash("[ERROR] Invalid username or password", "error")
        return render_template('user/login.html', form=form)

    if current_user.is_authenticated:
        return redirect(url_for('antminer.miners'))

    return render_template('user/login.html', form=form)


@user.route('/password_update', methods=['GET', 'POST'])
@login_required
def password_update():
    form = PasswordResetForm()
    form.username.choices = [(u.username, u.username)
                             for u in User.query.all()]
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            password = form.password.data
            user.set_password(password)
            db_session.commit()
            flash(
                "[INFO] Password updated for user '{}'".format(user.username),
                "info")
            next = request.args.get('next')
            if not is_safe_url(next):
                abort(400)
            return redirect(next or url_for('user.password_update'))
        flash("[ERROR] User '{}' does not exist".format(form.username.data),
              "error")
        return render_template('user/password_update.html', form=form)

    return render_template('user/password_update.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('antminer.miners'))
