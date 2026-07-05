from datetime import date as date_cls

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Attendance, Employee
from app.attendance.forms import AttendanceForm, AttendanceFilterForm
from app.decorators import admin_required

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/")
@login_required
@admin_required
def list_attendance():
    filter_form = AttendanceFilterForm(request.args, meta={"csrf": False})

    query = Attendance.query

    employee_id = request.args.get("employee_id", type=int)
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    date_str = request.args.get("date")
    if date_str:
        try:
            filter_date = date_cls.fromisoformat(date_str)
            query = query.filter(Attendance.date == filter_date)
        except ValueError:
            pass

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Attendance.date.desc()).paginate(
        page=page, per_page=current_app.config["ATTENDANCE_PER_PAGE"], error_out=False
    )

    return render_template(
        "attendance/list.html",
        records=pagination.items,
        pagination=pagination,
        filter_form=filter_form,
    )


@attendance_bp.route("/mark", methods=["GET", "POST"])
@login_required
@admin_required
def mark_attendance():
    form = AttendanceForm()
    if form.validate_on_submit():
        existing = Attendance.query.filter_by(
            employee_id=form.employee_id.data, date=form.date.data
        ).first()
        if existing:
            existing.status = form.status.data
            existing.remarks = form.remarks.data
            flash("Attendance record updated (already existed for that date).", "info")
        else:
            record = Attendance(
                employee_id=form.employee_id.data,
                date=form.date.data,
                status=form.status.data,
                remarks=form.remarks.data,
            )
            db.session.add(record)
            flash("Attendance marked.", "success")
        db.session.commit()
        return redirect(url_for("attendance.list_attendance"))

    return render_template("attendance/mark.html", form=form)


@attendance_bp.route("/<int:record_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_attendance(record_id):
    record = Attendance.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash("Attendance record removed.", "info")
    return redirect(url_for("attendance.list_attendance"))


@attendance_bp.route("/mine")
@login_required
def my_attendance():
    if not current_user.employee:
        flash("No employee profile linked to your account.", "warning")
        return redirect(url_for("dashboard.index"))

    page = request.args.get("page", 1, type=int)
    pagination = (
        Attendance.query.filter_by(employee_id=current_user.employee.id)
        .order_by(Attendance.date.desc())
        .paginate(page=page, per_page=current_app.config["ATTENDANCE_PER_PAGE"], error_out=False)
    )
    return render_template("attendance/mine.html", records=pagination.items, pagination=pagination)
