"""
Service layer for incident-related business logic.

This service encapsulates all business logic for incidents,
separating it from route handlers for better modularity.
"""
from typing import Optional
from datetime import datetime
from app.models.incident import Incident
from app.models.category import IncidentCategory
from app.extensions import db
from app.utils.audit import create_audit_log
from app.utils.error_handler import ValidationError, DatabaseError, NotFoundError, handle_db_errors
from app.utils.sanitizer import clean_html
from flask_login import current_user


class IncidentService:
    """Service class for incident operations."""

    @staticmethod
    @handle_db_errors
    def create_incident(
        title: str,
        description: str,
        status: str,
        category_id: int,
        user_id: int
    ) -> Incident:
        """
        Create a new incident.
        
        Args:
            title: Incident title
            description: Incident description
            status: Incident status
            category_id: ID of the category
            user_id: ID of the user creating the incident
        
        Returns:
            The created Incident object
        
        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        # Validate category exists
        category = IncidentCategory.query.get(category_id)
        if not category:
            raise ValidationError("Invalid category selected")
        
        # Validate status
        allowed_statuses = ['Open', 'In Progress', 'Closed']
        if status not in allowed_statuses:
            raise ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
        
        # Sanitize HTML in description
        clean_description = clean_html(description)
        
        # Create incident
        incident = Incident(
            title=title.strip(),
            description=clean_description,
            status=status,
            category_id=category_id,
            user_id=user_id
        )
        
        try:
            db.session.add(incident)
            db.session.commit()
            
            # Create audit log
            create_audit_log('create', 'Incident', incident.id, user_id)
            
            return incident
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create incident: {str(e)}")

    @staticmethod
    @handle_db_errors
    def update_incident(
        incident_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Incident:
        """
        Update an existing incident.
        
        Args:
            incident_id: ID of the incident to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            category_id: New category ID (optional)
            user_id: ID of user making the update (optional, defaults to current_user)
        
        Returns:
            The updated Incident object
        
        Raises:
            NotFoundError: If incident doesn't exist
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        incident = Incident.query.get(incident_id)
        if not incident:
            raise NotFoundError(f"Incident with ID {incident_id} not found")
        
        # Use provided user_id or default to current_user
        if user_id is None:
            if not current_user.is_authenticated:
                raise ValidationError("User must be authenticated to update incidents")
            user_id = current_user.id
        
        # Update fields if provided
        if title is not None:
            incident.title = title.strip()
        
        if description is not None:
            incident.description = clean_html(description)
        
        if status is not None:
            allowed_statuses = ['Open', 'In Progress', 'Closed']
            if status not in allowed_statuses:
                raise ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
            incident.status = status
            
            # Handle closed_at timestamp
            if status.lower() == 'closed' and incident.closed_at is None:
                incident.closed_at = datetime.utcnow()
            elif status.lower() != 'closed':
                incident.closed_at = None
        
        if category_id is not None:
            category = IncidentCategory.query.get(category_id)
            if not category:
                raise ValidationError("Invalid category selected")
            incident.category_id = category_id
        
        try:
            db.session.commit()
            
            # Create audit log
            create_audit_log('update', 'Incident', incident.id, user_id)
            
            return incident
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update incident: {str(e)}")

    @staticmethod
    @handle_db_errors
    def delete_incident(incident_id: int, user_id: Optional[int] = None) -> None:
        """
        Delete an incident.
        
        Args:
            incident_id: ID of the incident to delete
            user_id: ID of user deleting the incident (optional, defaults to current_user)
        
        Raises:
            NotFoundError: If incident doesn't exist
            DatabaseError: If database operation fails
        """
        incident = Incident.query.get(incident_id)
        if not incident:
            raise NotFoundError(f"Incident with ID {incident_id} not found")
        
        # Use provided user_id or default to current_user
        if user_id is None:
            if not current_user.is_authenticated:
                raise ValidationError("User must be authenticated to delete incidents")
            user_id = current_user.id
        
        # Store ID before deletion for audit log
        incident_id_for_log = incident.id
        
        try:
            db.session.delete(incident)
            db.session.commit()
            
            # Create audit log
            create_audit_log('delete', 'Incident', incident_id_for_log, user_id)
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete incident: {str(e)}")

    @staticmethod
    def get_incident(incident_id: int) -> Optional[Incident]:
        """
        Get an incident by ID.
        
        Args:
            incident_id: ID of the incident
        
        Returns:
            The Incident object or None if not found
        """
        return Incident.query.get(incident_id)

    @staticmethod
    def get_incident_or_404(incident_id: int) -> Incident:
        """
        Get an incident by ID or raise 404.
        
        Args:
            incident_id: ID of the incident
        
        Returns:
            The Incident object
        
        Raises:
            NotFoundError: If incident doesn't exist
        """
        incident = Incident.query.get(incident_id)
        if not incident:
            raise NotFoundError(f"Incident with ID {incident_id} not found")
        return incident

