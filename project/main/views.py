# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint
from flask.ext.login import login_required


################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################

@main_blueprint.route('/')
def home():
    return render_template('main/index.html')
