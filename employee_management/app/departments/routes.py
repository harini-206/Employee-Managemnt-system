from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Department
from app.departments.forms import DepartmentForm
from app.decorators import admin_required

departments_bp = Blueprint("departments", __name__)


@departments_bp.route("/")
@login_required
@admin_required
def list_departments():
    departments = Department.query.order_by(Department.name).all()
    return render_template("departments/list.html", departments=departments)


@departments_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        dept = Department(name=form.name.data.strip(), description=form.description.data)
        db.session.add(dept)
        db.session.commit()
        flash(f"Department '{dept.name}' created.", "success")
        return redirect(url_for("departments.list_departments"))
    return render_template("departments/form.html", form=form, title="Add Department")


@departments_bp.route("/<int:department_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_department(department_id):
    dept = Department.query.get_or_404(department_id)
    form = DepartmentForm(obj=dept)
    if form.validate_on_submit():
        dept.name = form.name.data.strip()
        dept.description = form.description.data
        db.session.commit()
        flash(f"Department '{dept.name}' updated.", "success")
        return redirect(url_for("departments.list_departments"))
    return render_template("departments/form.html", form=form, title="Edit Department")


@departments_bp.route("/<int:department_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_department(department_id):
    dept = Department.query.get_or_404(department_id)
    if dept.employees:
        flash("Cannot delete a department that still has employees assigned.", "danger")
        return redirect(url_for("departments.list_departments"))
    db.session.delete(dept)
    db.session.commit()
    flash("Department deleted.", "info")
    return redirect(url_for("departments.list_departments"))
