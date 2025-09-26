from ..app import db
from sqlalchemy import UniqueConstraint, Table, Column, Integer, ForeignKey

# Association Table for Company and Category
company_category_association = Table('company_category', db.Model.metadata,
    Column('company_id', Integer, ForeignKey('company.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id'), primary_key=True)
)

class Company(db.Model):
    __tablename__ = "company"
    __table_args__ = (
        UniqueConstraint("phone_mobile", name="uq_company_phone_mobile"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone_mobile = db.Column(db.String(20), nullable=False)
    phone_landline = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Many-to-Many relationship with Category
    categories = db.relationship('Category', secondary=company_category_association, back_populates='companies')

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationship back to Company
    companies = db.relationship('Company', secondary=company_category_association, back_populates='categories')
