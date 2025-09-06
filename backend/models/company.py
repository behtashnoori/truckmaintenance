from ..app import db


class Company(db.Model):
    __tablename__ = "Company"
    __table_args__ = {"schema": "dbo"}

    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Tel = db.Column(db.String(50), nullable=False)
    Name = db.Column(db.String(100), nullable=False)
