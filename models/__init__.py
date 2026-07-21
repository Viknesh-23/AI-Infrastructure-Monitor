from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to access the monitoring console."
login_manager.login_message_category = "warning"

# Import models so SQLAlchemy discovers all metadata before create_all().
from models.user import User  # noqa: E402, F401
from models.server import Server  # noqa: E402, F401
from models.metric import Metric  # noqa: E402, F401
from models.incident import Incident  # noqa: E402, F401
from models.alert import Alert  # noqa: E402, F401
