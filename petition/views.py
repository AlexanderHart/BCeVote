# project/user/views.py


#################
#### imports ####
#################
from algosdk import encoding
from algosdk import transaction
from algosdk import kmd
from algosdk import algod
from algosdk import account
from algosdk import mnemonic
import json


from project.email import send_email
from project.decorators import check_confirmed
from project.token import generate_confirmation_token, confirm_token

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, \
    login_required, current_user

from project.models import User, Petition
# from project.email import send_email
from project import db, bcrypt
from .forms import LoginForm, RegisterForm, ChangePasswordForm, CreatePetitionForm

import datetime

################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)
petition_blueprint = Blueprint('petition', __name__,)


################
#### routes ####
################

@petition_blueprint.route('/createPetition', methods=['GET', 'POST'])
@login_required
@check_confirmed
def createPetition():
    form = CreatePetitionForm(request.form)
    if form.validate_on_submit():
        # create kmd and algod clients
        kcl = kmd.KMDClient("43bdd18aee3788a8dd41d39a4d4c20c4e22539ec9c4faf0c3525cd30f0e2baae", "http://127.0.0.1:7833")
        acl = algod.AlgodClient("44018d81c65b1b2fc4c33380cc9bb3cd0e6c33f8ede8bbee63638943f819b003", "http://127.0.0.1:36971")

        wallet_name = "testWallet"
        wallet_pswd = "root"

        # get the wallet ID
        wallets = kcl.list_wallets()

        wallet_id = None
        for w in wallets:
    	    if w["name"] == wallet_name:
                wallet_id = w["id"]
                break

        # if it doesn't exist, create the wallet and get its ID
        if not wallet_id:
            wallet_id = kcl.create_wallet(wallet_name, wallet_pswd)["id"]

        # get a handle for the wallet
        handle = kcl.init_wallet_handle(wallet_id, wallet_pswd)

        # generate account with account and check if it's valid
        private_key_1, address_1 = account.generate_account()

        # import generated account into the wallet
        kcl.import_key(handle, private_key_1)

        petition = Petition(
            name=form.name.data,
	    publicKey=address_1,
            yesCount=0
        )
        db.session.add(petition)
        db.session.commit()

        flash('Petition has been created!.', 'success')

    return render_template('petition/createPetition.html', form=form)

@petition_blueprint.route('/listPetitions', methods=['GET', 'POST'])
@login_required
@check_confirmed
def listPetitions():
    myPetition = Petition.query.all()
    return render_template('petition/listPetitions.html', myPetition=myPetition)
