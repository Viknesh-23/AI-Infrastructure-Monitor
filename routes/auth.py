from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


def _safe_next_url(target):
    """Only redirect to an internal URL after sign-in."""
    if not target:
        return None
    base = urlparse(request.host_url)
    candidate = urlparse(urljoin(request.host_url, target))
    return target if candidate.scheme in ("http", "https") and candidate.netloc == base.netloc else None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if len(username) < 2 or "@" not in email or len(password) < 8:
            flash("Use a username, a valid email, and a password with at least 8 characters.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        elif User.query.filter((User.email == email) | (User.username == username)).first():
            flash("An account with that email or username already exists.", "warning")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Account created. Start by adding a server or loading demo data.", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier)
        ).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=bool(request.form.get("remember")))
            next_page = _safe_next_url(request.args.get("next"))
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
