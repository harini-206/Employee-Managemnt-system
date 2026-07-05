from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import Employee, Department, Attendance, LeaveRequest

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    if current_user.is_admin:
        stats = {
            "total_employees": Employee.query.filter_by(is_active=True).count(),
            "total_departments": Department.query.count(),
            "present_today": Attendance.query.filter_by(
                date=date.today(), status="Present"
            ).count(),
            "pending_leaves": LeaveRequest.query.filter_by(status="Pending").count(),
        }
        recent_leaves = (
            LeaveRequest.query.order_by(LeaveRequest.applied_on.desc()).limit(5).all()
        )
        dept_counts = [
            (d.name, len(d.employees)) for d in Department.query.all()
        ]
        return render_template(
            "dashboard/index.html",
            stats=stats,
            recent_leaves=recent_leaves,
            dept_counts=dept_counts,
        )
    else:
        employee = current_user.employee
        my_leaves = []
        my_attendance = []
        if employee:
            my_leaves = (
                LeaveRequest.query.filter_by(employee_id=employee.id)
                .order_by(LeaveRequest.applied_on.desc())
                .limit(5)
                .all()
            )
            my_attendance = (
                Attendance.query.filter_by(employee_id=employee.id)
                .order_by(Attendance.date.desc())
                .limit(5)
                .all()
            )
        return render_template(
            "dashboard/employee_index.html",
            employee=employee,
            my_leaves=my_leaves,
            my_attendance=my_attendance,
        )
