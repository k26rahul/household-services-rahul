from typing import Optional
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
  ADMIN = 'admin'
  CUSTOMER = 'customer'
  PROFESSIONAL = 'professional'


class BookingStatus(enum.Enum):
  OPEN = 'created'  # The booking has been created but a professional is yet to be assigned.
  ASSIGNED = 'assigned'  # A professional has been assigned, but the service is not yet fulfilled.
  CLOSED = 'closed'  # The booking has been fulfilled and is now closed.


class User(db.Model, UserMixin):
  """Represents a user in the system."""
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  email: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]
  role: Mapped[UserRole] = mapped_column(Enum(UserRole))
  name: Mapped[str]
  address: Mapped[str]
  postal_code: Mapped[str]
  phone_number: Mapped[str]
  city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'))
  geo_latitude: Mapped[Optional[float]]
  geo_longitude: Mapped[Optional[float]]
  created_on: Mapped[datetime] = mapped_column(default=lambda: datetime.now())
  last_logged_in_on: Mapped[datetime] = mapped_column(default=lambda: datetime.now())
  is_blocked: Mapped[bool] = mapped_column(default=False)

  city = relationship('City', back_populates='residents')
  customer = relationship('Customer', back_populates='user', uselist=False)
  professional = relationship('Professional', back_populates='user', uselist=False)


class Customer(db.Model):
  """Represents a customer in the system."""
  __tablename__ = 'customers'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

  user = relationship('User', back_populates='customer')
  bookings = relationship('Booking', back_populates='customer')


class Professional(db.Model):
  """Represents a professional in the system."""
  __tablename__ = 'professionals'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  service_type_id: Mapped[int] = mapped_column(ForeignKey('service_types.id'))
  about_me: Mapped[str]
  is_verified: Mapped[bool] = mapped_column(default=False)
  resume_file: Mapped[Optional[str]]

  user = relationship('User', back_populates='professional')
  service_type = relationship('ServiceType', back_populates='professionals')
  bookings = relationship('Booking', back_populates='assigned_professional')


class ServiceType(db.Model):
  """Represents a type of service offered by professionals."""
  __tablename__ = 'service_types'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  name: Mapped[str]
  description: Mapped[Optional[str]]

  professionals = relationship('Professional', back_populates='service_type')
  services = relationship('Service', back_populates='service_type')


class Service(db.Model):
  """Represents a specific service offered under a service type."""
  __tablename__ = 'services'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  service_type_id: Mapped[int] = mapped_column(ForeignKey('service_types.id'))
  name: Mapped[str]
  price: Mapped[int]
  description: Mapped[Optional[str]]

  service_type = relationship('ServiceType', back_populates='services')
  bookings = relationship('Booking', back_populates='service', cascade='all, delete')


class Booking(db.Model):
  """Represents a booking made by a customer for a service."""
  __tablename__ = 'bookings'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
  service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))
  details: Mapped[Optional[str]]
  assigned_professional_id: Mapped[Optional[int]] = mapped_column(ForeignKey('professionals.id'))
  status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.OPEN)
  created_on: Mapped[datetime] = mapped_column(
      default=lambda: datetime.now())  # When the booking was created
  scheduled_on: Mapped[datetime]  # When the service is scheduled to take place
  assigned_on: Mapped[Optional[datetime]]  # When a professional is assigned to the booking
  closed_on: Mapped[Optional[datetime]]  # When the booking is fulfilled and closed
  review_stars: Mapped[Optional[int]]
  review_comments: Mapped[Optional[str]]

  customer = relationship('Customer', back_populates='bookings')
  service = relationship('Service', back_populates='bookings')
  assigned_professional = relationship('Professional', back_populates='bookings')


class City(db.Model):
  """Represents a city where users are located."""
  __tablename__ = 'cities'

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  name: Mapped[str]
  state_code: Mapped[str]

  residents = relationship('User', back_populates='city')
