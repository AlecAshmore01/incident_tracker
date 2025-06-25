import random
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.category import IncidentCategory
from app.models.incident import Incident

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

    # Create 10 incidents
    statuses = ['Open', 'In Progress', 'Closed']
    incidents = []
    for i in range(1, 11):
        inc = Incident(
            title=f"Incident {i}",
            description=f"This is the description for incident {i}.",
            status=random.choice(statuses),
            user_id=random.choice(users).id,
            category_id=random.choice(categories).id
        )
        incidents.append(inc)

    db.session.add_all(incidents)
    db.session.commit()

    print("✅ Database seeded with updated admin email.")
