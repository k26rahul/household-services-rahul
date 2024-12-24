### Users

| Attribute         | Type            | Constraints                 |
| ----------------- | --------------- | --------------------------- |
| id                | int             | Primary Key, Auto Increment |
| email             | str             | Unique                      |
| password_hash     | str             |                             |
| role              | UserRole (Enum) |                             |
| name              | str             |                             |
| address           | str             |                             |
| postal_code       | str             |                             |
| phone_number      | str             |                             |
| city_id           | int             | Foreign Key (cities.id)     |
| geo_latitude      | Optional[float] |                             |
| geo_longitude     | Optional[float] |                             |
| created_on        | datetime        | Default: datetime.now()     |
| last_logged_in_on | datetime        | Default: datetime.now()     |
| is_blocked        | bool            | Default: False              |

---

### Customers

| Attribute | Type | Constraints                 |
| --------- | ---- | --------------------------- |
| id        | int  | Primary Key, Auto Increment |
| user_id   | int  | Foreign Key (users.id)      |

---

### Professionals

| Attribute       | Type          | Constraints                    |
| --------------- | ------------- | ------------------------------ |
| id              | int           | Primary Key, Auto Increment    |
| user_id         | int           | Foreign Key (users.id)         |
| service_type_id | int           | Foreign Key (service_types.id) |
| about_me        | str           |                                |
| is_verified     | bool          | Default: False                 |
| resume_file     | Optional[str] |                                |

---

### ServiceTypes

| Attribute   | Type          | Constraints                 |
| ----------- | ------------- | --------------------------- |
| id          | int           | Primary Key, Auto Increment |
| name        | str           |                             |
| description | Optional[str] |                             |

---

### Services

| Attribute       | Type          | Constraints                    |
| --------------- | ------------- | ------------------------------ |
| id              | int           | Primary Key, Auto Increment    |
| service_type_id | int           | Foreign Key (service_types.id) |
| name            | str           |                                |
| price           | int           |                                |
| description     | Optional[str] |                                |

---

### Bookings

| Attribute                | Type                 | Constraints                    |
| ------------------------ | -------------------- | ------------------------------ |
| id                       | int                  | Primary Key, Auto Increment    |
| customer_id              | int                  | Foreign Key (customers.id)     |
| service_id               | int                  | Foreign Key (services.id)      |
| details                  | Optional[str]        |                                |
| assigned_professional_id | Optional[int]        | Foreign Key (professionals.id) |
| status                   | BookingStatus (Enum) | Default: BookingStatus.OPEN    |
| created_on               | datetime             | Default: datetime.now()        |
| scheduled_on             | datetime             |                                |
| assigned_on              | Optional[datetime]   |                                |
| closed_on                | Optional[datetime]   |                                |
| review_stars             | Optional[int]        |                                |
| review_comments          | Optional[str]        |                                |

---

### Cities

| Attribute  | Type | Constraints                 |
| ---------- | ---- | --------------------------- |
| id         | int  | Primary Key, Auto Increment |
| name       | str  |                             |
| state_code | str  |                             |
