from flask import (
    render_template, redirect, url_for,
    jsonify, abort, Response
)
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from flask.typing import ResponseReturnValue
from datetime import datetime, timedelta

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

    try:
        # 1) Incidents by status
        status_data = (
            db.session.query(Incident.status, func.count(Incident.id))  # type: ignore
            .group_by(Incident.status)
            .all()
        )
        statuses, status_counts = zip(*status_data) if status_data else ([], [])

        # 2) Incidents over the last 30 days
        # Use database-agnostic approach: fetch all incidents and group in Python
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_incidents = (
            Incident.query
            .filter(Incident.timestamp >= thirty_days_ago)
            .all()
        )
        
        # Group by date in Python (database-agnostic)
        daily_data: dict[str, int] = {}
        for incident in recent_incidents:
            date_str = incident.timestamp.strftime('%Y-%m-%d')
            daily_data[date_str] = daily_data.get(date_str, 0) + 1
        
        dates = sorted(daily_data.keys())
        daily_counts = [daily_data[date] for date in dates]

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
        # Database-agnostic: calculate in Python
        closed_incidents = (
            db.session.query(Incident.timestamp, Incident.closed_at)  # type: ignore[call-overload]
            .filter(Incident.closed_at != None)  # noqa: E711
            .all()
        )
        
        if closed_incidents:
            total_hours = 0
            for timestamp, closed_at in closed_incidents:
                delta = closed_at - timestamp
                total_hours += delta.total_seconds() / 3600
            avg_hours = round(total_hours / len(closed_incidents), 2)
        else:
            avg_hours = 0.0

        return jsonify({
            'statuses':      list(statuses),
            'status_counts': list(status_counts),
            'dates':         dates,
            'daily_counts':  daily_counts,
            'cat_names':     list(cat_names),
            'cat_counts':    list(cat_counts),
            'avg_hours':     avg_hours
        })
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f'Error in dashboard_data: {str(e)}', exc_info=True)
        # Return empty data structure on error
        return jsonify({
            'statuses':      [],
            'status_counts': [],
            'dates':         [],
            'daily_counts':  [],
            'cat_names':     [],
            'cat_counts':    [],
            'avg_hours':     0.0
        }), 500
