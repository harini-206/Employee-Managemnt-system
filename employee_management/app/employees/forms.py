from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    FloatField,
    DateField,
    SelectField,
    TextAreaField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length

from app.models import Department


class EmployeeForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=64)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    designation = StringField("Designation", validators=[Optional(), Length(max=100)])
    department_id = SelectField("Department", coerce=int, validators=[Optional()])
    date_joined = DateField("Date Joined", validators=[Optional()])
    salary = FloatField("Salary", validators=[Optional(), NumberRange(min=0)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=255)])
    profile_pic = FileField(
        "Profile Picture", validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!")]
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Employee")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department_id.choices = [(0, "-- None --")] + [
            (d.id, d.name) for d in Department.query.order_by(Department.name).all()
        ]


class EmployeeSearchForm(FlaskForm):
    q = StringField("Search")
    department_id = SelectField("Department", coerce=int, validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[("", "All"), ("active", "Active"), ("inactive", "Inactive")],
        validators=[Optional()],
    )
    submit = SubmitField("Filter")

    class Meta:
        csrf = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department_id.choices = [(0, "All Departments")] + [
            (d.id, d.name) for d in Department.query.order_by(Department.name).all()
        ]
