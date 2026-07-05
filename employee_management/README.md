# Employee Management System (Flask)

A full-featured Employee Management web app built with Flask, demonstrating
Blueprints, SQLAlchemy ORM, Flask-Login, WTForms, Jinja2, file uploads,
pagination, CRUD, and role-based access control (RBAC).

## Modules

- **User Authentication** — Admin & Employee roles (Flask-Login + password hashing)
- **Employee CRUD** — add / edit / delete / view, with profile picture upload
- **Department Management** — CRUD for departments
- **Attendance Management** — admins mark attendance; employees view their own
- **Leave Request & Approval** — employees apply, admins approve/reject
- **Dashboard with Statistics** — different views for admin vs. employee
- **Search & Filters** — employee search by name/email/designation, filter by department/status
- **Profile Management** — employees update phone/address/photo, change password

## Project layout

```
employee_management/
├── app/
│   ├── __init__.py            # app factory, blueprint registration
│   ├── extensions.py          # db, login_manager
│   ├── models.py              # User, Employee, Department, Attendance, LeaveRequest
│   ├── decorators.py          # role_required / admin_required
│   ├── auth/                  # login, register, logout
│   ├── dashboard/             # role-aware dashboard with stats
│   ├── employees/             # employee CRUD, search, pagination, uploads
│   ├── departments/           # department CRUD
│   ├── attendance/            # mark / list / view attendance
│   ├── leaves/                # apply / review / cancel leave requests
│   ├── profile/               # self-service profile + password change
│   ├── static/                # css, uploaded profile pictures
│   └── templates/             # Jinja2 templates (Bootstrap 5 UI)
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   cd employee_management
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Initialize the database**

   The app auto-creates tables on first run via `run.py`, but you can also
   use Flask-Migrate style manual creation:

   ```bash
   python run.py
   ```

   This starts the dev server AND creates `app/ems.db` (SQLite) automatically.
   Stop the server (Ctrl+C) once you see it's running, or leave it running
   and open a second terminal for the next step.

3. **Create the default admin account**

   ```bash
   export FLASK_APP=run.py         # Windows: set FLASK_APP=run.py
   flask seed-admin
   ```

   This creates:
   - username: `admin`
   - password: `Admin@123`

   **Change this password after first login** (Profile → Change Password).

4. **Run the app**

   ```bash
   python run.py
   ```

   Visit http://127.0.0.1:5000

## How roles work

- **Admin**: full access — manage employees, departments, attendance, and
  approve/reject leave requests.
- **Employee**: self-registers via `/register` (role fixed to "employee"),
  can view their own attendance, apply for leave, and edit their profile.
- An employee **user account** is separate from an **Employee record**.
  After an employee registers, an admin should create/link an Employee
  record with the same email so the employee's dashboard, attendance, and
  leave pages populate correctly. (A quick way: when adding an Employee,
  use the same email the user registered with — you can extend the
  `Employee` model/admin form to pick an existing `User` to link to
  `user_id` if you want tighter automatic linking.)

## Key implementation notes

- **Flask Blueprints**: each module (`auth`, `employees`, `departments`,
  `attendance`, `leaves`, `dashboard`, `profile`) is a self-contained
  blueprint registered in `app/__init__.py`.
- **RBAC**: `app/decorators.py` provides `@admin_required` / `@role_required(...)`
  used alongside Flask-Login's `@login_required`.
- **WTForms**: all forms (`LoginForm`, `EmployeeForm`, `LeaveRequestForm`, etc.)
  use `Flask-WTF` with CSRF protection and server-side validation.
- **File uploads**: profile pictures are validated by extension, renamed with
  a UUID, and stored under `app/static/uploads/profile_pics/`.
- **Pagination**: employee list, attendance list, and leave list use
  SQLAlchemy's `.paginate()`, rendered via `templates/includes/pagination.html`.
- **Search & filters**: implemented with SQLAlchemy `ilike` queries and
  query-string parameters (`?q=...&department_id=...&status=...`).

## Extending this project

- Add Flask-Migrate for schema migrations instead of `db.create_all()`.
- Add email notifications on leave approval/rejection.
- Add an admin screen to link an existing `User` to an `Employee` record.
- Add unit tests with `pytest` + `Flask-Testing`.
- Swap SQLite for PostgreSQL/MySQL by changing `DATABASE_URL`.
