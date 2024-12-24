from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from database.models import *
from collections import defaultdict

bp = Blueprint('customer_dashboard', __name__, url_prefix='/customer')


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


def is_professional_available(service_type_id: int, city_id: int) -> bool:
  professional = db.session.query(Professional).join(User).filter(
      Professional.service_type_id == service_type_id,
      User.city_id == city_id
  ).first()

  return professional is not None


@bp.route('/dashboard')
@login_required
def home():
  if current_user.role.name != 'CUSTOMER':
    abort(403)

  customer = current_user.customer

  # fetch all service types and services
  service_types = ServiceType.query.options(db.joinedload(ServiceType.services)).all()

  # fetch all bookings for the customer
  open_bookings = Booking.query.filter_by(
      customer_id=customer.id,
      status=BookingStatus.OPEN
  ).all()

  assigned_bookings = Booking.query.filter_by(
      customer_id=customer.id,
      status=BookingStatus.ASSIGNED
  ).all()

  closed_bookings = Booking.query.filter_by(
      customer_id=customer.id,
      status=BookingStatus.CLOSED
  ).all()

  return render_template(
      'dashboard/customer/home.html',
      service_types=service_types,
      open_bookings=open_bookings,
      assigned_bookings=assigned_bookings,
      closed_bookings=closed_bookings,
      is_professional_available=is_professional_available
  )


@bp.route('/search')
@login_required
def search():
  if current_user.role.name != 'CUSTOMER':
    abort(403)
  cities = City.query.all()
  return render_template('dashboard/customer/search.html', cities=cities)


@bp.route('/search-results')
@login_required
def search_results():
  if current_user.role.name != 'CUSTOMER':
    abort(403)

  # Query parameters
  name = request.args.get('name', '').strip()
  description = request.args.get('description', '').strip()
  price = request.args.get('price')
  postal_code = request.args.get('postal_code')

  # Pin code filter for ServiceTypes
  service_types_query = ServiceType.query
  if postal_code:
    service_types_query = service_types_query.join(Professional).join(User).filter(
        User.role == UserRole.PROFESSIONAL,
        User.city_id == current_user.city_id,
        User.postal_code.ilike(f"%{postal_code}%")
    ).distinct()

  service_types = service_types_query.all()

  # Fetch services of filtered service types
  services_query = Service.query.filter(Service.service_type_id.in_([st.id for st in service_types]))

  # Apply other filters
  if name:
    services_query = services_query.filter(Service.name.ilike(f"%{name}%"))
  if description:
    services_query = services_query.filter(Service.description.ilike(f"%{description}%"))
  if price:
    services_query = services_query.filter(Service.price <= price)

  services = services_query.all()

  # Group services by service type name
  services_by_type = defaultdict(list)
  for service in services:
    services_by_type[service.service_type.name].append(service)

  # Pass `services_by_type` to the template
  return render_template(
      'dashboard/customer/search_results.html',
      services_by_type=services_by_type,
      postal_code=postal_code,
      is_professional_available=is_professional_available
  )


@bp.route('/summary')
@login_required
def summary():
  if current_user.role.name != 'CUSTOMER':
    abort(403)

  total_spent = (
      db.session.query(db.func.sum(Service.price))
      .join(Booking, Booking.service_id == Service.id)
      .filter(Booking.customer_id == current_user.customer.id)
      .filter(Booking.status == BookingStatus.CLOSED)
      .scalar() or 0
  )

  booking_status_counts = (
      db.session.query(Booking.status, db.func.count(Booking.id))
      .filter(Booking.customer_id == current_user.customer.id)
      .group_by(Booking.status)
      .all()
  )
  total_bookings = sum(count for _, count in booking_status_counts)
  status_dict = [
      {
          'status': status.name,
          'count': count,
          'percentage': (count / total_bookings) * 100 if total_bookings else 0,
      }
      for status, count in booking_status_counts
  ]

  summary_data = {
      'total_spent': total_spent,
      'status_dict': status_dict,
  }

  return render_template('dashboard/customer/summary.html', summary=summary_data)


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


@bp.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book_service(service_id):
  if current_user.role.name != 'CUSTOMER':
    abort(403)

  service = Service.query.filter_by(id=service_id).first()
  customer = current_user.customer

  if request.method == 'POST':
    details = request.form.get('details', '').strip()
    scheduled_on = request.form.get('scheduled_on')
    scheduled_on = datetime.strptime(scheduled_on, '%Y-%m-%dT%H:%M')  # parse datetime input

    booking = Booking(
        customer_id=customer.id,
        service_id=service.id,
        status=BookingStatus.OPEN,
        created_on=datetime.now(),
        scheduled_on=scheduled_on,
        details=details
    )
    db.session.add(booking)
    db.session.commit()
    flash('Service booked successfully!', 'success')
    return redirect(url_for('customer_dashboard.home', _anchor='open_bookings_table'))

  return render_template(
      'dashboard/customer/book_service.html',
      service=service,
      is_professional_available=is_professional_available
  )


@bp.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
  if current_user.role.name != 'CUSTOMER':
    abort(403)

  booking = Booking.query.filter_by(id=booking_id).first()
  if booking.customer_id != current_user.customer.id:
    abort(403)

  db.session.delete(booking)
  db.session.commit()
  flash('Booking canceled successfully.', 'success')
  return redirect(url_for('customer_dashboard.home', _anchor='open_bookings_table'))


@bp.route('/close-booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def close_booking(booking_id):
  if current_user.role.name != 'CUSTOMER':
    abort(403)

  booking = Booking.query.filter_by(id=booking_id).first()
  if not booking or booking.customer_id != current_user.customer.id:
    abort(403)

  if request.method == 'POST':
    # Capture rating and comments
    rating = request.form.get('rating')
    comments = request.form.get('comments')

    if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
      flash('Please provide a valid rating between 1 and 5.', 'danger')
      return redirect(request.url)

    booking.review_stars = int(rating)
    booking.review_comments = comments
    booking.status = BookingStatus.CLOSED
    booking.closed_on = datetime.now()
    db.session.commit()
    flash('Booking closed successfully.', 'success')
    return redirect(url_for('customer_dashboard.home', _anchor='assigned_bookings_table'))

  return render_template('dashboard/customer/close_booking.html', booking=booking)
