from algosdk import kmd
from algosdk import algod
from algosdk.wallet import Wallet
from algosdk import account
from algosdk import mnemonic
#from algosdk import encoding

import json
from getpass import getpass


#Creating kmd and algod sign(This was taken from python_SDK_Algorand). This will start up things
kcl = kmd.KMDClient(params.kmd_token, params.kmd_address)
acl = algod.AlgodClient(params.algod_token, params.algod_address)

#This module was created by Vivek Sharma
def create_New_Wallet(wallet_name,wallet_pass):#This will create a wallet with chosen id and password
    print("Please remember your Wallet Name:(It can't be recovered now)");
    print(wallet_name,wallet_pass)
    wallet_id = kcl.create_wallet(wallet_name, wallet_pass)["id"]#These 3 lines were taken from algorand website
    print("Wallet created!")
    print("Wallet ID: " + wallet_id)
    #generate_key(display_mnemonic=True)
    #get_mnemonic()
    #info()
    account_choice = input("Do you want to create an account. Press y or Y to procedd. To exit press n or N")
    if account_choice == "Y" or account_choice == "y":
        create_New_Account(wallet_id,wallet_pass)
    else:
        sys.exit(0)

def create_New_Account(wallet_id,wallet_pass):#Taken from algorand example.py, changed the variable name to more suitable one
    wallet_handle = kcl.init_wallet_handle(wallet_id, wallet_pass)
    account_private_key, account_address = account.generate_account()
    kcl.import_key(handle, accouunt_private_key)  # import generated account into the wallet
    mnemonice_phrase = mnemonic.from_private_key(account_private_key)
    print("Wallet handle token: " + handle + "\n")
    print("Private key: " + account_private_key + "\n")
    print("Account address: " + account_address)
    print("Mnemonic phrase generated for the account:(Keep it safe) " + mnemonice_phrase + "\n")
    algosdk.algod.account_info(address, **kwargs)

#Main Program starts from here
choice_user = input("""Welcome to Test ALgorand program
                        If you wish to create an wallet, press y/Y""")
if wallet_choice == 'y' or walet_choice == 'Y':
    wallet_name = input("Enter a name for your wallet")
    wallet_password = getpass()
    create_New_Wallet(wallet_name,wallet_password)
