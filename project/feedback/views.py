# project/feedback/views.py

from .forms import FeedbackForm
from project.token import generate_confirmation_token, confirm_token
from project.decorators import check_confirmed
from project.models import User, Petition, Feedback
from project.email import send_email
from project import db


from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, \
    login_required, current_user



user_blueprint      = Blueprint('user', __name__,)
petition_blueprint  = Blueprint('petition', __name__,)
feedback_blueprint  = Blueprint('feedback', __name__,)

##################################################
#                                                #
# Return type:                                   #
# (render_template)                              #
#                                                #
# Parameters:                                    #
# None                                           #
#                                                #
#                                                #
##################################################
@feedback_blueprint.route('/feedback', methods=['GET', 'POST'])
@login_required
@check_confirmed
def giveFeedback():
    form = FeedbackForm(request.form)
    if form.validate_on_submit():
        feedback = Feedback(
            q1=form.q1.data,
            q2=form.q2.data,
            q3=form.q3.data,
            q4=form.q4.data,
            q5=form.q5.data
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback has been created!.', 'success')

    return render_template('feedback/feedback.html', form=form)
