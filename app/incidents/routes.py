"""
Incident routes using service layer for business logic.

This module handles HTTP requests for incidents and delegates
business logic to the IncidentService.
"""
from flask import (
    render_template, redirect, url_for, flash,
    current_app, request
)
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from flask.typing import ResponseReturnValue

from app.incidents import incident_bp
from app.extensions import mail
from app.incidents.forms import IncidentForm
from app.models.incident import Incident
from app.models.category import IncidentCategory
from app.models.user import User
from app.services.incident_service import IncidentService
from app.utils.error_handler import NotFoundError, ValidationError, DatabaseError, log_error
from flask_mail import Message


def notify_admins(incident: Incident, action: str) -> None:
    """Helper to email all admins about an incident action."""
    try:
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
            mail.send(msg)
    except Exception as e:
        log_error(e, f"Failed to send '{action}' email for Incident {incident.id}")


@incident_bp.route('/')
@login_required
def list_incidents() -> str:
    """List all incidents with filtering and pagination."""
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

    # Execute with ordering and pagination (optimized with joinedload)
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
def view_incident(id: int) -> ResponseReturnValue:
    """View a single incident."""
    try:
        incident = IncidentService.get_incident_or_404(id)
        return render_template('incidents/detail.html', incident=incident)
    except NotFoundError as e:
        log_error(e, f"View incident {id}")
        flash('Incident not found.', 'danger')
        return redirect(url_for('incident.list_incidents'))


@incident_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_incident() -> ResponseReturnValue:
    """Create a new incident."""
    form = IncidentForm()
    form.category.choices = [
        (c.id, c.name) for c in IncidentCategory.query.all()
    ]

    if form.validate_on_submit():
        try:
            incident = IncidentService.create_incident(
                title=form.title.data,
                description=form.description.data,
                status=form.status.data,
                category_id=form.category.data,
                user_id=current_user.id
            )
            
            # Email notification
            notify_admins(incident, 'created')
            
            flash('Incident created successfully.', 'success')
            return redirect(url_for('incident.list_incidents'))
        except ValidationError as e:
            flash(str(e), 'warning')
        except DatabaseError as e:
            log_error(e, "Create incident")
            flash('Failed to create incident. Please try again.', 'danger')
        except Exception as e:
            log_error(e, "Create incident - unexpected error")
            flash('An unexpected error occurred. Please try again.', 'danger')

    return render_template('incidents/form.html', form=form, action='Create')


@incident_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_incident(id: int) -> ResponseReturnValue:
    """Edit an existing incident."""
    try:
        incident = IncidentService.get_incident_or_404(id)
        
        # Check authorization
        if not (current_user.is_admin() or incident.creator == current_user):
            flash('You do not have permission to edit this incident.', 'danger')
            return redirect(url_for('incident.list_incidents'))

        form = IncidentForm(obj=incident)
        form.category.choices = [
            (c.id, c.name) for c in IncidentCategory.query.all()
        ]

        if form.validate_on_submit():
            try:
                updated_incident = IncidentService.update_incident(
                    incident_id=id,
                    title=form.title.data,
                    description=form.description.data,
                    status=form.status.data,
                    category_id=form.category.data
                )
                
                # Email notification
                notify_admins(updated_incident, 'updated')
                
                flash('Incident updated successfully.', 'success')
                return redirect(url_for('incident.view_incident', id=id))
            except ValidationError as e:
                flash(str(e), 'warning')
            except DatabaseError as e:
                log_error(e, f"Update incident {id}")
                flash('Failed to update incident. Please try again.', 'danger')
            except Exception as e:
                log_error(e, f"Update incident {id} - unexpected error")
                flash('An unexpected error occurred. Please try again.', 'danger')

        return render_template('incidents/form.html', form=form, action='Edit')
    except NotFoundError as e:
        log_error(e, f"Edit incident {id}")
        flash('Incident not found.', 'danger')
        return redirect(url_for('incident.list_incidents'))


@incident_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_incident(id: int) -> ResponseReturnValue:
    """Delete an incident."""
    # Check authorization
    if not current_user.is_admin():
        flash('Only administrators can delete incidents.', 'danger')
        return redirect(url_for('incident.list_incidents'))
    
    try:
        # Get incident before deletion for notification
        incident = IncidentService.get_incident_or_404(id)
        
        # Delete using service
        IncidentService.delete_incident(id)
        
        # Email notification
        notify_admins(incident, 'deleted')
        
        flash('Incident deleted successfully.', 'success')
    except NotFoundError as e:
        log_error(e, f"Delete incident {id}")
        flash('Incident not found.', 'danger')
    except DatabaseError as e:
        log_error(e, f"Delete incident {id}")
        flash('Failed to delete incident. Please try again.', 'danger')
    except Exception as e:
        log_error(e, f"Delete incident {id} - unexpected error")
        flash('An unexpected error occurred. Please try again.', 'danger')

    return redirect(url_for('incident.list_incidents'))
