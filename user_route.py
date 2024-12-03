import logging
from datetime import datetime, timezone

from flask import Blueprint, render_template, session, redirect, url_for, request, flash, make_response
from sqlalchemy import or_

from log_config import setup_logging
from models import User, Todo, Session
from utils import hash_password, verify_password, create_token, session_token_required

setup_logging()
logger = logging.getLogger(__name__)

user_router = Blueprint('user', __name__)


@user_router.route("/")
def index():
    if not session.get('user_name'):
        return redirect(url_for('user.login'))
    return redirect(url_for('user.dashboard'))


@user_router.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        logger.debug(f"Login attempt for username_or_email: {username_or_email}")

        with Session() as session_db:
            user = session_db.query(User).filter(
                or_(User.username == username_or_email, User.email == username_or_email)
            ).first()

            if not user or not verify_password(password, user.password):
                message = f"Invalid Username or Password: Failed login attempt for username: {username_or_email}."
                flash(message, "Error")
                logger.error(message)
                return redirect(url_for("user.login"))

            tokens = create_token(user.username)
            session['user_name'] = user.username
            session.permanent = True
            resp = make_response(redirect(url_for('user.dashboard')))
            resp.set_cookie('token', tokens["access_token"], httponly=True, secure=True)
            logger.info(f"User {user.fullname} logged in successfully.")
            return resp

    return render_template("login.html")


@user_router.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        logger.info(f"Signup attempt for username: {username}")

        with Session() as session_db:
            if session_db.query(User).filter_by(username=username).first():
                message = f"Username {username} already exists."
                flash(message, "Error")
                logger.error(message)
                return redirect(url_for("user.signup"))

            if session_db.query(User).filter_by(email=email).first():
                message = f"Email {email} already exists."
                flash(message, "Error")
                logger.error(message)
                return redirect(url_for("user.signup"))

            user = User(username=username, fullname=fullname, email=email, password=hash_password(password))
            session_db.add(user)
            session_db.commit()
            message = f"User {username} signed up successfully."
            flash(message, "Success")
            logger.info(message)
            return redirect(url_for("user.login"))

    return render_template("signup.html")


@user_router.route("/dashboard")
@session_token_required
def dashboard():
    username = session['user_name']
    with Session() as session_db:
        user = session_db.query(User).filter_by(username=username).first()
        #todos = session_db.query(Todo).filter_by(user_id=user.id).all()
        todos = session_db.query(Todo).filter_by(user_id=user.id, is_active=True).all()
        logger.info(f"Displaying dashboard for user {username}.")
        current_time = datetime.now(timezone.utc)
        return render_template("dashboard.html", user=user.fullname, todos=todos,now=current_time)


@user_router.route("/logout")
@session_token_required
def logout():
    logger.info(f"Logging out user {session.get('user_name')}")
    session.pop('user_name', None)
    resp = make_response(redirect(url_for('user.index')))
    resp.delete_cookie('token')
    logger.info("User logged out and token removed from cookie.")
    flash("Logged out successfully", "Success")
    return resp
