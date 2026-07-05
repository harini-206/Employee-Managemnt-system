import os

from flask import Flask, render_template

from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # ---- Blueprints ----
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.employees.routes import employees_bp
    from app.departments.routes import departments_bp
    from app.attendance.routes import attendance_bp
    from app.leaves.routes import leaves_bp
    from app.profile.routes import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(departments_bp, url_prefix="/departments")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(leaves_bp, url_prefix="/leaves")
    app.register_blueprint(profile_bp, url_prefix="/profile")

    # ---- Error handlers ----
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    # ---- CLI: seed database with an admin user ----
    @app.cli.command("seed-admin")
    def seed_admin():
        """Create a default admin user (username: admin / password: Admin@123)."""
        from app.models import User

        with app.app_context():
            if User.query.filter_by(username="admin").first():
                print("Admin already exists.")
                return
            admin = User(username="admin", email="admin@example.com", role="admin")
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created -> username: admin, password: Admin@123")

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from flask import request, url_for

        def url_for_page(page):
            args = request.args.to_dict(flat=True)
            args["page"] = page
            return url_for(request.endpoint, **args)

        return {"current_year": datetime.utcnow().year, "url_for_page": url_for_page}

    return app
