from flask import (
    render_template, redirect, url_for, flash
)
from flask_login import login_required, current_user

from app.categories import category_bp
from app.extensions import db
from app.categories.forms import CategoryForm
from app.models.category import IncidentCategory
from app.models.audit import AuditLog


def log_action(action: str, target_id: int) -> None:
    """Helper to audit category actions."""
    db.session.add(AuditLog(
        user_id=current_user.id,
        action=action,
        target_type='Category',
        target_id=target_id
    ))
    db.session.commit()


@category_bp.route('/')
@login_required
def list_categories() -> str:
    categories = IncidentCategory.query.order_by(IncidentCategory.name).all()
    return render_template('categories/list.html', categories=categories)


@category_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_category() -> str:
    if not current_user.is_admin():
        flash('Only admins can manage categories.', 'danger')
        return redirect(url_for('category.list_categories'))

    form = CategoryForm()
    if form.validate_on_submit():
        cat = IncidentCategory(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(cat)
        db.session.commit()

        # Audit
        log_action('create', cat.id)

        flash('Category created.', 'success')
        return redirect(url_for('category.list_categories'))

    return render_template('categories/form.html', form=form, action='Create')


@category_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id: int) -> str:
    if not current_user.is_admin():
        flash('Only admins can manage categories.', 'danger')
        return redirect(url_for('category.list_categories'))

    cat = IncidentCategory.query.get_or_404(id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.description = form.description.data
        db.session.commit()

        # Audit
        log_action('update', cat.id)

        flash('Category updated.', 'success')
        return redirect(url_for('category.list_categories'))

    return render_template('categories/form.html', form=form, action='Edit')


@category_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id: int) -> str:
    if not current_user.is_admin():
        flash('Only admins can manage categories.', 'danger')
        return redirect(url_for('category.list_categories'))

    cat = IncidentCategory.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()

    # Audit
    log_action('delete', id)

    flash('Category deleted.', 'success')
    return redirect(url_for('category.list_categories'))
