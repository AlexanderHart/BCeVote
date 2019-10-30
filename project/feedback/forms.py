# project/feedback/forms.py


from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from project.models import User


class FeedbackForm(Form):
    q1 = TextField('q1')
    q2 = TextField('q2')
    q3 = TextField('q3')
    q4 = TextField('q4')
    q5 = TextField('q5')
