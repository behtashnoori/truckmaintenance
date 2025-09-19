from ..app import db


class Company(db.Model):
    __tablename__ = "Company"
    __table_args__ = {"schema": "dbo"}

    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Tel = db.Column(db.String(50), nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    Type_Of_Service = db.Column(db.String(255), nullable=True)
    Radius_Of_Activity = db.Column(db.Integer, nullable=True)
    Working_Hours = db.Column(db.String(100), nullable=True)
    Vehicle_Type = db.Column(db.String(255), nullable=True)
    Date = db.Column(db.DateTime, nullable=True)

    def update_details(
        self,
        *,
        type_of_service=None,
        radius_of_activity=None,
        working_hours=None,
        vehicle_type=None,
        date_value=None,
    ):
        if type_of_service is not None:
            self.Type_Of_Service = type_of_service
        if radius_of_activity is not None:
            self.Radius_Of_Activity = radius_of_activity
        if working_hours is not None:
            self.Working_Hours = working_hours
        if vehicle_type is not None:
            self.Vehicle_Type = vehicle_type
        if date_value is not None:
            self.Date = date_value
