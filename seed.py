import random
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.category import IncidentCategory
from app.models.incident import Incident
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # If you want to fully reset during seeding, uncomment:
    db.drop_all()
    db.create_all()

    # Create 10 categories
    categories = [
        IncidentCategory(name=f"Category {i}", description=f"Description for category {i}")
        for i in range(1, 11)
    ]
    db.session.add_all(categories)

    # Create 10 users (user1=admin with your Gmail address)
    users = []
    for i in range(1, 11):
        if i == 1:
            role = 'admin'
            email = "alecashmore50@gmail.com"
        else:
            role = 'regular'
            email = f"user{i}@example.com"

        u = User(username=f"user{i}", email=email, role=role)
        # Hash the seed password with Bcrypt
        u.password_hash = bcrypt.generate_password_hash("Password123").decode('utf-8')
        users.append(u)

    db.session.add_all(users)
    db.session.commit()

    # Pick 3-4 random days in the last 30 days
    num_days = random.randint(3, 4)
    days_offsets = sorted(random.sample(range(0, 30), num_days))
    day_datetimes = [datetime.utcnow() - timedelta(days=offset) for offset in days_offsets]

    # Create 10 incidents, distributed across these days
    statuses = ['Open', 'In Progress', 'Closed']
    incidents = []
    for i in range(1, 11):
        # Assign each incident to a random day from the chosen days
        random_time = random.choice(day_datetimes)
        # Add some random hours/minutes for variety
        random_time = random_time.replace(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)
        inc = Incident(
            title=f"Incident {i}",
            description=f"This is the description for incident {i}.",
            status=random.choice(statuses),
            user_id=random.choice(users).id,
            category_id=random.choice(categories).id,
            timestamp=random_time
        )
        incidents.append(inc)

    db.session.add_all(incidents)
    db.session.commit()

    print("✅ Database seeded with random incidents.")
