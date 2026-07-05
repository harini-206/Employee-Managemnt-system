from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")  # 'admin' or 'employee'
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship(
        "Employee", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    # Flask-Login expects `is_active`; keep our own flag distinct.
    @property
    def is_active(self):
        return self.is_active_account

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    employees = db.relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department {self.name}>"


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True)

    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    designation = db.Column(db.String(100))
    date_joined = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Float, default=0.0)
    address = db.Column(db.String(255))
    profile_pic = db.Column(db.String(255), default="default.png")
    is_active = db.Column(db.Boolean, default=True)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    department = db.relationship("Department", back_populates="employees")

    user = db.relationship("User", back_populates="employee")

    attendances = db.relationship(
        "Attendance", back_populates="employee", cascade="all, delete-orphan"
    )
    leave_requests = db.relationship(
        "LeaveRequest", back_populates="employee", cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee {self.full_name}>"


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (db.UniqueConstraint("employee_id", "date", name="uq_employee_date"),)

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(20), default="Present")  # Present, Absent, Half Day, Leave
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    remarks = db.Column(db.String(255))

    employee = db.relationship("Employee", back_populates="attendances")

    def __repr__(self):
        return f"<Attendance {self.employee_id} {self.date} {self.status}>"


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(50), default="Casual")
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")  # Pending, Approved, Rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    review_comment = db.Column(db.String(255))

    employee = db.relationship("Employee", back_populates="leave_requests")

    @property
    def days_requested(self):
        return (self.end_date - self.start_date).days + 1

    def __repr__(self):
        return f"<LeaveRequest {self.employee_id} {self.status}>"
