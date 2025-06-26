from datetime import datetime
from flask import (
    render_template, redirect, url_for, flash,
    current_app, request, Response
)
from flask_login import login_required, current_user
from math import ceil
from sqlalchemy.orm import joinedload
from flask.typing import ResponseReturnValue

from app.incidents import incident_bp
from app.extensions import db, mail
from app.incidents.forms import IncidentForm
from app.models.incident import Incident
from app.models.category import IncidentCategory
from app.utils.sanitizer import clean_html
from app.models.audit import AuditLog
from app.models.user import User
from flask_mail import Message


def notify_admins(incident: Incident, action: str) -> None:
    """Helper to email all admins about an incident action."""
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        msg = Message(
            subject=f"Incident #{incident.id} {action.capitalize()}",
            recipients=[admin.email]
        )
        msg.html = render_template(
            'email/incident_notification.html',
            user=admin,
            incident=incident,
            action=action
        )
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(
                f"Failed to send '{action}' email for Incident {incident.id} "
                f"to {admin.email}: {e}"
            )


@incident_bp.route('/')
@login_required
def list_incidents() -> str:
    # Grab query parameters
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    category = request.args.get('category', '')

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Full‐text search if `q` provided, otherwise normal query
    if q:
        # whooshee_search performs full-text lookup on the registered fields
        query = Incident.query.whooshee_search(q)
    else:
        query = Incident.query

    # Apply status/category filters
    if status:
        query = query.filter_by(status=status)
    if category:
        try:
            cid = int(category)
            query = query.filter_by(category_id=cid)
        except ValueError:
            pass

    # Execute with ordering and pagination
    pagination = (
        query
        .options(joinedload(Incident.category), joinedload(Incident.creator))
        .order_by(Incident.timestamp.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    incidents = pagination.items

    # Data for filter dropdowns
    all_statuses = ['Open', 'In Progress', 'Closed']
    all_categories = IncidentCategory.query.all()

    # Render the template with everything
    return render_template(
        'incidents/list.html',
        incidents=incidents,
        pagination=pagination,
        q=q,
        selected_status=status,
        selected_category=category,
        all_statuses=all_statuses,
        all_categories=all_categories
    )


@incident_bp.route('/<int:id>')
@login_required
def view_incident(id: int) -> str:
    incident = Incident.query.get_or_404(id)
    return render_template('incidents/detail.html', incident=incident)


@incident_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_incident() -> ResponseReturnValue:
    form = IncidentForm()
    form.category.choices = [
        (c.id, c.name) for c in IncidentCategory.query.all()
    ]

    if form.validate_on_submit():
        inc = Incident(
            title=form.title.data,
            description=clean_html(form.description.data),
            status=form.status.data,
            category_id=form.category.data,
            user_id=current_user.id
        )
        db.session.add(inc)
        db.session.commit()

        # Audit log
        db.session.add(AuditLog(
            user_id=current_user.id,
            action='create',
            target_type='Incident',
            target_id=inc.id
        ))
        db.session.commit()

        # Email notification
        notify_admins(inc, 'created')

        flash('Incident created.', 'success')
        return redirect(url_for('incident.list_incidents'))

    return render_template('incidents/form.html', form=form, action='Create')


@incident_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_incident(id: int) -> ResponseReturnValue:
    inc = Incident.query.get_or_404(id)
    if not (current_user.is_admin() or inc.creator == current_user):
        flash('Access denied.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    form = IncidentForm(obj=inc)
    form.category.choices = [
        (c.id, c.name) for c in IncidentCategory.query.all()
    ]

    if form.validate_on_submit():
        inc.title = form.title.data
        inc.description = clean_html(form.description.data)
        inc.status = form.status.data
        inc.category_id = form.category.data

        if inc.status.lower() == 'closed' and inc.closed_at is None:
            inc.closed_at = datetime.utcnow()
        elif inc.status.lower() != 'closed':
            inc.closed_at = None
        db.session.commit()

        # Audit log
        db.session.add(AuditLog(
            user_id=current_user.id,
            action='update',
            target_type='Incident',
            target_id=inc.id
        ))
        db.session.commit()

        # Email notification
        notify_admins(inc, 'updated')

        flash('Incident updated.', 'success')
        return redirect(url_for('incident.view_incident', id=inc.id))

    return render_template('incidents/form.html', form=form, action='Edit')


@incident_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_incident(id: int) -> ResponseReturnValue:
    inc = Incident.query.get_or_404(id)
    if not current_user.is_admin():
        flash('Only admins can delete incidents.', 'danger')
    else:
        inc_id = inc.id  # Store ID before deletion
        db.session.delete(inc)
        db.session.commit()

        # Audit log (created after delete/commit)
        log = AuditLog(
            user_id=current_user.id,
            action='delete',
            target_type='Incident',
            target_id=inc_id
        )
        db.session.add(log)
        db.session.commit()
        print(f"Created audit log for delete: id={log.id}, target_id={inc_id}")
        # Print all audit logs in this context
        all_logs = AuditLog.query.order_by(AuditLog.id.desc()).all()
        print("[ROUTE] All audit logs after delete:")
        for log_entry in all_logs:
            print(f"  action={log_entry.action}, target_type={log_entry.target_type}, "
                  f"target_id={log_entry.target_id}, id={log_entry.id}, time={log_entry.timestamp}")

        # Email notification (pass only ID, not object)
        notify_admins(inc, 'deleted')

        flash('Incident deleted.', 'success')

    return redirect(url_for('incident.list_incidents'))
