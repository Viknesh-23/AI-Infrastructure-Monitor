import ipaddress
import uuid

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.server import Server

servers_bp = Blueprint("servers", __name__, url_prefix="/servers")


def owned_server(server_id):
    server = db.session.get(Server, server_id)
    if not server or server.user_id != current_user.id:
        abort(404)
    return server


def validate_server_form():
    values = {
        "server_code": request.form.get("server_code", "").strip().upper(),
        "name": request.form.get("name", "").strip(),
        "ip_address": request.form.get("ip_address", "").strip(),
        "os": request.form.get("os", "").strip(),
        "environment": request.form.get("environment", "Development"),
        "status": request.form.get("status", "Healthy"),
    }
    if not all([values["server_code"], values["name"], values["ip_address"], values["os"]]):
        return values, "All server fields are required."
    if values["environment"] not in ("Development", "Testing", "Production"):
        return values, "Choose a valid environment."
    if values["status"] not in ("Healthy", "Warning", "Critical", "Offline"):
        return values, "Choose a valid status."
    try:
        ipaddress.ip_address(values["ip_address"])
    except ValueError:
        return values, "Enter a valid IPv4 or IPv6 address."
    return values, None


@servers_bp.route("/")
@login_required
def list_servers():
    return render_template("servers.html", servers=current_user.servers)


@servers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_server():
    if request.method == "POST":
        values, error = validate_server_form()
        if not error and Server.query.filter_by(server_code=values["server_code"]).first():
            error = "That Server ID is already in use."
        if error:
            flash(error, "danger")
            return render_template("add_server.html", values=values)
        server = Server(**values, user_id=current_user.id)
        db.session.add(server)
        db.session.commit()
        flash(f"{server.name} is now being monitored.", "success")
        return redirect(url_for("servers.server_detail", server_id=server.id))
    return render_template("add_server.html", values={"server_code": f"SRV-{uuid.uuid4().hex[:5].upper()}"})


@servers_bp.route("/<int:server_id>")
@login_required
def server_detail(server_id):
    return render_template("server_detail.html", server=owned_server(server_id))


@servers_bp.route("/<int:server_id>/edit", methods=["GET", "POST"])
@login_required
def edit_server(server_id):
    server = owned_server(server_id)
    if request.method == "POST":
        values, error = validate_server_form()
        existing = Server.query.filter_by(server_code=values["server_code"]).first()
        if not error and existing and existing.id != server.id:
            error = "That Server ID is already in use."
        if error:
            flash(error, "danger")
            return render_template("edit_server.html", server=server, values=values)
        for key, value in values.items():
            setattr(server, key, value)
        db.session.commit()
        flash("Server details updated.", "success")
        return redirect(url_for("servers.server_detail", server_id=server.id))
    return render_template("edit_server.html", server=server, values=server.__dict__)


@servers_bp.route("/<int:server_id>/delete", methods=["POST"])
@login_required
def delete_server(server_id):
    server = owned_server(server_id)
    db.session.delete(server)
    db.session.commit()
    flash("Server and its monitoring history were deleted.", "info")
    return redirect(url_for("servers.list_servers"))
