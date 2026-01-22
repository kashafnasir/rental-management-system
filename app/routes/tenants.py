from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Tenant, User
from datetime import datetime

bp = Blueprint('tenants', __name__, url_prefix='/tenants')

@bp.route('/')
@login_required
def list_tenants():
    """List all tenants"""
    tenants = Tenant.query.all()
    return render_template('tenants/list.html', tenants=tenants)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_tenant():
    """Add new tenant"""
    if request.method == 'POST':
        try:
            # First create or get user
            email = request.form.get('email')
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                # Check if already a tenant
                if existing_user.tenant_profile:
                    flash('This user is already registered as a tenant.', 'error')
                    return redirect(url_for('tenants.list_tenants'))
                user = existing_user
            else:
                # Create new user for tenant
                user = User(
                    username=request.form.get('username'),
                    email=email,
                    phone=request.form.get('phone'),
                    role='tenant'
                )
                user.set_password(request.form.get('password', 'changeme123'))
                db.session.add(user)
                db.session.flush()  # Get user ID
            
            # Create tenant profile
            tenant = Tenant(
                user_id=user.id,
                national_id=request.form.get('national_id'),
                emergency_contact=request.form.get('emergency_contact'),
                occupation=request.form.get('occupation'),
                move_in_date=datetime.strptime(request.form.get('move_in_date'), '%Y-%m-%d').date() if request.form.get('move_in_date') else None
            )
            
            db.session.add(tenant)
            db.session.commit()
            
            flash('Tenant added successfully!', 'success')
            return redirect(url_for('tenants.list_tenants'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding tenant: {str(e)}', 'error')
    
    return render_template('tenants/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tenant(id):
    """Edit tenant"""
    tenant = Tenant.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update user info
            tenant.user.username = request.form.get('username')
            tenant.user.email = request.form.get('email')
            tenant.user.phone = request.form.get('phone')
            
            # Update tenant info
            tenant.national_id = request.form.get('national_id')
            tenant.emergency_contact = request.form.get('emergency_contact')
            tenant.occupation = request.form.get('occupation')
            
            move_in_date = request.form.get('move_in_date')
            if move_in_date:
                tenant.move_in_date = datetime.strptime(move_in_date, '%Y-%m-%d').date()
            
            db.session.commit()
            flash('Tenant updated successfully!', 'success')
            return redirect(url_for('tenants.list_tenants'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating tenant: {str(e)}', 'error')
    
    return render_template('tenants/edit.html', tenant=tenant)

@bp.route('/view/<int:id>')
@login_required
def view_tenant(id):
    """View tenant details"""
    tenant = Tenant.query.get_or_404(id)
    return render_template('tenants/view.html', tenant=tenant)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_tenant(id):
    """Delete tenant"""
    tenant = Tenant.query.get_or_404(id)
    
    try:
        # Check if tenant has active leases
        if tenant.leases and any(l.status == 'active' for l in tenant.leases):
            flash('Cannot delete tenant with active leases.', 'error')
            return redirect(url_for('tenants.list_tenants'))
        
        db.session.delete(tenant)
        db.session.commit()
        
        flash('Tenant deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting tenant: {str(e)}', 'error')
    
    return redirect(url_for('tenants.list_tenants'))