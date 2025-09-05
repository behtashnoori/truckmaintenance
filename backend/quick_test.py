from app import create_app, db
from app.models.company import Company

app = create_app()
with app.app_context():
    c = Company(phone="09120000011", name="Another Company")
    db.session.add(c)
    db.session.commit()
    print("Inserted Company with id:", c.id)
