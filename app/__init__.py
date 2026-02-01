from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    # JWT Error Loaders
    from flask import redirect, url_for, flash

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        flash("Your session has expired. Please login again.", "warning")
        return redirect(url_for('main.login'))

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        flash("You need to login to access this page.", "warning")
        return redirect(url_for('main.login'))

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Error Handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        from flask import flash, redirect, url_for
        flash('File too large. Maximum size is 16MB.', 'danger')
        return redirect(url_for('main.admin_list'))

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    with app.app_context():
        # Import models inside context to ensure they are registered
        from app.models import User, Document, Setting
        db.create_all()

        # Seed Superuser
        if not User.query.filter_by(username='rachitbishnoi16@gmail.com').first():
            hashed_pw = bcrypt.generate_password_hash('tircha@12345').decode('utf-8')
            new_user = User(username='rachitbishnoi16@gmail.com', password_hash=hashed_pw, role='SUPERUSER')
            db.session.add(new_user)
            db.session.commit()
            print("Superuser seeded: rachitbishnoi16@gmail.com")

        # Seed Admin
        if not User.query.filter_by(username='admin@gmail.com').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            new_admin = User(username='admin@gmail.com', password_hash=hashed_pw, role='ADMIN')
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user seeded: admin@gmail.com")

    return app
