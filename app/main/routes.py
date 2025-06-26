from flask import (
    render_template, redirect, url_for,
    jsonify, abort, Response
)
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from flask.typing import ResponseReturnValue

from app.main import main_bp
from app.extensions import db
from app.models.audit import AuditLog
from app.models.incident import Incident
from app.models.category import IncidentCategory


@main_bp.route('/')
def index() -> ResponseReturnValue:
    return render_template('index.html')


@main_bp.route('/audit-logs')
@login_required
def audit_logs() -> ResponseReturnValue:
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    logs = (
        AuditLog.query
        .order_by(desc(AuditLog.timestamp))  # type: ignore
        .limit(100)
        .all()
    )
    return render_template('audit/list.html', logs=logs)


@main_bp.route('/dashboard')
@login_required
def dashboard() -> ResponseReturnValue:
    """Render the dashboard page (HTML + JS)."""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    return render_template('dashboard.html')


@main_bp.route('/api/dashboard-data')
@login_required
def dashboard_data() -> ResponseReturnValue:
    """Provide JSON data for the dashboard charts."""
    if not current_user.is_admin():
        abort(403)

    # 1) Incidents by status
    status_data = (
        db.session.query(Incident.status, func.count(Incident.id))  # type: ignore
        .group_by(Incident.status)
        .all()
    )
    statuses, status_counts = zip(*status_data) if status_data else ([], [])

    # 2) Incidents over the last 30 days
    time_data = (
        db.session.query(
            func.strftime('%Y-%m-%d', Incident.timestamp),
            func.count(Incident.id)  # type: ignore
        )
        .filter(Incident.timestamp >= func.datetime('now', '-30 days'))
        .group_by(func.strftime('%Y-%m-%d', Incident.timestamp))
        .order_by(func.strftime('%Y-%m-%d', Incident.timestamp))
        .all()
    )
    dates, daily_counts = zip(*time_data) if time_data else ([], [])

    # 3) Top 5 categories by incident count
    cat_data = (
        db.session.query(
            IncidentCategory.name,
            func.count(Incident.id)  # type: ignore
        )
        .join(Incident, Incident.category_id == IncidentCategory.id)
        .group_by(IncidentCategory.name)
        .order_by(desc(func.count(Incident.id)))  # type: ignore
        .limit(5)
        .all()
    )
    cat_names, cat_counts = zip(*cat_data) if cat_data else ([], [])

    # 4) Average resolution time (in hours)
    avg_days = (
        db.session.query(
            func.avg(
                func.julianday(Incident.closed_at) - func.julianday(Incident.timestamp)
            )
        )
        .filter(Incident.closed_at != None)  # noqa: E711
        .scalar() or 0.0
    )
    avg_hours = round(avg_days * 24, 2)

    return jsonify({
        'statuses':      list(statuses),
        'status_counts': list(status_counts),
        'dates':         list(dates),
        'daily_counts':  list(daily_counts),
        'cat_names':     list(cat_names),
        'cat_counts':    list(cat_counts),
        'avg_hours':     avg_hours
    })
