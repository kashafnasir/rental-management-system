from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import MaintenanceRequest, Property, Tenant
from datetime import datetime

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@bp.route('/')
@login_required
def list_requests():
    """List all maintenance requests"""
    if current_user.role == 'admin':
        requests = MaintenanceRequest.query.all()
    else:
        # Get requests for user's properties
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        requests = MaintenanceRequest.query.filter(MaintenanceRequest.property_id.in_(property_ids)).all() if property_ids else []
    
    return render_template('maintenance/list.html', requests=requests)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_request():
    """Add new maintenance request"""
    if request.method == 'POST':
        try:
            property_id = int(request.form.get('property_id'))
            property_obj = Property.query.get_or_404(property_id)
            
            # Check permission
            if current_user.role != 'admin' and property_obj.owner_id != current_user.id:
                flash('You do not have permission to create maintenance requests for this property.', 'error')
                return redirect(url_for('maintenance.list_requests'))
            
            # Create maintenance request
            maintenance_request = MaintenanceRequest(
                property_id=property_id,
                tenant_id=int(request.form.get('tenant_id')),
                request_type=request.form.get('request_type'),
                description=request.form.get('description'),
                priority=request.form.get('priority', 'medium'),
                status=request.form.get('status', 'pending')
            )
            
            # Assign staff if provided
            assigned_staff_id = request.form.get('assigned_staff_id')
            if assigned_staff_id:
                maintenance_request.assigned_staff_id = int(assigned_staff_id)
            
            db.session.add(maintenance_request)
            db.session.commit()
            
            flash('Maintenance request created successfully!', 'success')
            return redirect(url_for('maintenance.list_requests'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating maintenance request: {str(e)}', 'error')
    
    # Get properties and tenants
    if current_user.role == 'admin':
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    
    tenants = Tenant.query.all()
    
    return render_template('maintenance/add.html', properties=properties, tenants=tenants)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_request(id):
    """Edit maintenance request"""
    maintenance_request = MaintenanceRequest.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and maintenance_request.property.owner_id != current_user.id:
        flash('You do not have permission to edit this maintenance request.', 'error')
        return redirect(url_for('maintenance.list_requests'))
    
    if request.method == 'POST':
        try:
            maintenance_request.property_id = int(request.form.get('property_id'))
            maintenance_request.tenant_id = int(request.form.get('tenant_id'))
            maintenance_request.request_type = request.form.get('request_type')
            maintenance_request.description = request.form.get('description')
            maintenance_request.priority = request.form.get('priority')
            
            old_status = maintenance_request.status
            maintenance_request.status = request.form.get('status')
            
            # Set resolved date if status changed to resolved
            if old_status != 'resolved' and maintenance_request.status == 'resolved':
                maintenance_request.resolved_at = datetime.utcnow()
            
            # Assign staff
            assigned_staff_id = request.form.get('assigned_staff_id')
            if assigned_staff_id:
                maintenance_request.assigned_staff_id = int(assigned_staff_id)
            
            db.session.commit()
            flash('Maintenance request updated successfully!', 'success')
            return redirect(url_for('maintenance.list_requests'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating maintenance request: {str(e)}', 'error')
    
    # Get properties and tenants
    if current_user.role == 'admin':
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    
    tenants = Tenant.query.all()
    
    return render_template('maintenance/edit.html', request=maintenance_request, properties=properties, tenants=tenants)

@bp.route('/view/<int:id>')
@login_required
def view_request(id):
    """View maintenance request details"""
    maintenance_request = MaintenanceRequest.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and maintenance_request.property.owner_id != current_user.id:
        flash('You do not have permission to view this maintenance request.', 'error')
        return redirect(url_for('maintenance.list_requests'))
    
    return render_template('maintenance/view.html', request=maintenance_request)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_request(id):
    """Delete maintenance request"""
    maintenance_request = MaintenanceRequest.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and maintenance_request.property.owner_id != current_user.id:
        flash('You do not have permission to delete this maintenance request.', 'error')
        return redirect(url_for('maintenance.list_requests'))
    
    try:
        db.session.delete(maintenance_request)
        db.session.commit()
        
        flash('Maintenance request deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting maintenance request: {str(e)}', 'error')
    
    return redirect(url_for('maintenance.list_requests'))