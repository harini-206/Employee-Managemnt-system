import os

from app import create_app
from app.extensions import db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    from app.models import User, Employee, Department, Attendance, LeaveRequest

    return {
        "db": db,
        "User": User,
        "Employee": Employee,
        "Department": Department,
        "Attendance": Attendance,
        "LeaveRequest": LeaveRequest,
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
