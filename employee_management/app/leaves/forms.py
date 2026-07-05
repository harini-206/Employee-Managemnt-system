from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


class LeaveRequestForm(FlaskForm):
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    leave_type = SelectField(
        "Leave Type",
        choices=[("Casual", "Casual"), ("Sick", "Sick"), ("Earned", "Earned"), ("Unpaid", "Unpaid")],
        validators=[DataRequired()],
    )
    reason = TextAreaField("Reason", validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField("Submit Request")

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("End date cannot be before start date.")


class LeaveReviewForm(FlaskForm):
    status = SelectField(
        "Decision", choices=[("Approved", "Approve"), ("Rejected", "Reject")], validators=[DataRequired()]
    )
    review_comment = StringField("Comment", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Submit Decision")
