# project/models.py


import datetime

from project import db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, email, password, confirmed, paid=False, admin=False, confirmed_on=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)

class Petition(db.Model):

    __tablename__ = "petitions"

    publicKey = db.Column(db.String)
    masterAccount = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    uid = db.Column(db.Integer, primary_key=True)
    yesCount = db.Column(db.Integer)
    startDate = db.Column(db.Date, nullable=True)
    endDate = db.Column(db.Date, nullable=True)

    def __init__(self, name, publicKey, masterAccount, yesCount, startDate=None, endDate=None):
        self.name = name
        self.publicKey = publicKey
        self.masterAccount = masterAccount
        self.yesCount = yesCount
        self.startDate = startDate
        self.endDate = endDate

class Feedback(db.Model):

    __tablename__ = "feedback"

    q1 = db.Column(db.String, nullable=True)
    q2 = db.Column(db.String, nullable=True)
    q3 = db.Column(db.String, nullable=True)
    q4 = db.Column(db.String, nullable=True)
    q5 = db.Column(db.String, nullable=True)

    def __init__(self, q1, q2, q3, q4, q5):
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4
        self.q5 = q5
