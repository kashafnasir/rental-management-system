from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Property
from werkzeug.utils import secure_filename
import os

bp = Blueprint('properties', __name__, url_prefix='/properties')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def list_properties():
    """List all properties"""
    if current_user.role == 'admin':
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
    
    return render_template('properties/list.html', properties=properties)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_property():
    """Add new property"""
    if request.method == 'POST':
        try:
            # Handle file upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Create unique filename
                    import uuid
                    filename = f"{uuid.uuid4()}_{filename}"
                    filepath = os.path.join('app/static/uploads', filename)
                    file.save(filepath)
                    image_path = f"uploads/{filename}"
            
            # Create property
            property = Property(
                owner_id=current_user.id,
                property_type=request.form.get('property_type'),
                address=request.form.get('address'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                rent_amount=float(request.form.get('rent_amount')),
                availability_status=request.form.get('availability_status', 'available'),
                description=request.form.get('description'),
                bedrooms=int(request.form.get('bedrooms', 0)),
                bathrooms=int(request.form.get('bathrooms', 0)),
                area_sqft=float(request.form.get('area_sqft', 0)),
                image_path=image_path
            )
            
            db.session.add(property)
            db.session.commit()
            
            flash('Property added successfully!', 'success')
            return redirect(url_for('properties.list_properties'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding property: {str(e)}', 'error')
    
    return render_template('properties/add.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_property(id):
    """Edit existing property"""
    property = Property.query.get_or_404(id)
    
    # Check ownership
    if current_user.role != 'admin' and property.owner_id != current_user.id:
        flash('You do not have permission to edit this property.', 'error')
        return redirect(url_for('properties.list_properties'))
    
    if request.method == 'POST':
        try:
            # Handle file upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    # Delete old image if exists
                    if property.image_path:
                        old_path = os.path.join('app/static', property.image_path)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    filename = secure_filename(file.filename)
                    import uuid
                    filename = f"{uuid.uuid4()}_{filename}"
                    filepath = os.path.join('app/static/uploads', filename)
                    file.save(filepath)
                    property.image_path = f"uploads/{filename}"
            
            # Update property fields
            property.property_type = request.form.get('property_type')
            property.address = request.form.get('address')
            property.city = request.form.get('city')
            property.state = request.form.get('state')
            property.rent_amount = float(request.form.get('rent_amount'))
            property.availability_status = request.form.get('availability_status')
            property.description = request.form.get('description')
            property.bedrooms = int(request.form.get('bedrooms', 0))
            property.bathrooms = int(request.form.get('bathrooms', 0))
            property.area_sqft = float(request.form.get('area_sqft', 0))
            
            db.session.commit()
            
            flash('Property updated successfully!', 'success')
            return redirect(url_for('properties.list_properties'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating property: {str(e)}', 'error')
    
    return render_template('properties/edit.html', property=property)

@bp.route('/view/<int:id>')
@login_required
def view_property(id):
    """View property details"""
    property = Property.query.get_or_404(id)
    return render_template('properties/view.html', property=property)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_property(id):
    """Delete property"""
    property = Property.query.get_or_404(id)
    
    # Check ownership
    if current_user.role != 'admin' and property.owner_id != current_user.id:
        flash('You do not have permission to delete this property.', 'error')
        return redirect(url_for('properties.list_properties'))
    
    try:
        # Delete associated image if exists
        if property.image_path:
            image_path = os.path.join('app/static', property.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(property)
        db.session.commit()
        
        flash('Property deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting property: {str(e)}', 'error')
    
    return redirect(url_for('properties.list_properties'))