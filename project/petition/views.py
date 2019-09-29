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
import hashlib


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
import time

################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)
petition_blueprint = Blueprint('petition', __name__,)

kcl = kmd.KMDClient("780954d4d6d9a6e052d92f4b6c91c5f8f044514cabe1c697b3904270c784fd75", "http://127.0.0.1:7833")
acl = algod.AlgodClient("4a327d8ae7faa2d890ff05d95bae2a167b7bdff2e58630dd4afff1f693856d90", "http://127.0.0.1:8080")

################
#### routes ####
################

@petition_blueprint.route('/createPetition', methods=['GET', 'POST'])
@login_required
@check_confirmed
def createPetition():
    form = CreatePetitionForm(request.form)
    if form.validate_on_submit():

        petitionWallet = "Petitions"
        petitionWalletPassword = "root"

        masterAccountWallet = "MasterAccounts"
        masterAccountWalletPassword = "root"


        # get the wallet ID
        wallets = kcl.list_wallets()

        petitionWalletID = None
        for w in wallets:
    	    if w["name"] == petitionWallet:
                petitionWalletID = w["id"]
                break

        masterAccountWalletID = None
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

        flash('Petition has been created!.', 'success')

    return render_template('petition/createPetition.html', form=form)


def DoubleVoteChecker(curUser, txArray):
    txSize = txArray.get("transactions")

    for i in range(0,len(txSize)):
        currentTx = txArray.get("transactions")[i]
        # read noteb64 field of first transaction
        noteb64 = currentTx.get("noteb64")
        # Decode to bytes
        note = base64.b64decode(noteb64)
        print(note)
        print("Note type: " + str(type(note)))
        print(type(json.loads(note)))
        email = json.loads(note)["email"]
        if email == str(curUser):
            return True
            break
    return False


def GetTxListElements(txList):
    list = {}
    for i in range(0, len(txList)):
        test = base64.b64decode(txList[i]['noteb64'])
        jsonTest = json.loads(test)
        email = jsonTest["email"]
        timeStamp = jsonTest["timeStamp"]
        
        list.update( {str(email) : str(timeStamp)} )
        print("test::")
        print(list)

    return list


@petition_blueprint.route('/listPetitions', methods=['GET', 'POST'])
@login_required
@check_confirmed
def listPetitions():
    form = ListPetitionForm(request.form)
    if form.validate_on_submit():
        if request.method == 'POST':
            if "details" in request.form:
                curPetition = Petition.query.filter_by(uid=str(request.form["details"])).first()
                txs = acl.transactions_by_address(curPetition.publicKey, first=10399, last=acl.block_info(acl.status().get("lastRound"))["round"])
                print("test")
                print("test")
                my_json = (GetTxListElements(txs.get("transactions")))
                print("HODL")
                #print(type((GetTxListElements(txs.get("transactions"))[0]).decode()))
                #print(GetTxListElements(txs.get("transactions"))[0])
                #print(str(type(GetTxListElements(txs.get("transactions"))[0].decode('utf8'))))
                #print(str(type(GetTxListElements(txs.get("transactions"))[0])))
                #print("Json:")
                #print(my_json)

                testJson='{"history":{"tx":[{"email":"1","timeStamp":"1321"},{"email":"2","timeStamp":"132333331"}]}}'

                my_list = {"alex@gmail.com":"4141312413", "jon@gmail.com":"4141312413"}
                #my_json_string = json.dumps(my_list)
                print("values")
                #print(my_json_string)
                #print(my_json_string)
                #data = json.loads(testJson)
                #s = json.dumps(data, indent=4, sort_keys=True)
                print("MESSAGE")
                #print(data["history"])
                #print(s)

                return render_template('petition/viewDetails.html', txList=my_json, curPetition=curPetition)
            elif "voteYes" in request.form:
                petPK = str(request.form['voteYes'])
                petitionMasterAccount = (Petition.query.filter_by(publicKey=petPK).one())
                txs = acl.transactions_by_address(petPK, first=10399, last=acl.block_info(acl.status().get("lastRound"))["round"])

                ## Error checking for when no votes has been casted yet.
                if txs.get("transactions") is None:
                    print("No votes has been casted yet.")
                    masterAccountWallet = "MasterAccounts"
                    masterAccountPassword = "root"
                    masterAccount = petitionMasterAccount.masterAccount

                    wallets = kcl.list_wallets()
                    masterAccountID = None
                    for w in wallets:
                        if w["name"] == masterAccountWallet:
                            masterAccountID = w["id"]
                            break

                    masterAccountHandle = kcl.init_wallet_handle(masterAccountID,masterAccountPassword)

                    petitionWallet = "Petitions"
                    petitionWalletPassword = "root"

                    petitionWalletID = None
                    for w in wallets:
                        if w["name"] == petitionWallet:
                            petitionWalletID = w["id"]
                            break

                    if not petitionWalletID:
                        petitionWalletID = kcl.create_wallet(petitionWallet, petitionWalletPassword)["id"]

                    handle = kcl.init_wallet_handle(petitionWalletID, petitionWalletPassword)
                    params = acl.suggested_params()
                    gen = params["genesisID"]
                    gh = params["genesishashb64"]
                    last_round = params["lastRound"]
                    fee = params["fee"]
                #jsonInput = '{"email": "' + str(hashlib.sha256(current_user.email.encode()).hexdigest()) + '", "timeStamp": "34123213124.32412"}'
                    jsonInput = '{"email": "' + str(current_user.email) + '", "timeStamp": "' + str(time.time()) + '"}'
                    note = (jsonInput).encode()
                    amount = 103000
                    txn = transaction.PaymentTxn(masterAccount, fee, last_round, last_round+100, gh, petPK, amount, gen=gen, note=note)
                    signed_with_kmd = kcl.sign_transaction(masterAccountHandle,masterAccountPassword, txn)
                    private_key = kcl.export_key(masterAccountHandle, masterAccountPassword,masterAccount)
                    signed_offline = txn.sign(private_key)
                    transaction_id = acl.send_transaction(signed_with_kmd)
                    print(transaction_id)
                else:
                    if DoubleVoteChecker(current_user.email, txs):
                        flash(str(current_user.email) + " has already signed this petition.")
                    else:
                        masterAccountWallet = "MasterAccounts"
                        masterAccountPassword = "root"
                        masterAccount = petitionMasterAccount.masterAccount

                        wallets = kcl.list_wallets()
                        masterAccountID = None
                        for w in wallets:
                            if w["name"] == masterAccountWallet:
                                masterAccountID = w["id"]
                                break

                        masterAccountHandle = kcl.init_wallet_handle(masterAccountID,masterAccountPassword)

                        petitionWallet = "Petitions"
                        petitionWalletPassword = "root"

                        petitionWalletID = None
                        for w in wallets:
                            if w["name"] == petitionWallet:
                                petitionWalletID = w["id"]
                                break

                        if not petitionWalletID:
                            petitionWalletID = kcl.create_wallet(petitionWallet, petitionWalletPassword)["id"]

                        handle = kcl.init_wallet_handle(petitionWalletID, petitionWalletPassword)
                        params = acl.suggested_params()
                        gen = params["genesisID"]
                        gh = params["genesishashb64"]
                        last_round = params["lastRound"]
                        fee = params["fee"]
                    #jsonInput = '{"email": "' + str(hashlib.sha256(current_user.email.encode()).hexdigest()) + '", "timeStamp": "34123213124.32412"}'
                        jsonInput = '{"email": "' + str(current_user.email) + '", "timeStamp": "' + str(time.time()) + '"}'
                        note = (jsonInput).encode()
                        amount = 103000
                        txn = transaction.PaymentTxn(masterAccount, fee, last_round, last_round+100, gh, petPK, amount, gen=gen, note=note)
                        signed_with_kmd = kcl.sign_transaction(masterAccountHandle,masterAccountPassword, txn)
                        private_key = kcl.export_key(masterAccountHandle, masterAccountPassword,masterAccount)
                        signed_offline = txn.sign(private_key)
                        transaction_id = acl.send_transaction(signed_with_kmd)
                        print(transaction_id)

    curDate = datetime.datetime.now().strftime("%Y-%m-%d")
    curPetitions = Petition.query.filter(Petition.endDate >= curDate)
    pastPetitions = Petition.query.filter(Petition.endDate < curDate)
    return render_template('petition/listPetitions.html', form=form, pastPetitions=pastPetitions, curPetitions=curPetitions)
