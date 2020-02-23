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

class Config(UtilityTable, db.Model):

    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    config_name = db.Column(db.String(255))
    config_value = db.Column(db.String(255))