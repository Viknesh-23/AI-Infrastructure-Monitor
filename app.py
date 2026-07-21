import os
import click
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from config import Config
from models import db, login_manager
from routes.analytics import analytics_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.incidents import incidents_bp
from routes.monitoring import monitoring_bp
from routes.servers import servers_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create instance folder
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(servers_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(analytics_bp)

    # Automatically create database tables
    with app.app_context():
        db.create_all()

    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        with app.app_context():
            db.create_all()
        click.echo("Database tables created.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)