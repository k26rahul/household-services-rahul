import os
import json5
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from .models import *

load_dotenv()

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
LOREM = "Lorem ipsum dolor sit amet."


def create_admin():
  hashed_password = generate_password_hash(ADMIN_PASSWORD)
  db.session.add(User(
      email="rahul@gmail.com",
      password_hash=hashed_password,
      name="Rahul",
      role=UserRole.ADMIN,
      address='NA',
      postal_code='NA',
      phone_number='NA',
      city_id=1
  ))
  db.session.commit()


def create_customers():
  with open('database/sample-data/customers.jsonc') as f:
    data = json5.load(f)
    for customer in data:
      hashed_password = generate_password_hash('12345')
      user = User(
          email=customer["email"],
          password_hash=hashed_password,
          name=customer["name"],
          role=UserRole.CUSTOMER,
          address=customer["address"],
          postal_code=customer["postal_code"],
          phone_number=customer["phone_number"],
          city_id=customer["city_id"]
      )
      db.session.add(user)
      db.session.add(Customer(user=user))
  db.session.commit()


def create_professionals():
  with open('database/sample-data/professionals.jsonc') as f:
    data = json5.load(f)
    for professional in data:
      hashed_password = generate_password_hash('12345')
      user = User(
          email=professional["email"],
          password_hash=hashed_password,
          name=professional["name"],
          role=UserRole.PROFESSIONAL,
          address=professional["address"],
          postal_code=professional["postal_code"],
          phone_number=professional["phone_number"],
          city_id=professional["city_id"]
      )
      db.session.add(user)
      db.session.add(Professional(
          user=user,
          service_type_id=professional["service_type_id"],
          about_me=professional["about_me"],
          is_verified=professional["is_verified"]
      ))
  db.session.commit()


def create_cities():
  with open('database/sample-data/cities.jsonc') as f:
    data = json5.load(f)
    for state_code, cities in data.items():
      for city_name in cities:
        city = City(name=city_name, state_code=state_code)
        db.session.add(city)
  db.session.commit()


def create_service_types_and_services():
  with open('database/sample-data/services.jsonc') as f:
    data = json5.load(f)
    for service_type_name, services in data.items():
      service_type = ServiceType(name=service_type_name, description=LOREM)
      db.session.add(service_type)
      db.session.flush()  # To get the id of service_type after insert
      for service in services:
        db.session.add(Service(
            name=service["name"],
            price=service["price"],
            service_type_id=service_type.id,
            description=LOREM
        ))
  db.session.commit()


def create_bookings():
  with open('database/sample-data/bookings.jsonc') as f:
    data = json5.load(f)
    for booking in data:
      if booking["status"] == "CLOSED":
        booking['created_on'] = '2024-11-12T14:00:00'
        booking['assigned_on'] = '2024-11-14T14:00:00'

      elif booking['status'] == 'ASSIGNED':
        booking['created_on'] = '2024-11-22T14:00:00'
        booking['assigned_on'] = '2024-11-24T14:00:00'

      else:
        booking['created_on'] = (datetime.now() - timedelta(days=0)).isoformat(timespec='seconds')

      db.session.add(
          Booking(
              customer_id=booking["customer_id"],
              service_id=booking["service_id"],
              details=booking["details"],
              assigned_professional_id=booking.get("assigned_professional_id"),
              status=BookingStatus[booking["status"]],
              scheduled_on=datetime.fromisoformat(booking["scheduled_on"]),
              created_on=(
                  datetime.fromisoformat(booking["created_on"])
                  if booking.get("created_on")
                  else None
              ),
              assigned_on=(
                  datetime.fromisoformat(booking["assigned_on"])
                  if booking.get("assigned_on")
                  else None
              ),
              closed_on=(
                  datetime.fromisoformat(booking["scheduled_on"]) + timedelta(hours=2)
                  if booking["status"] == "CLOSED"
                  else None
              ),
              review_stars=booking.get("review_stars"),
              review_comments=booking.get("review_comments"),
          )
      )

  db.session.commit()


def clear_all_tables():
  """ clear all records from the database tables. """
  db.session.query(User).delete()
  db.session.query(Customer).delete()
  db.session.query(Professional).delete()
  db.session.query(ServiceType).delete()
  db.session.query(Service).delete()
  db.session.query(Booking).delete()
  db.session.query(City).delete()
  db.session.commit()


def insert_sample_data():
  clear_all_tables()
  create_admin()
  create_customers()
  create_professionals()
  create_cities()
  create_service_types_and_services()
  create_bookings()
