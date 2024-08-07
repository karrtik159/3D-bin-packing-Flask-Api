from . import db

class TBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    openTop = db.Column(db.String(100), nullable=False)
    coner = db.Column(db.Integer, nullable=False)

class TItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whd = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    updown = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    loadbear = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Integer, nullable=False)
