import os
import uuid

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.profile.forms import ProfileForm, ChangePasswordForm

profile_bp = Blueprint("profile", __name__)


def _save_profile_pic(file_storage):
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(path)
    return unique_name


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def my_profile():
    employee = current_user.employee
    form = ProfileForm(obj=employee) if employee else ProfileForm()

    if form.validate_on_submit():
        if not employee:
            flash("No employee record is linked to your account yet. Contact an admin.", "warning")
            return redirect(url_for("profile.my_profile"))

        employee.phone = form.phone.data
        employee.address = form.address.data
        if form.profile_pic.data:
            employee.profile_pic = _save_profile_pic(form.profile_pic.data)
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile.my_profile"))

    return render_template("profile/edit.html", form=form, employee=employee)


@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for("profile.my_profile"))

    return render_template("profile/change_password.html", form=form)
