from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Lease, Property, Tenant
from datetime import datetime

bp = Blueprint('leases', __name__, url_prefix='/leases')

@bp.route('/')
@login_required
def list_leases():
    """List all leases"""
    if current_user.role == 'admin':
        leases = Lease.query.all()
    else:
        # Get leases for user's properties
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        leases = Lease.query.filter(Lease.property_id.in_(property_ids)).all() if property_ids else []
    
    return render_template('leases/list.html', leases=leases)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_lease():
    """Add new lease"""
    if request.method == 'POST':
        try:
            property_id = int(request.form.get('property_id'))
            tenant_id = int(request.form.get('tenant_id'))
            
            # Validate property ownership
            property = Property.query.get_or_404(property_id)
            if current_user.role != 'admin' and property.owner_id != current_user.id:
                flash('You do not have permission to create a lease for this property.', 'error')
                return redirect(url_for('leases.list_leases'))
            
            # Create lease
            lease = Lease(
                property_id=property_id,
                tenant_id=tenant_id,
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
                monthly_rent=float(request.form.get('monthly_rent')),
                security_deposit=float(request.form.get('security_deposit', 0)),
                terms_conditions=request.form.get('terms_conditions'),
                status=request.form.get('status', 'active')
            )
            
            # Update property status if lease is active
            if lease.status == 'active':
                property.availability_status = 'occupied'
            
            db.session.add(lease)
            db.session.commit()
            
            flash('Lease created successfully!', 'success')
            return redirect(url_for('leases.list_leases'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating lease: {str(e)}', 'error')
    
    # Get available properties and tenants
    if current_user.role == 'admin':
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    
    tenants = Tenant.query.all()
    
    return render_template('leases/add.html', properties=properties, tenants=tenants)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lease(id):
    """Edit lease"""
    lease = Lease.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and lease.property.owner_id != current_user.id:
        flash('You do not have permission to edit this lease.', 'error')
        return redirect(url_for('leases.list_leases'))
    
    if request.method == 'POST':
        try:
            old_status = lease.status
            
            lease.property_id = int(request.form.get('property_id'))
            lease.tenant_id = int(request.form.get('tenant_id'))
            lease.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            lease.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            lease.monthly_rent = float(request.form.get('monthly_rent'))
            lease.security_deposit = float(request.form.get('security_deposit', 0))
            lease.terms_conditions = request.form.get('terms_conditions')
            lease.status = request.form.get('status')
            
            # Update property status based on lease status change
            if old_status != lease.status:
                if lease.status == 'active':
                    lease.property.availability_status = 'occupied'
                elif lease.status == 'expired' or lease.status == 'terminated':
                    lease.property.availability_status = 'available'
            
            db.session.commit()
            flash('Lease updated successfully!', 'success')
            return redirect(url_for('leases.list_leases'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating lease: {str(e)}', 'error')
    
    # Get properties and tenants
    if current_user.role == 'admin':
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    
    tenants = Tenant.query.all()
    
    return render_template('leases/edit.html', lease=lease, properties=properties, tenants=tenants)

@bp.route('/view/<int:id>')
@login_required
def view_lease(id):
    """View lease details"""
    lease = Lease.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and lease.property.owner_id != current_user.id:
        flash('You do not have permission to view this lease.', 'error')
        return redirect(url_for('leases.list_leases'))
    
    return render_template('leases/view.html', lease=lease)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_lease(id):
    """Delete lease"""
    lease = Lease.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and lease.property.owner_id != current_user.id:
        flash('You do not have permission to delete this lease.', 'error')
        return redirect(url_for('leases.list_leases'))
    
    try:
        # Update property status
        if lease.status == 'active':
            lease.property.availability_status = 'available'
        
        db.session.delete(lease)
        db.session.commit()
        
        flash('Lease deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting lease: {str(e)}', 'error')
    
    return redirect(url_for('leases.list_leases'))