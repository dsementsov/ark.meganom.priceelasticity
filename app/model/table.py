from app import db
from datetime import datetime, date
import json
from sqlalchemy.orm import relationship


class UtilityTable:
    """Interface class for readability"""

    def __init__(self, **kwargs):
        members = [
            attr
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        ]
        for member in members:
            if member in kwargs.keys():
                setattr(self, member, kwargs.get(member))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class PriceData(UtilityTable, db.Model):

    __tablename__ = 'price_data'

    date = db.Column(db.DateTime, nullable=False)
    ticket_type = db.Column(db.String(255))
    count = db.Column(db.Integer)
    price = db.Column(db.Float)
    season = db.Column(db.String(255))
    day_week = db.Column(db.String(255))
    workday = db.Column(db.Integer)