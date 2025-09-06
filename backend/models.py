from backend.app import db
from sqlalchemy import UniqueConstraint


class Company(db.Model):
    __tablename__ = "Company"
    __table_args__ = (
        UniqueConstraint("Tel", name="uq_company_tel"),
        {"schema": "dbo"},
    )

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tel = db.Column(db.String(20), nullable=False, unique=True, index=True)
    Name = db.Column(db.String(255), nullable=False)

    def to_dict(self) -> dict:
        return {"Id": self.Id, "Tel": self.Tel, "Name": self.Name}

    def __repr__(self) -> str:
        return f"<Company Id={self.Id} Tel={self.Tel!r}>"
