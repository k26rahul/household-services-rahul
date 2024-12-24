import os
from dotenv import load_dotenv

load_dotenv()


class Config:
  SECRET_KEY = os.getenv('APP_SECRET_KEY', 'oJAg5QDgL7Qy3')
  SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///test.db')
  DEBUG = os.getenv('DEBUG', '1') == '1'
