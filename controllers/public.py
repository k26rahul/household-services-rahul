from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from database.models import *
from datetime import datetime
import os

bp = Blueprint('public', __name__)


@bp.route('/')
def index():
  if current_user.is_authenticated:
    role_routes = {
        UserRole.ADMIN: 'admin_dashboard.home',
        UserRole.CUSTOMER: 'customer_dashboard.home',
        UserRole.PROFESSIONAL: 'professional_dashboard.home'
    }
    flash('You have been redirected to your dashboard', 'info')
    return redirect(url_for(role_routes.get(current_user.role)))

  cities = City.query.all()
  service_types = ServiceType.query.all()
  return render_template('public/index.html',
                         cities=cities, service_types=service_types)


@bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    flash('Already logged in', 'info')
    return redirect(url_for('public.index'))

  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
      login_user(user)
      flash('Login successful', 'success')
      return redirect(url_for('public.index'))
    else:
      flash('Invalid email or password', 'danger')
      return render_template('public/login.html', email=email)

  return render_template('public/login.html')


@bp.route('/logout')
def logout():
  logout_user()
  flash('Logged out successfully', 'success')
  return redirect(url_for('public.login'))


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
  if current_user.is_authenticated:
    flash('You are already logged in', 'info')
    return redirect(url_for('public.index'))

  def render_signup_form():
    cities = City.query.all()
    return render_template('public/signup.html', cities=cities)

  if request.method == 'POST':
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    city_id = request.form.get('city_id')
    address = request.form.get('address')
    postal_code = request.form.get('postal_code')

    # check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
      flash('Email is already taken', 'danger')
      return render_signup_form()

    password_hash = generate_password_hash(password)
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        phone_number=phone_number,
        address=address,
        postal_code=postal_code,
        city_id=city_id,
        role=UserRole.CUSTOMER
    )

    db.session.add(user)
    db.session.flush()

    customer = Customer(user_id=user.id)
    db.session.add(customer)
    db.session.commit()

    login_user(user)
    flash('Signup successful. You are now logged in.', 'success')
    return redirect(url_for('public.index'))

  return render_signup_form()


@bp.route('/signup-as-professional', methods=['GET', 'POST'])
def signup_professional():
  if current_user.is_authenticated:
    flash('You are already logged in', 'info')
    return redirect(url_for('public.index'))

  def render_signup_form():
    cities = City.query.all()
    service_types = ServiceType.query.all()
    return render_template('public/signup_professional.html',
                           cities=cities, service_types=service_types)

  if request.method == 'POST':
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

    def allowed_file(filename):
      if '.' not in filename:
        return False
      extension = filename.rsplit('.', 1)[1].lower()
      return extension in ALLOWED_EXTENSIONS

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    city_id = request.form.get('city_id')
    address = request.form.get('address')
    postal_code = request.form.get('postal_code')
    service_type_id = request.form.get('service_type_id')
    about_me = request.form.get('about_me')

    # check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
      flash('Email is already taken', 'danger')
      return render_signup_form()

    # handle resume file upload
    resume = request.files.get('resume')
    if resume and allowed_file(resume.filename):
      file_ext = resume.filename.rsplit('.', 1)[1].lower()
      filename = f"{datetime.now().strftime(r'%Y%m%d%H%M%S')}.{file_ext}"
      filepath = os.path.join(UPLOAD_FOLDER, filename)
      resume.save(filepath)
    else:
      flash('Invalid resume file', 'danger')
      return render_signup_form()

    password_hash = generate_password_hash(password)
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        phone_number=phone_number,
        address=address,
        postal_code=postal_code,
        city_id=city_id,
        role=UserRole.PROFESSIONAL
    )

    db.session.add(user)
    db.session.flush()

    professional = Professional(
        user_id=user.id,
        service_type_id=service_type_id,
        about_me=about_me,
        resume_file=filename
    )
    db.session.add(professional)
    db.session.commit()

    login_user(user)
    flash('Signup successful. You are now logged in as a professional.', 'success')
    return redirect(url_for('public.index'))

  return render_signup_form()
