from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

from app.models import Employee


class AttendanceForm(FlaskForm):
    employee_id = SelectField("Employee", coerce=int, validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[("Present", "Present"), ("Absent", "Absent"), ("Half Day", "Half Day"), ("Leave", "Leave")],
        validators=[DataRequired()],
    )
    remarks = StringField("Remarks", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save Attendance")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee_id.choices = [
            (e.id, e.full_name) for e in Employee.query.order_by(Employee.first_name).all()
        ]


class AttendanceFilterForm(FlaskForm):
    employee_id = SelectField("Employee", coerce=int, validators=[Optional()])
    date = DateField("Date", validators=[Optional()])
    submit = SubmitField("Filter")

    class Meta:
        csrf = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee_id.choices = [(0, "All Employees")] + [
            (e.id, e.full_name) for e in Employee.query.order_by(Employee.first_name).all()
        ]
