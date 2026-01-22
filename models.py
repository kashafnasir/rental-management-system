from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='owner')
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True, cascade='all, delete-orphan')
    maintenance_requests = db.relationship('MaintenanceRequest', backref='assigned_staff', lazy=True,
                                          foreign_keys='MaintenanceRequest.assigned_staff_id')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
    """Property model"""
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    availability_status = db.Column(db.String(20), default='available')
    description = db.Column(db.Text)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    area_sqft = db.Column(db.Float)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    leases = db.relationship('Lease', backref='property', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Property {self.address}>'

class Tenant(db.Model):
    """Tenant model"""
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    national_id = db.Column(db.String(50), nullable=False)
    emergency_contact = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    move_in_date = db.Column(db.Date)
    
    # Relationships
    user = db.relationship('User', backref='tenant_profile', foreign_keys=[user_id])
    leases = db.relationship('Lease', backref='tenant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.user.username}>'

class Lease(db.Model):
    """Lease agreement model"""
    __tablename__ = 'leases'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float)
    terms_conditions = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='lease', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lease {self.id}>'

class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    receipt_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id}>'

class MaintenanceRequest(db.Model):
    """Maintenance request model"""
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    request_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    property = db.relationship('Property', backref='maintenance_requests')
    tenant_relation = db.relationship('Tenant', backref='maintenance_requests')
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.id}>'

class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}>'