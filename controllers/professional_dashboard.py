from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from database.models import *

bp = Blueprint('professional_dashboard', __name__, url_prefix='/professional')


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
def home():
  if current_user.role.name != 'PROFESSIONAL':
    abort(403)

  professional = current_user.professional

  open_bookings = (
      Booking.query
      .filter(Booking.status == BookingStatus.OPEN)
      .join(Service, Booking.service_id == Service.id)
      .join(Customer, Booking.customer_id == Customer.id)
      .join(User, Customer.user_id == User.id)
      .filter(
          Service.service_type_id == professional.service_type_id,  # match service type
          User.city_id == current_user.city_id  # match city
      )
      .all()
  )

  today = datetime.now().date()
  today_bookings = (
      Booking.query
      .filter(
          Booking.assigned_professional_id == professional.id,  # match professional
          Booking.status == BookingStatus.ASSIGNED,  # match status
          func.date(Booking.scheduled_on) == today  # extract and compare date
      )
      .all()
  )

  upcoming_bookings = Booking.query.filter_by(
      assigned_professional_id=professional.id,
      status=BookingStatus.ASSIGNED
  ).filter(func.date(Booking.scheduled_on) != today).all()

  closed_bookings = Booking.query.filter_by(
      assigned_professional_id=professional.id,
      status=BookingStatus.CLOSED
  ).all()

  return render_template(
      'dashboard/professional/home.html',
      open_bookings=open_bookings,
      today_bookings=today_bookings,
      upcoming_bookings=upcoming_bookings,
      closed_bookings=closed_bookings
  )


@bp.route('/search')
@login_required
def search():
  if current_user.role.name != 'PROFESSIONAL':
    abort(403)

  cities = City.query.all()
  service_types = ServiceType.query.all()
  services = Service.query.filter_by(service_type_id=current_user.professional.service_type_id).all()

  return render_template('dashboard/professional/search.html',
                         cities=cities,
                         service_types=service_types,
                         services=services)


@bp.route('/search-results')
@login_required
def search_results():
  if current_user.role.name != 'PROFESSIONAL':
    abort(403)

  booking_status = request.args.get('booking_status')
  customer_name = request.args.get('customer_name', '').strip()
  customer_address = request.args.get('customer_address', '').strip()
  customer_postal_code = request.args.get('customer_postal_code', '').strip()
  service_id = request.args.get('service_id')

  query = Booking.query.join(Customer).join(User)

  if booking_status in ['assigned', 'closed']:
    query = query.filter(
        Booking.assigned_professional_id == current_user.professional.id)

  # filter by booking status
  if booking_status == 'all':
    query = query.filter(
        (Booking.assigned_professional_id == current_user.professional.id) |
        ((Booking.status == BookingStatus.OPEN) &
         Customer.user.has(city_id=current_user.professional.user.city_id) &
         Booking.service.has(service_type_id=current_user.professional.service_type_id))
    )
  elif booking_status == 'open':
    query = query.filter((Booking.status == BookingStatus.OPEN) &
                         Customer.user.has(city_id=current_user.professional.user.city_id) &
                         Booking.service.has(service_type_id=current_user.professional.service_type_id))
  elif booking_status == 'assigned':
    query = query.filter(Booking.status == BookingStatus.ASSIGNED)
  elif booking_status == 'closed':
    query = query.filter(Booking.status == BookingStatus.CLOSED)

  # filter by customer information
  if customer_name:
    query = query.filter(User.name.ilike(f"%{customer_name}%"))
  if customer_address:
    query = query.filter(User.address.ilike(f"%{customer_address}%"))
  if customer_postal_code:
    query = query.filter(User.postal_code.ilike(f"%{customer_postal_code}%"))

  # filter by service
  if service_id:
    query = query.filter(Booking.service_id == service_id)

  results = query.all()

  return render_template('dashboard/professional/search_results.html',
                         bookings=results, booking_status=booking_status)


@bp.route('/summary')
@login_required
def summary():
  if current_user.role.name != 'PROFESSIONAL':
    abort(403)

  total_bookings = Booking.query.filter_by(assigned_professional_id=current_user.professional.id).count()

  # Count ratings by 1-5 stars with percentages
  ratings_count = db.session.query(
      Booking.review_stars,
      func.count(Booking.id)
  ).filter(
      Booking.assigned_professional_id == current_user.professional.id,
      Booking.review_stars.isnot(None)
  ).group_by(Booking.review_stars).all()

  ratings_dict = [
      {
          "stars": star,
          "count": count,
          "percentage": (count / total_bookings * 100) if total_bookings else 0
      }
      for star, count in ratings_count
  ]

  # Ensure all 1-5 stars are present
  for star in range(1, 6):
    if not any(r["stars"] == star for r in ratings_dict):
      ratings_dict.append({"stars": star, "count": 0, "percentage": 0})
  ratings_dict.sort(key=lambda r: r["stars"])

  # Count bookings by status with percentages
  booking_status_counts = db.session.query(
      Booking.status,
      func.count(Booking.id)
  ).filter(
      Booking.assigned_professional_id == current_user.professional.id
  ).group_by(Booking.status).all()

  status_dict = [
      {
          "status": status.name.title(),
          "count": count,
          "percentage": (count / total_bookings * 100) if total_bookings else 0
      }
      for status, count in booking_status_counts
  ]

  # Ensure all statuses are present
  for status in BookingStatus:
    if not any(s["status"] == status.name.title() for s in status_dict):
      status_dict.append({"status": status.name.title(), "count": 0, "percentage": 0})
  status_dict.sort(key=lambda s: s["status"])

  return render_template(
      'dashboard/professional/summary.html',
      ratings_dict=ratings_dict,
      status_dict=status_dict,
      total_bookings=total_bookings
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


@bp.route('/accept-booking/<int:booking_id>')
@login_required
def accept_booking(booking_id):
  if current_user.role.name != 'PROFESSIONAL':
    abort(403)

  booking = Booking.query.filter_by(id=booking_id).first()
  booking.status = BookingStatus.ASSIGNED
  booking.assigned_professional_id = current_user.professional.id
  booking.assigned_on = datetime.now()
  db.session.commit()

  flash('Booking accepted successfully.', 'success')
  return redirect(url_for('professional_dashboard.home', _anchor='open_bookings_table'))


@bp.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
  if current_user.role.name != 'PROFESSIONAL':
    abort(403)

  booking = Booking.query.filter_by(id=booking_id).first()
  booking.status = BookingStatus.OPEN
  booking.assigned_professional_id = None
  booking.assigned_on = None
  db.session.commit()

  flash('Booking canceled successfully.', 'success')
  return redirect(url_for('professional_dashboard.home', _anchor='open_bookings_table'))
