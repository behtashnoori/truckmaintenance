from backend.app import db


class Company(db.Model):
    __tablename__ = "Company"
    __table_args__ = {"schema": "dbo"}  # پیش‌فرض SQL Server

    Id   = db.Column("Id",  db.Integer, primary_key=True, autoincrement=True)
    Tel  = db.Column("Tel", db.String(20),  nullable=False, unique=True)
    Name = db.Column("Name", db.String(255), nullable=False)
