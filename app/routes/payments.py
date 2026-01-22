from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Payment, Lease, Property
from datetime import datetime

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/')
@login_required
def list_payments():
    """List all payments"""
    if current_user.role == 'admin':
        payments = Payment.query.all()
    else:
        # Get payments for user's properties
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        payments = Payment.query.join(Lease).filter(Lease.property_id.in_(property_ids)).all() if property_ids else []
    
    return render_template('payments/list.html', payments=payments)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    """Add new payment"""
    if request.method == 'POST':
        try:
            lease_id = int(request.form.get('lease_id'))
            lease = Lease.query.get_or_404(lease_id)
            
            # Check permission
            if current_user.role != 'admin' and lease.property.owner_id != current_user.id:
                flash('You do not have permission to record payments for this lease.', 'error')
                return redirect(url_for('payments.list_payments'))
            
            # Create payment
            payment = Payment(
                lease_id=lease_id,
                amount=float(request.form.get('amount')),
                due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
                paid_date=datetime.strptime(request.form.get('paid_date'), '%Y-%m-%d').date() if request.form.get('paid_date') else None,
                payment_method=request.form.get('payment_method'),
                status=request.form.get('status', 'pending')
            )
            
            db.session.add(payment)
            db.session.commit()
            
            flash('Payment recorded successfully!', 'success')
            return redirect(url_for('payments.list_payments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording payment: {str(e)}', 'error')
    
    # Get leases
    if current_user.role == 'admin':
        leases = Lease.query.filter_by(status='active').all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        leases = Lease.query.filter(Lease.property_id.in_(property_ids), Lease.status == 'active').all() if property_ids else []
    
    return render_template('payments/add.html', leases=leases)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_payment(id):
    """Edit payment"""
    payment = Payment.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and payment.lease.property.owner_id != current_user.id:
        flash('You do not have permission to edit this payment.', 'error')
        return redirect(url_for('payments.list_payments'))
    
    if request.method == 'POST':
        try:
            payment.lease_id = int(request.form.get('lease_id'))
            payment.amount = float(request.form.get('amount'))
            
            due_date = request.form.get('due_date')
            payment.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
            
            paid_date = request.form.get('paid_date')
            payment.paid_date = datetime.strptime(paid_date, '%Y-%m-%d').date() if paid_date else None
            
            payment.payment_method = request.form.get('payment_method')
            payment.status = request.form.get('status')
            
            db.session.commit()
            flash('Payment updated successfully!', 'success')
            return redirect(url_for('payments.list_payments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating payment: {str(e)}', 'error')
    
    # Get leases
    if current_user.role == 'admin':
        leases = Lease.query.all()
    else:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        leases = Lease.query.filter(Lease.property_id.in_(property_ids)).all() if property_ids else []
    
    return render_template('payments/edit.html', payment=payment, leases=leases)

@bp.route('/view/<int:id>')
@login_required
def view_payment(id):
    """View payment details"""
    payment = Payment.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and payment.lease.property.owner_id != current_user.id:
        flash('You do not have permission to view this payment.', 'error')
        return redirect(url_for('payments.list_payments'))
    
    return render_template('payments/view.html', payment=payment)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_payment(id):
    """Delete payment"""
    payment = Payment.query.get_or_404(id)
    
    # Check permission
    if current_user.role != 'admin' and payment.lease.property.owner_id != current_user.id:
        flash('You do not have permission to delete this payment.', 'error')
        return redirect(url_for('payments.list_payments'))
    
    try:
        db.session.delete(payment)
        db.session.commit()
        
        flash('Payment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting payment: {str(e)}', 'error')
    
    return redirect(url_for('payments.list_payments'))