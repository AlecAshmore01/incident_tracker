"""
Category routes using service layer for business logic.

This module handles HTTP requests for categories and delegates
business logic to the CategoryService.
"""
from flask import (
    render_template, redirect, url_for, flash
)
from flask_login import login_required, current_user
from flask.typing import ResponseReturnValue

from app.categories import category_bp
from app.categories.forms import CategoryForm
from app.services.category_service import CategoryService
from app.utils.error_handler import NotFoundError, ValidationError, DatabaseError, log_error


@category_bp.route('/')
@login_required
def list_categories() -> ResponseReturnValue:
    """List all categories."""
    try:
        categories = CategoryService.get_all_categories()
        return render_template('categories/list.html', categories=categories)
    except Exception as e:
        log_error(e, "List categories")
        flash('Failed to load categories. Please try again.', 'danger')
        return redirect(url_for('main.index'))


@category_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_category() -> ResponseReturnValue:
    """Create a new category."""
    # Check authorization
    if not current_user.is_admin():
        flash('Only administrators can manage categories.', 'danger')
        return redirect(url_for('category.list_categories'))

    form = CategoryForm()
    if form.validate_on_submit():
        try:
            CategoryService.create_category(
                name=form.name.data,
                description=form.description.data
            )
            flash('Category created successfully.', 'success')
            return redirect(url_for('category.list_categories'))
        except ValidationError as e:
            flash(str(e), 'warning')
        except DatabaseError as e:
            log_error(e, "Create category")
            flash('Failed to create category. Please try again.', 'danger')
        except Exception as e:
            log_error(e, "Create category - unexpected error")
            flash('An unexpected error occurred. Please try again.', 'danger')

    return render_template('categories/form.html', form=form, action='Create')


@category_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id: int) -> ResponseReturnValue:
    """Edit an existing category."""
    # Check authorization
    if not current_user.is_admin():
        flash('Only administrators can manage categories.', 'danger')
        return redirect(url_for('category.list_categories'))

    try:
        category = CategoryService.get_category_or_404(id)
        form = CategoryForm(obj=category)
        
        if form.validate_on_submit():
            try:
                CategoryService.update_category(
                    category_id=id,
                    name=form.name.data,
                    description=form.description.data
                )
                flash('Category updated successfully.', 'success')
                return redirect(url_for('category.list_categories'))
            except ValidationError as e:
                flash(str(e), 'warning')
            except DatabaseError as e:
                log_error(e, f"Update category {id}")
                flash('Failed to update category. Please try again.', 'danger')
            except Exception as e:
                log_error(e, f"Update category {id} - unexpected error")
                flash('An unexpected error occurred. Please try again.', 'danger')

        return render_template('categories/form.html', form=form, action='Edit')
    except NotFoundError as e:
        log_error(e, f"Edit category {id}")
        flash('Category not found.', 'danger')
        return redirect(url_for('category.list_categories'))


@category_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id: int) -> ResponseReturnValue:
    """Delete a category."""
    # Check authorization
    if not current_user.is_admin():
        flash('Only administrators can manage categories.', 'danger')
        return redirect(url_for('category.list_categories'))

    try:
        CategoryService.delete_category(id)
        flash('Category deleted successfully.', 'success')
    except NotFoundError as e:
        log_error(e, f"Delete category {id}")
        flash('Category not found.', 'danger')
    except ValidationError as e:
        flash(str(e), 'warning')
    except DatabaseError as e:
        log_error(e, f"Delete category {id}")
        flash('Failed to delete category. Please try again.', 'danger')
    except Exception as e:
        log_error(e, f"Delete category {id} - unexpected error")
        flash('An unexpected error occurred. Please try again.', 'danger')

    return redirect(url_for('category.list_categories'))
