from database.db import get_db
from werkzeug.security import generate_password_hash


name = "Disaster Authority"
email = "authority@disaster.local"
phone = "9999999999"
password = "Authority@123"
role = "authority"


db = get_db()

# Check if authority already exists
existing_user = db.execute(
    "SELECT id FROM users WHERE email = ?",
    (email,)
).fetchone()


if existing_user:

    print("Authority account already exists.")

else:

    password_hash = generate_password_hash(password)

    db.execute("""
        INSERT INTO users (
            name,
            email,
            phone,
            password,
            role
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        email,
        phone,
        password_hash,
        role
    ))

    db.commit()

    print("Authority account created successfully!")


db.close()