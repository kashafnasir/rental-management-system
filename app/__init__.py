from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import auth, main, properties, tenants, leases, payments, maintenance
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(properties.bp)
    app.register_blueprint(tenants.bp)
    app.register_blueprint(leases.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(maintenance.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if doesn't exist
        from app.models import User
        admin = User.query.filter_by(email='admin@rental.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@rental.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: admin@rental.com / admin123")
    
    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))