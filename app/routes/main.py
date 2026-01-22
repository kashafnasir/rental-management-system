from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Property, Tenant, Lease, Payment, MaintenanceRequest
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Landing page"""
    # Get some stats for landing page
    total_properties = Property.query.count()
    available_properties = Property.query.filter_by(availability_status='available').count()
    
    return render_template('index.html', 
                         total_properties=total_properties,
                         available_properties=available_properties)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get user's properties
    if current_user.role == 'admin':
        properties = Property.query.all()
        leases = Lease.query.all()
        payments = Payment.query.all()
        maintenance_requests = MaintenanceRequest.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        leases = Lease.query.filter(Lease.property_id.in_(property_ids)).all() if property_ids else []
        payments = Payment.query.join(Lease).filter(Lease.property_id.in_(property_ids)).all() if property_ids else []
        maintenance_requests = MaintenanceRequest.query.filter(MaintenanceRequest.property_id.in_(property_ids)).all() if property_ids else []
    
    # Calculate statistics
    stats = {
        'total_properties': len(properties),
        'available_properties': len([p for p in properties if p.availability_status == 'available']),
        'occupied_properties': len([p for p in properties if p.availability_status == 'occupied']),
        'active_leases': len([l for l in leases if l.status == 'active']),
        'total_rent': sum([l.monthly_rent for l in leases if l.status == 'active']),
        'pending_payments': len([p for p in payments if p.status == 'pending']),
        'pending_maintenance': len([m for m in maintenance_requests if m.status == 'pending']),
    }
    
    # Recent activities
    recent_payments = sorted(payments, key=lambda x: x.created_at, reverse=True)[:5]
    recent_maintenance = sorted(maintenance_requests, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Upcoming lease expirations (within 30 days)
    today = datetime.now().date()
    expiring_soon = [l for l in leases if l.end_date and l.end_date <= today + timedelta(days=30) and l.end_date >= today]
    
    return render_template('dashboard.html',
                         stats=stats,
                         recent_payments=recent_payments,
                         recent_maintenance=recent_maintenance,
                         expiring_leases=expiring_soon)

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html')

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_password = request.form.get('current_password')
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('main.profile'))
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('main.profile'))