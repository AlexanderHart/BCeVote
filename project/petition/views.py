# project/petition/views.py

from .forms import LoginForm, RegisterForm, ChangePasswordForm, CreatePetitionForm, ListPetitionForm
from project.token import generate_confirmation_token, confirm_token
from project.decorators import check_confirmed
from project.models import User, Petition
from project.email import send_email
from project import db, bcrypt
from algosdk import transaction
from algosdk import mnemonic
from algosdk import encoding
from algosdk import account
from algosdk import algod
from algosdk import kmd
import subprocess
import datetime
import hashlib
import json
import base64
from project import params
import time

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, \
    login_required, current_user



user_blueprint      = Blueprint('user', __name__,)
petition_blueprint  = Blueprint('petition', __name__,)

kcl = kmd.KMDClient(params.kmd_token, params.kmd_address)
acl = algod.AlgodClient(params.algod_token, params.algod_address)


##################################################
#                                                #
# Return type:                                   #
# (render_template)                              #
#                                                #
# Parameters:                                    #
# None                                           #
#                                                #
# Description:                                   #
# Create petition and respective master account  #
# with error checking. Additionally, add the     #
# account(s) details to SQL database. Finally,   #
# execute bash script to populate master account.#
#                                                #
##################################################
@petition_blueprint.route('/createPetition', methods=['GET', 'POST'])
@login_required
@check_confirmed
def createPetition():
    form = CreatePetitionForm(request.form)
    if form.validate_on_submit():

        petitionWallet              = "Petitions"
        petitionWalletPassword      = "root"
        masterAccountWallet         = "MasterAccounts"
        masterAccountWalletPassword = "root"
        wallets                     = kcl.list_wallets()
        petitionWalletID            = None
        for w in wallets:
    	    if w["name"] == petitionWallet:
                petitionWalletID = w["id"]
                break
        masterAccountWalletID       = None
        for w2 in wallets:
    	    if w2["name"] == masterAccountWallet:
                masterAccountWalletID = w2["id"]
                break

        # if it doesn't exist, create the wallet and get its ID
        if not petitionWalletID:
            petitionWalletID = kcl.create_wallet(petitionWallet, petitionWalletPassword)["id"]

        # get a handle for the wallet
        handle = kcl.init_wallet_handle(petitionWalletID, petitionWalletPassword)
        #### MASTER ACCOUNTS
        # if it doesn't exist, create the wallet and get its ID
        if not masterAccountWalletID:
            masterAccountWalletID = kcl.create_wallet(masterAccountWallet, masterAccountWalletPassword)["id"]
        # get a handle for the wallet
        handle2 = kcl.init_wallet_handle(masterAccountWalletID, masterAccountWalletPassword)
        # generate account with account and check if it's valid
        private_key_1, address_1 = account.generate_account()
        # generate master account with account and check if it's valid
        private_key_2, address_2 = account.generate_account()
        # import generated account into the wallet
        kcl.import_key(handle, private_key_1)
        kcl.import_key(handle2, private_key_2)

        petition = Petition(
            name=form.name.data,
	        publicKey=address_1,
            masterAccount = address_2,
            yesCount=0,
            startDate=form.startDate.data,
            endDate=form.endDate.data
        )
        db.session.add(petition)
        db.session.commit()

        # Run bash script that automatically transfers microAlgos
        # from unencrypted-default-wallet to the desired Peition's
        # Master Account.
        subprocess.call(["project/petition/autoDispense.sh",str(address_2)])

        flash('Petition has been created!.', 'success')

    return render_template('petition/createPetition.html', form=form)


#####################################################
#                                                   #
# Return type:                                      #
# (Boolean)                                         #
#                                                   #
# Parameters:                                       #
# (String) - Current user's email.                  #
# (Dict)   - Collection of transactions for the     #
#            specified Algorand account address.    #
# (String) - Indicate which type of vote(yes or no) #
#            the function is handling so it's knows #
#            which algorithm to use.                #
#                                                   #
# Description:                                      #
# If checking "Yes" votes; Iterate through Dict and #
# parse JSON data to check if String matches itself #
# in Dict; return True if such; otherwise return    #
# False to indicate no match was found and the user #
# has not voted for a particular petition yet.      #
#                                                   #
# If checking "No" votes; Iterate through Dict and  #
# check the key value if it matches itself, return  #
# True if such, otherwise return False to indicate  #
# no match was found and the user has not voted for #
# a particular petition yet.                        #
#                                                   #
#####################################################
def DoubleVoteChecker(curUser, txArray, yesNo):
    if yesNo == "Yes":
        txSize = txArray.get("transactions")

        if txSize is None:
            return False

        for i in range(0,len(txSize)):
            currentTx = txArray.get("transactions")[i]
            noteb64 = currentTx.get("noteb64")
            note = base64.b64decode(noteb64)
            email = json.loads(note)["email"]
            if email == str(curUser):
                print(email)
                return True
                break

        return False
    elif yesNo == "No":

        if txArray is None:
            return False

        for key in txArray:
            email = key
            if email == str(curUser):
                print(email)
                return True
                break

        return False


##################################################
#                                                #
# Return type:                                   #
# (Dict)                                         #
#                                                #
# Parameters:                                    #
# (List) Algorand account transactions.          #
# (String) Account public key to check for.      #
#                                                #
# Description:                                   #
# Return Dict of transactions for specific       #
# account with multiple layers of checking       #
# throughout the process.                        #
#                                                #
##################################################
def GetTxListElements(txList, intendedPK):
    list = {}

    if txList is None:
        return {}

    for i in range(0, len(txList)):
        jsonStr     = base64.b64decode(txList[i]['noteb64'])
        realJson    = json.loads(jsonStr)
        email       = realJson["email"]
        timeStamp   = realJson["timeStamp"]
        petitionPK  = realJson["petitionPK"]

        if petitionPK == intendedPK:
            list.update( {str(email) : str(timeStamp)} )

    return list


####################################################
#                                                  #
# Return type:                                     #
# (render_template)                                #
#                                                  #
# Parameters:                                      #
# None                                             #
#                                                  #
# Description:                                     #
# If 'view details' button is clicked, then        #
# first get current petition public key and use    #
# it to parse all the yes votes for account.       #
# Next, get trash bag public key and parse all     #
# appropiate no votes for specific petition        #
# account. Finally, pass that parsed data to HTML. #
#                                                  #
# If button clicked for yes, or no vote; then      #
# then get required account public key(s) and do   #
# error checking to make sure current user is      #
# eligable to vote.                                #
#                                                  #
####################################################
@petition_blueprint.route('/listPetitions', methods=['GET', 'POST'])
@login_required
@check_confirmed
def listPetitions():
    form = ListPetitionForm(request.form)
    if form.validate_on_submit():
        if request.method == 'POST':
            if "details" in request.form:
                curPetition = Petition.query.filter_by(uid=str(request.form["details"])).first()
                startDate   = str(curPetition.startDate.strftime("%b %d %Y"))
                endDate     = str(curPetition.endDate.strftime("%b %d %Y"))
                yes_votes   = acl.transactions_by_address(curPetition.publicKey, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                yes_json    = (GetTxListElements(yes_votes.get("transactions"),curPetition.publicKey))
                trashBagPK  = (Petition.query.filter_by(uid=1).one()).masterAccount
                no_txs      = acl.transactions_by_address(trashBagPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                no_json     = (GetTxListElements(no_txs.get("transactions"),curPetition.publicKey))
                yesCount    = len(yes_json)
                noCount     = len(no_json)
                return render_template('petition/viewDetails.html', startDate=startDate, endDate=endDate, yesCount=yesCount, noCount=noCount, txList=yes_json, NotxList=no_json, curPetition=curPetition)

            elif "voteYes" in request.form:
                petPK                   = str(request.form['voteYes'])
                curPetition             = Petition.query.filter_by(publicKey=petPK).first()
                yestxs                  = acl.transactions_by_address(petPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                trashBagPK              = (Petition.query.filter_by(uid=1).one()).masterAccount
                notxs_raw               = acl.transactions_by_address(trashBagPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                notxs_parsed            = (GetTxListElements(notxs_raw.get("transactions"),curPetition.publicKey))

                if DoubleVoteChecker(current_user.email, notxs_parsed, "No") or DoubleVoteChecker(current_user.email, yestxs, "Yes"):
                    flash("You have already signed this petition.")
                else:
                    masterAccountWallet     = "MasterAccounts"
                    masterAccountPassword   = "root"
                    masterAccount           = (Petition.query.filter_by(publicKey=petPK).one()).masterAccount
                    wallets                 = kcl.list_wallets()
                    masterAccountID         = None
                    for w in wallets:
                        if w["name"] == masterAccountWallet:
                            masterAccountID = w["id"]
                            break
                    masterAccountHandle     = kcl.init_wallet_handle(masterAccountID,masterAccountPassword)
                    petitionWallet          = "Petitions"
                    petitionWalletPassword  = "root"
                    petitionWalletID        = None
                    for w in wallets:
                        if w["name"] == petitionWallet:
                            petitionWalletID = w["id"]
                            break

                    if not petitionWalletID:
                        petitionWalletID = kcl.create_wallet(petitionWallet, petitionWalletPassword)["id"]

                    handle          = kcl.init_wallet_handle(petitionWalletID, petitionWalletPassword)
                    params          = acl.suggested_params()
                    gen             = params["genesisID"]
                    gh              = params["genesishashb64"]
                    last_round      = params["lastRound"]
                    fee             = params["fee"]
                    now             = datetime.datetime.now()
                    dt_string       = now.strftime("%m/%d/%Y %H:%M:%S")
                    #encrypt email like such: str(hashlib.sha256(current_user.email.encode()).hexdigest())
                    jsonInput       = '{"email": "' + str(current_user.email) + '", "timeStamp": "' + str(dt_string) + '", "petitionPK": "' + str(petPK) + '"}'
                    note            = (jsonInput).encode()
                    amount          = 100000
                    txn             = transaction.PaymentTxn(masterAccount, fee, last_round, last_round+100, gh, petPK, amount, gen=gen, note=note)
                    signed_with_kmd = kcl.sign_transaction(masterAccountHandle,masterAccountPassword, txn)
                    private_key     = kcl.export_key(masterAccountHandle, masterAccountPassword,masterAccount)
                    signed_offline  = txn.sign(private_key)
                    transaction_id  = acl.send_transaction(signed_with_kmd)
            elif "voteNo" in request.form:
                # petPK                   = str(request.form['voteNo'])
                # petitionMasterAccount   = (Petition.query.filter_by(publicKey=petPK).one())
                # yestxs                  = acl.transactions_by_address(petPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                # trashBagPK              = (Petition.query.filter_by(uid=1).one()).masterAccount
                # notxs                   = acl.transactions_by_address(trashBagPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                petPK                   = str(request.form['voteNo'])
                curPetition             = Petition.query.filter_by(publicKey=petPK).first()
                yestxs                  = acl.transactions_by_address(petPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                trashBagPK              = (Petition.query.filter_by(uid=1).one()).masterAccount
                notxs_raw               = acl.transactions_by_address(trashBagPK, first=1, last=acl.block_info(acl.status().get("lastRound"))["round"])
                notxs_parsed            = (GetTxListElements(notxs_raw.get("transactions"),curPetition.publicKey))

                if DoubleVoteChecker(current_user.email, notxs_parsed, "No") or DoubleVoteChecker(current_user.email, yestxs, "Yes"):
                    flash("You have already signed this petition.")
                else:
                    masterAccountWallet     = "MasterAccounts"
                    masterAccountPassword   = "root"
                    masterAccount           = (Petition.query.filter_by(publicKey=petPK).one()).masterAccount
                    wallets                 = kcl.list_wallets()
                    masterAccountID         = None
                    for w in wallets:
                        if w["name"] == masterAccountWallet:
                            masterAccountID = w["id"]
                            break
                    masterAccountHandle     = kcl.init_wallet_handle(masterAccountID,masterAccountPassword)
                    petitionWallet          = "Petitions"
                    petitionWalletPassword  = "root"
                    petitionWalletID        = None
                    for w in wallets:
                        if w["name"] == petitionWallet:
                            petitionWalletID = w["id"]
                            break
                    if not petitionWalletID:
                        petitionWalletID = kcl.create_wallet(petitionWallet, petitionWalletPassword)["id"]

                    handle          = kcl.init_wallet_handle(petitionWalletID, petitionWalletPassword)
                    params          = acl.suggested_params()
                    gen             = params["genesisID"]
                    gh              = params["genesishashb64"]
                    last_round      = params["lastRound"]
                    fee             = params["fee"]
                    now             = datetime.datetime.now()
                    dt_string       = now.strftime("%m/%d/%Y %H:%M:%S")
                    #str(hashlib.sha256(current_user.email.encode()).hexdigest())
                    jsonInput       = '{"email": "' + str(current_user.email) + '", "timeStamp": "' + str(dt_string) + '", "petitionPK": "' + str(petPK) + '"}'
                    note            = (jsonInput).encode()
                    amount          = 100000
                    txn             = transaction.PaymentTxn(masterAccount, fee, last_round, last_round+100, gh, trashBagPK, amount, gen=gen, note=note)
                    signed_with_kmd = kcl.sign_transaction(masterAccountHandle,masterAccountPassword, txn)
                    private_key     = kcl.export_key(masterAccountHandle, masterAccountPassword,masterAccount)
                    signed_offline  = txn.sign(private_key)
                    transaction_id  = acl.send_transaction(signed_with_kmd)
                    flash("Success: You have voted!", "success")
    curDate         = datetime.datetime.now().strftime("%Y-%m-%d")
    curPetitions    = Petition.query.filter(Petition.endDate >= curDate)
    pastPetitions   = Petition.query.filter(Petition.endDate < curDate)
    return render_template('petition/listPetitions.html', form=form, pastPetitions=pastPetitions, curPetitions=curPetitions)
