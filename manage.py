# manage.py


import os
import unittest
import coverage
import datetime
import hashlib
from project import params

from algosdk import encoding
from algosdk import transaction
from algosdk import kmd
from algosdk import algod
from algosdk import account
from algosdk import mnemonic

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from project import app, db
from project.models import User, Petition


app.config.from_object("project.config.DevelopmentConfig")

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Runs the unit tests without coverage."""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    cov = coverage.coverage(branch=True, include='project/*')
    cov.start()
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    cov.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    cov.erase()


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(
        email=str(hashlib.sha256("ad@min.com".encode()).hexdigest()),
        password="admin",
        admin=True,
        confirmed=True,
        confirmed_on=datetime.datetime.now())
    )
    db.session.commit()

@manager.command
def create_trashbag():
    kcl = kmd.KMDClient(params.kmd_token, params.kmd_address)
    acl = algod.AlgodClient(params.algod_token, params.algod_address)

    petitionWallet = "Petitions"
    petitionWalletPassword = "root"



    # get the wallet ID
    wallets = kcl.list_wallets()

    petitionWalletID = None
    for w in wallets:
        if w["name"] == petitionWallet:
            petitionWalletID = w["id"]
            break

    # if it doesn't exist, create the wallet and get its ID
    if not petitionWalletID:
        petitionWalletID = kcl.create_wallet(petitionWallet, petitionWalletPassword)["id"]

    # get a handle for the wallet
    handle = kcl.init_wallet_handle(petitionWalletID, petitionWalletPassword)
    # generate account with account and check if it's valid
    private_key_1, address_1 = account.generate_account()
    # import generated account into the wallet
    kcl.import_key(handle, private_key_1)

    """Creates trash bag account for all petitions."""
    petition = Petition(
        name="Trash Bag Account",
    publicKey=address_1,
    masterAccount = address_1,
        yesCount=0
    )
    db.session.add(petition)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
