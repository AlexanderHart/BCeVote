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
import base64
from project import params


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
from .forms import LoginForm, RegisterForm, ChangePasswordForm, CreatePetitionForm, ListPetitionForm

import datetime

################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)
petition_blueprint = Blueprint('petition', __name__,)

kcl = kmd.KMDClient(params.kmd_token, params.kmd_address)
acl = algod.AlgodClient(params.algod_token, params.algod_address)

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


def DoubleVoteChecker(curUser, txArray):
    for i in range(0,len(txArray)):
        currentTx = txArray.get("transactions")[i]
        # read noteb64 field of first transaction
        noteb64 = currentTx.get("noteb64")
        # Decode to bytes
        note = base64.b64decode(noteb64)
        note2 = str(note)[2:len(str(note))-1]
        if note2 == str(curUser):
            return True
            break
    return False


@petition_blueprint.route('/listPetitions', methods=['GET', 'POST'])
@login_required
@check_confirmed
def listPetitions():
    form = ListPetitionForm(request.form)
    if form.validate_on_submit():
        if request.method == 'POST':
            # This would be a good place

            petPK = str(request.form['castVote'])
	    # to check if the current email has been used
	    # for petition before.
            txs = acl.transactions_by_address(petPK, first=3000, last=3100)
            if DoubleVoteChecker(current_user.email, txs):
                flash(str(current_user.email) + " has already signed this petition.")
            else:
                flash("This user is allowed to sign this peition.")

	    # Given the petitionPK
	    # check to see if any transactions exist,
    	    # if they do, then check to see if any specific
	    # transaction notefield has the current email hash.
	    # Else: Successfully sign petition with email hash.
            flash(petPK)
            flash(current_user.email)

    myPetition = Petition.query.all()
    return render_template('petition/listPetitions.html', form=form, myPetition=myPetition)
