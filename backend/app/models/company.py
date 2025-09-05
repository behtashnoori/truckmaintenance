from .. import db


class Company(db.Model):
    __tablename__ = "Company"  # در SQL Server داخل schema dbo می‌رود
    id = db.Column("Id", db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column("Tel", db.String(20), nullable=False, index=True)
    name = db.Column("Name", db.String(255), nullable=False)

    def to_dict(self):
        return {"id": self.id, "phone": self.phone, "name": self.name}
