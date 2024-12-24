from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import *

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/customer/<int:customer_id>')
@login_required
def view_customer_profile(customer_id):
  customer = Customer.query.filter_by(id=customer_id).first()
  if customer:
    user = customer.user

    if current_user.role == UserRole.CUSTOMER and current_user.id != user.id:
      flash('You do not have permission to view this profile.', 'danger')
      return redirect(url_for('public.index'))

    return render_template('dashboard/profile/customer_profile.html', user=user)

  flash('Customer not found.', 'danger')
  return redirect(url_for('public.index'))


@bp.route('/professional/<int:professional_id>')
@login_required
def view_professional_profile(professional_id):
  professional = Professional.query.filter_by(id=professional_id).first()
  if professional:
    user = professional.user

    if current_user.role == UserRole.PROFESSIONAL and current_user.id != user.id:
      flash('You do not have permission to view this profile.', 'danger')
      return redirect(url_for('public.index'))

    return render_template('dashboard/profile/professional_profile.html', user=user)

  flash('Professional not found.', 'danger')
  return redirect(url_for('public.index'))


@bp.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer_profile(customer_id):
  customer = Customer.query.filter_by(id=customer_id).first()
  if customer:
    user = customer.user

    if current_user.id == user.id or current_user.role == UserRole.ADMIN:
      if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        user.address = request.form['address']
        user.postal_code = request.form['postal_code']
        user.city_id = request.form['city_id']

        try:
          db.session.commit()
          flash('Profile updated successfully.', 'success')
        except Exception as e:
          db.session.rollback()
          flash('An error occurred while updating the profile.', 'danger')

        return redirect(url_for('profile.view_customer_profile', customer_id=customer.id))

      return render_template('dashboard/profile/edit_customer_profile.html',
                             user=user, cities=City.query.all())

  flash('Customer not found.', 'danger')
  return redirect(url_for('public.index'))


@bp.route('/edit_professional/<int:professional_id>', methods=['GET', 'POST'])
@login_required
def edit_professional_profile(professional_id):
  professional = Professional.query.filter_by(id=professional_id).first()
  if professional:
    user = professional.user

    if current_user.id == user.id or current_user.role == UserRole.ADMIN:
      if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone_number = request.form['phone_number']
        user.address = request.form['address']
        user.postal_code = request.form['postal_code']
        user.city_id = request.form['city_id']
        professional.about_me = request.form['about_me']
        professional.service_type_id = request.form['service_type']

        try:
          db.session.commit()
          flash('Profile updated successfully.', 'success')
        except Exception as e:
          db.session.rollback()
          flash('An error occurred while updating the profile.', 'danger')

        return redirect(url_for('profile.view_professional_profile', professional_id=professional.id))

      return render_template('dashboard/profile/edit_professional_profile.html', user=user,
                             cities=City.query.all(),
                             service_types=ServiceType.query.all())

  flash('Professional not found.', 'danger')
  return redirect(url_for('public.index'))
