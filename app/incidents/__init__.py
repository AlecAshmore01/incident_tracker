from flask import Blueprint

incident_bp = Blueprint('incident', __name__)

from app.incidents import routes  # noqa