from flask import Blueprint, render_template, request, abort, flash, redirect, url_for
from flask_login import current_user, login_required
from controllers.security import role_required
from database.models import *
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')


"""
https://patorjk.com/software/taag/#p=display&f=Electronic&t=pages

 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          
▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌ ▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌▐░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌ ▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌                    ▐░▌
▐░▌          ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄█░▌
▐░▌          ▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀            ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀ 

"""


@bp.route('/dashboard')
@login_required
@role_required(UserRole.ADMIN)
def home():
  customers = db.session.query(Customer).all()
  professionals = db.session.query(Professional).all()
  service_types = db.session.query(ServiceType).all()
  services = db.session.query(Service).all()
  bookings = db.session.query(Booking).all()
  cities = db.session.query(City).all()

  return render_template('dashboard/admin/home.html',
                         customers=customers,
                         professionals=professionals,
                         service_types=service_types,
                         services=services,
                         bookings=bookings,
                         cities=cities
                         )


@bp.route('/search')
@login_required
@role_required(UserRole.ADMIN)
def search():
  cities = db.session.query(City).all()
  service_types = db.session.query(ServiceType).all()
  return render_template('dashboard/admin/search.html',
                         cities=cities,
                         service_types=service_types
                         )


@bp.route('/search-results')
@login_required
@role_required(UserRole.ADMIN)
def search_results():
  role = request.args.get('role')
  name = request.args.get('name').strip()
  address = request.args.get('address').strip()
  postal_code = request.args.get('postal_code').strip()
  phone_number = request.args.get('phone_number').strip()
  city_id = request.args.get('city')
  service_type_id = request.args.get('service_type_id')

  query = None
  if role == 'customer':
    query = db.session.query(Customer).join(User).filter(User.role == UserRole.CUSTOMER)
  elif role == 'professional':
    query = db.session.query(Professional).join(User).filter(User.role == UserRole.PROFESSIONAL)

  if name:
    query = query.filter(User.name.ilike(f"%{name}%"))
  if address:
    query = query.filter(User.address.ilike(f"%{address}%"))
  if postal_code:
    query = query.filter(User.postal_code.ilike(f"%{postal_code}%"))
  if city_id:
    query = query.filter(User.city_id == city_id)
  if phone_number:
    query = query.filter(User.phone_number.ilike(f"%{phone_number}%"))
  if service_type_id:
    query = query.filter(Professional.service_type_id == service_type_id)

  results = query.all()
  return render_template('dashboard/admin/search_results.html',
                         role=role,
                         results=results)


@bp.route('/summary')
@login_required
@role_required(UserRole.ADMIN)
def summary():
  total_bookings = db.session.query(Booking).count()

  # count ratings by 1-5 stars with percentages
  ratings_count = db.session.query(
      Booking.review_stars,
      func.count(Booking.id)
  ).filter(
      Booking.review_stars.isnot(None)
  ).group_by(
      Booking.review_stars
  ).all()

  rated_bookings = 0
  for star, count in ratings_count:
    rated_bookings += count

  ratings_dict = [
      {
          "stars": star,
          "count": count,
          "percentage": (count / rated_bookings * 100) if rated_bookings else 0
      }
      for star, count in ratings_count
  ]

  # ensure all 1-5 stars are present
  for star in range(1, 6):
    if not any(r["stars"] == star for r in ratings_dict):
      ratings_dict.append({"stars": star, "count": 0, "percentage": 0})
  ratings_dict.sort(key=lambda r: r["stars"])

  # count bookings by status with percentages
  booking_status_counts = db.session.query(
      Booking.status,
      func.count(Booking.id)
  ).group_by(Booking.status).all()

  status_dict = [
      {
          "status": status.name.title(),
          "count": count,
          "percentage": (count / total_bookings * 100) if total_bookings else 0
      }
      for status, count in booking_status_counts
  ]

  # ensure all statuses are present
  for status in BookingStatus:
    if not any(s["status"] == status.name.title() for s in status_dict):
      status_dict.append({"status": status.name.title(), "count": 0, "percentage": 0})
  status_dict.sort(key=lambda s: s["status"])

  # today's bookings count
  today = datetime.today().date()
  today_created = db.session.query(Booking).filter(
      func.date(Booking.created_on) == today
  ).count()
  today_assigned = db.session.query(Booking).filter(
      func.date(Booking.assigned_on) == today
  ).count()
  today_closed = db.session.query(Booking).filter(
      func.date(Booking.closed_on) == today
  ).count()

  return render_template(
      'dashboard/admin/summary.html',
      ratings_dict=ratings_dict,
      status_dict=status_dict,
      total_bookings=total_bookings,
      today_created=today_created,
      today_assigned=today_assigned,
      today_closed=today_closed
  )


"""
https://patorjk.com/software/taag/#p=display&f=Electronic&t=rpcs

 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ 
▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌          
▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌          ▐░█▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌
▐░█▀▀▀▀█░█▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░▌           ▀▀▀▀▀▀▀▀▀█░▌
▐░▌     ▐░▌  ▐░▌          ▐░▌                    ▐░▌
▐░▌      ▐░▌ ▐░▌          ▐░█▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄█░▌
▐░▌       ▐░▌▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀         ▀  ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀ 
                                                    
"""


@bp.route('/block_user/<int:user_id>')
@login_required
@role_required(UserRole.ADMIN)
def block_user(user_id):
  user = User.query.filter_by(id=user_id).first()
  user.is_blocked = True
  db.session.commit()

  flash(f'{user.role.name.capitalize()} "{user.name}" has been blocked.', 'success')
  anchor = 'professionals_table' if user.role.name == 'PROFESSIONAL' \
      else 'customers_table'
  return redirect(url_for('admin_dashboard.home', _anchor=anchor))


@bp.route('/unblock_user/<int:user_id>')
@login_required
@role_required(UserRole.ADMIN)
def unblock_user(user_id):
  user = User.query.filter_by(id=user_id).first()
  user.is_blocked = False
  db.session.commit()

  flash(f'{user.role.name.capitalize()} "{user.name}" has been unblocked.', 'success')
  anchor = 'professionals_table' if user.role.name == 'PROFESSIONAL' \
      else 'customers_table'
  return redirect(url_for('admin_dashboard.home', _anchor=anchor))


@bp.route('/verify_professional/<int:professional_id>')
@login_required
@role_required(UserRole.ADMIN)
def verify_professional(professional_id):
  professional = Professional.query.filter_by(id=professional_id).first()
  professional.is_verified = True
  db.session.commit()

  flash(f'Professional {professional.user.name} has been verified.', 'success')
  return redirect(url_for('admin_dashboard.home', _anchor='professionals_table'))


@bp.route('/update_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.ADMIN)
def update_service(service_id):
  service = Service.query.filter_by(id=service_id).first()

  if request.method == 'POST':
    service.name = request.form.get('name')
    service.price = request.form.get('price')
    service.description = request.form.get('description')
    service.service_type_id = request.form.get('service_type')
    db.session.commit()
    flash(f'Service "{service.name}" has been updated.', 'success')
    return redirect(url_for('admin_dashboard.home', _anchor='services_table'))

  service_types = ServiceType.query.all()
  return render_template(
      'dashboard/admin/update_service.html',
      service=service,
      service_types=service_types,
  )


@bp.route('/delete_service/<int:service_id>')
@login_required
@role_required(UserRole.ADMIN)
def delete_service(service_id):
  service = Service.query.filter_by(id=service_id).first()
  db.session.delete(service)
  db.session.commit()

  flash(f'Service "{service.name}" has been deleted.', 'success')
  return redirect(url_for('admin_dashboard.home', _anchor='services_table'))


@bp.route('/create_service', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.ADMIN)
def create_service():
  if request.method == 'POST':
    service_name = request.form.get('name')
    service_type_id = request.form.get('service_type')
    price = request.form.get('price')
    description = request.form.get('description')
    new_service = Service(
        name=service_name,
        service_type_id=service_type_id,
        price=price,
        description=description
    )
    db.session.add(new_service)
    db.session.commit()
    flash(f'Service "{new_service.name}" has been created.', 'success')
    return redirect(url_for('admin_dashboard.home', _anchor='services_table'))

  service_types = ServiceType.query.all()
  return render_template('dashboard/admin/create_service.html', service_types=service_types)


@bp.route('/create_service_type', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.ADMIN)
def create_service_type():
  if request.method == 'POST':
    service_type_name = request.form.get('name')
    description = request.form.get('description')
    new_service_type = ServiceType(name=service_type_name, description=description)
    db.session.add(new_service_type)
    db.session.commit()
    flash(f'Service Type "{new_service_type.name}" has been created.', 'success')
    return redirect(url_for('admin_dashboard.home', _anchor='service_types_table'))

  return render_template('dashboard/admin/create_service_type.html')


@bp.route('/create_city', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.ADMIN)
def create_city():
  states = [
      ('UP', 'Uttar Pradesh'),
      ('MH', 'Maharashtra'),
      ('KA', 'Karnataka'),
      ('TN', 'Tamil Nadu'),
      ('AP', 'Andhra Pradesh'),
      ('GJ', 'Gujarat'),
      ('MP', 'Madhya Pradesh')
  ]

  if request.method == 'POST':
    city_name = request.form.get('name')
    state_code = request.form.get('state_code')
    new_city = City(name=city_name, state_code=state_code)
    db.session.add(new_city)
    db.session.commit()
    flash(f'City "{new_city.name}" has been created.', 'success')
    return redirect(url_for('admin_dashboard.home', _anchor='cities_table'))

  return render_template('dashboard/admin/create_city.html', states=states)
