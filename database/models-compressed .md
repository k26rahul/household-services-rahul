User: id (int, PK, Auto Increment), email (str, Unique), password_hash (str), role (UserRole Enum), name (str), address (str), postal_code (str), phone_number (str), city_id (int, FK City.id), geo_latitude (Optional[float]), geo_longitude (Optional[float]), created_on (datetime, Default: now), last_logged_in_on (datetime, Default: now), is_blocked (bool, Default: False)

Customer: id (int, PK, Auto Increment), user_id (int, FK User.id)

Professional: id (int, PK, Auto Increment), user_id (int, FK User.id), service_type_id (int, FK ServiceType.id), about_me (str), is_verified (bool, Default: False), resume_file (Optional[str])

ServiceType: id (int, PK, Auto Increment), name (str), description (Optional[str])

Service: id (int, PK, Auto Increment), service_type_id (int, FK ServiceType.id), name (str), price (int), description (Optional[str])

Booking: id (int, PK, Auto Increment), customer_id (int, FK Customer.id), service_id (int, FK Service.id), details (Optional[str]), assigned_professional_id (Optional[int], FK Professional.id), status (BookingStatus Enum, Default: OPEN), created_on (datetime, Default: now), scheduled_on (datetime), assigned_on (Optional[datetime]), closed_on (Optional[datetime]), review_stars (Optional[int]), review_comments (Optional[str])

City: id (int, PK, Auto Increment), name (str), state_code (str)
