from flask import Flask
from flask_login import LoginManager
from database.models import db
from .config import Config

login_manager = LoginManager()


def create_app():
  app = Flask(
      __name__,
      template_folder="../templates",
      static_folder="../static"
  )

  # Load configurations
  app.config.from_object(Config)

  # Initialize extensions
  db.init_app(app)
  login_manager.init_app(app)

  # Register blueprints
  register_blueprints(app)

  with app.app_context():
    db.create_all()
    insert_sample_data_if_needed()

  return app


def register_blueprints(app: Flask):
  from controllers import (public_blueprint, admin_dashboard_blueprint,
                           customer_dashboard_blueprint, professional_dashboard_blueprint,
                           profile_blueprint)
  app.register_blueprint(public_blueprint)
  app.register_blueprint(admin_dashboard_blueprint)
  app.register_blueprint(customer_dashboard_blueprint)
  app.register_blueprint(professional_dashboard_blueprint)
  app.register_blueprint(profile_blueprint)


def insert_sample_data_if_needed():
  from database.insert_sample_data import insert_sample_data
  insert_sample_data()


@login_manager.user_loader
def load_user(user_id):
  from database.models import User
  return User.query.filter_by(id=user_id).first()
