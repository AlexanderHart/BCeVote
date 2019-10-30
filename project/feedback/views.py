# project/feedback/views.py

from .forms import FeedbackForm
from project.token import generate_confirmation_token, confirm_token
from project.decorators import check_confirmed
from project.models import User, Petition
from project.email import send_email


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
        petition = Petition(
            name="form.name.data,",
	        publicKey="address_1",
            masterAccount = "",
            yesCount=0,
            startDate="form.startDate.data",
            endDate="orm.endDate.data"
        )
        db.session.add(petition)
        db.session.commit()
        flash('Feedback has been created!.', 'success')

    return render_template('feedback/feedback.html', form=form)
