import os
import uuid

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Employee, Department
from app.employees.forms import EmployeeForm, EmployeeSearchForm
from app.decorators import admin_required

employees_bp = Blueprint("employees", __name__)


def _save_profile_pic(file_storage):
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(path)
    return unique_name


@employees_bp.route("/")
@login_required
@admin_required
def list_employees():
    search_form = EmployeeSearchForm(request.args, meta={"csrf": False})

    query = Employee.query

    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Employee.first_name.ilike(like),
                Employee.last_name.ilike(like),
                Employee.email.ilike(like),
                Employee.designation.ilike(like),
            )
        )

    department_id = request.args.get("department_id", type=int)
    if department_id:
        query = query.filter(Employee.department_id == department_id)

    status = request.args.get("status", "")
    if status == "active":
        query = query.filter(Employee.is_active.is_(True))
    elif status == "inactive":
        query = query.filter(Employee.is_active.is_(False))

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Employee.first_name).paginate(
        page=page, per_page=current_app.config["EMPLOYEES_PER_PAGE"], error_out=False
    )

    return render_template(
        "employees/list.html",
        employees=pagination.items,
        pagination=pagination,
        search_form=search_form,
    )


@employees_bp.route("/<int:employee_id>")
@login_required
def view_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    # Employees may only view their own profile; admins can view anyone's.
    if not current_user.is_admin and (
        not current_user.employee or current_user.employee.id != employee.id
    ):
        abort(403)
    return render_template("employees/view.html", employee=employee)


@employees_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data,
            designation=form.designation.data,
            department_id=form.department_id.data or None,
            date_joined=form.date_joined.data,
            salary=form.salary.data or 0,
            address=form.address.data,
            is_active=form.is_active.data,
        )
        if form.profile_pic.data:
            employee.profile_pic = _save_profile_pic(form.profile_pic.data)

        db.session.add(employee)
        db.session.commit()
        flash(f"Employee {employee.full_name} added successfully.", "success")
        return redirect(url_for("employees.list_employees"))

    return render_template("employees/form.html", form=form, title="Add Employee")


@employees_bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)
    if form.department_id.data is None:
        form.department_id.data = employee.department_id or 0

    if form.validate_on_submit():
        employee.first_name = form.first_name.data.strip()
        employee.last_name = form.last_name.data.strip()
        employee.email = form.email.data.strip()
        employee.phone = form.phone.data
        employee.designation = form.designation.data
        employee.department_id = form.department_id.data or None
        employee.date_joined = form.date_joined.data
        employee.salary = form.salary.data or 0
        employee.address = form.address.data
        employee.is_active = form.is_active.data

        if form.profile_pic.data:
            employee.profile_pic = _save_profile_pic(form.profile_pic.data)

        db.session.commit()
        flash(f"Employee {employee.full_name} updated.", "success")
        return redirect(url_for("employees.list_employees"))

    return render_template(
        "employees/form.html", form=form, title="Edit Employee", employee=employee
    )


@employees_bp.route("/<int:employee_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    name = employee.full_name
    db.session.delete(employee)
    db.session.commit()
    flash(f"Employee {name} deleted.", "info")
    return redirect(url_for("employees.list_employees"))
