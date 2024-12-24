from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(roles):
  if not isinstance(roles, list):
    roles = [roles]

  def decorator(func):
    # use the functools.wraps decorator to
    # retain the original function's name and metadata when creating the wrapper
    @wraps(func)
    def wrapped_function(*args, **kwargs):
      if current_user.role not in roles:
        abort(403)
      return func(*args, **kwargs)
    return wrapped_function
  return decorator
