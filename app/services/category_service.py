"""
Service layer for category-related business logic.

This service encapsulates all business logic for categories,
separating it from route handlers for better modularity.
"""
from typing import Optional
from app.models.category import IncidentCategory
from app.extensions import db
from app.utils.audit import create_audit_log
from app.utils.error_handler import ValidationError, DatabaseError, NotFoundError, handle_db_errors
from flask_login import current_user


class CategoryService:
    """Service class for category operations."""

    @staticmethod
    @handle_db_errors
    def create_category(
        name: str,
        description: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> IncidentCategory:
        """
        Create a new category.
        
        Args:
            name: Category name
            description: Category description (optional)
            user_id: ID of user creating the category (optional, defaults to current_user)
        
        Returns:
            The created IncidentCategory object
        
        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        # Use provided user_id or default to current_user
        if user_id is None:
            if not current_user.is_authenticated:
                raise ValidationError("User must be authenticated to create categories")
            user_id = current_user.id
        
        # Check for duplicate name
        existing = IncidentCategory.query.filter_by(name=name.strip()).first()
        if existing:
            raise ValidationError("A category with this name already exists")
        
        # Create category
        category = IncidentCategory(
            name=name.strip(),
            description=description.strip() if description else None
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            
            # Create audit log
            create_audit_log('create', 'Category', category.id, user_id)
            
            return category
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to create category: {str(e)}")

    @staticmethod
    @handle_db_errors
    def update_category(
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> IncidentCategory:
        """
        Update an existing category.
        
        Args:
            category_id: ID of the category to update
            name: New name (optional)
            description: New description (optional)
            user_id: ID of user making the update (optional, defaults to current_user)
        
        Returns:
            The updated IncidentCategory object
        
        Raises:
            NotFoundError: If category doesn't exist
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        category = IncidentCategory.query.get(category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        
        # Use provided user_id or default to current_user
        if user_id is None:
            if not current_user.is_authenticated:
                raise ValidationError("User must be authenticated to update categories")
            user_id = current_user.id
        
        # Update fields if provided
        if name is not None:
            # Check for duplicate name (excluding current category)
            existing = IncidentCategory.query.filter(
                IncidentCategory.name == name.strip(),
                IncidentCategory.id != category_id
            ).first()
            if existing:
                raise ValidationError("A category with this name already exists")
            category.name = name.strip()
        
        if description is not None:
            category.description = description.strip() if description else None
        
        try:
            db.session.commit()
            
            # Create audit log
            create_audit_log('update', 'Category', category.id, user_id)
            
            return category
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to update category: {str(e)}")

    @staticmethod
    @handle_db_errors
    def delete_category(category_id: int, user_id: Optional[int] = None) -> None:
        """
        Delete a category.
        
        Args:
            category_id: ID of the category to delete
            user_id: ID of user deleting the category (optional, defaults to current_user)
        
        Raises:
            NotFoundError: If category doesn't exist
            ValidationError: If category is in use
            DatabaseError: If database operation fails
        """
        category = IncidentCategory.query.get(category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        
        # Check if category is in use
        if category.incidents.first():
            raise ValidationError("Cannot delete a category that is currently in use by incidents")
        
        # Use provided user_id or default to current_user
        if user_id is None:
            if not current_user.is_authenticated:
                raise ValidationError("User must be authenticated to delete categories")
            user_id = current_user.id
        
        try:
            db.session.delete(category)
            db.session.commit()
            
            # Create audit log
            create_audit_log('delete', 'Category', category_id, user_id)
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Failed to delete category: {str(e)}")

    @staticmethod
    def get_category(category_id: int) -> Optional[IncidentCategory]:
        """
        Get a category by ID.
        
        Args:
            category_id: ID of the category
        
        Returns:
            The IncidentCategory object or None if not found
        """
        return IncidentCategory.query.get(category_id)

    @staticmethod
    def get_category_or_404(category_id: int) -> IncidentCategory:
        """
        Get a category by ID or raise 404.
        
        Args:
            category_id: ID of the category
        
        Returns:
            The IncidentCategory object
        
        Raises:
            NotFoundError: If category doesn't exist
        """
        category = IncidentCategory.query.get(category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        return category

    @staticmethod
    def get_all_categories() -> list[IncidentCategory]:
        """
        Get all categories ordered by name.
        
        Returns:
            List of all IncidentCategory objects
        """
        return IncidentCategory.query.order_by(IncidentCategory.name).all()

