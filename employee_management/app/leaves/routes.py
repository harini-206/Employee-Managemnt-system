from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import LeaveRequest
from app.leaves.forms import LeaveRequestForm, LeaveReviewForm
from app.decorators import admin_required

leaves_bp = Blueprint("leaves", __name__)


@leaves_bp.route("/")
@login_required
@admin_required
def list_leaves():
    status = request.args.get("status", "")
    query = LeaveRequest.query
    if status:
        query = query.filter_by(status=status)

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(LeaveRequest.applied_on.desc()).paginate(
        page=page, per_page=current_app.config["LEAVES_PER_PAGE"], error_out=False
    )
    return render_template(
        "leaves/list.html", leaves=pagination.items, pagination=pagination, status=status
    )


@leaves_bp.route("/<int:leave_id>/review", methods=["GET", "POST"])
@login_required
@admin_required
def review_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    form = LeaveReviewForm()
    if form.validate_on_submit():
        leave.status = form.status.data
        leave.review_comment = form.review_comment.data
        leave.reviewed_by = current_user.id
        db.session.commit()
        flash(f"Leave request {leave.status.lower()}.", "success")
        return redirect(url_for("leaves.list_leaves"))
    return render_template("leaves/review.html", form=form, leave=leave)


@leaves_bp.route("/apply", methods=["GET", "POST"])
@login_required
def apply_leave():
    if not current_user.employee:
        flash("No employee profile linked to your account. Contact an admin.", "warning")
        return redirect(url_for("dashboard.index"))

    form = LeaveRequestForm()
    if form.validate_on_submit():
        leave = LeaveRequest(
            employee_id=current_user.employee.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            leave_type=form.leave_type.data,
            reason=form.reason.data,
        )
        db.session.add(leave)
        db.session.commit()
        flash("Leave request submitted.", "success")
        return redirect(url_for("leaves.my_leaves"))

    return render_template("leaves/apply.html", form=form)


@leaves_bp.route("/mine")
@login_required
def my_leaves():
    if not current_user.employee:
        flash("No employee profile linked to your account.", "warning")
        return redirect(url_for("dashboard.index"))

    leaves = (
        LeaveRequest.query.filter_by(employee_id=current_user.employee.id)
        .order_by(LeaveRequest.applied_on.desc())
        .all()
    )
    return render_template("leaves/mine.html", leaves=leaves)


@leaves_bp.route("/<int:leave_id>/cancel", methods=["POST"])
@login_required
def cancel_leave(leave_id):
    leave = LeaveRequest.query.get_or_404(leave_id)
    if not current_user.employee or leave.employee_id != current_user.employee.id:
        abort(403)
    if leave.status != "Pending":
        flash("Only pending requests can be cancelled.", "danger")
    else:
        db.session.delete(leave)
        db.session.commit()
        flash("Leave request cancelled.", "info")
    return redirect(url_for("leaves.my_leaves"))
