# Brooklyn College eVote
<img width="496" alt="screenshot" src="https://user-images.githubusercontent.com/10848641/65827844-8a82a180-e262-11e9-9bcc-98cd4eafcf1c.png">
(Fig.) Default index page.

<img width="498" alt="createPetition" src="https://user-images.githubusercontent.com/10848641/65838085-4a0c3d80-e2cd-11e9-99a1-af29eab94e2f.png">
(Fig.) Create petition page.

<img width="843" alt="votes" src="https://user-images.githubusercontent.com/10848641/65838013-44622800-e2cc-11e9-8bf1-8672a7e5aa41.png">
(Fig.) View more details page.

# Dev Environment Specifications:
-Tested on Mac OS X 10.14

-Tested on Ubuntu 18.04.03 with VirtualBox v5.50.20

-Written in Python3.6.8.

### Local Setup/Installation Process [for OS X]:
### Part One - Install Algorand Node:
1. Click on this link and follow instructions for your specific operating system: https://developer.algorand.org/docs/introduction-installing-node

### Part Two - Install Python Virtual Environment and BCeV:
1. Create empty parent directory.
2. Create Python virtual environment within new parent directory `python3 -m venv venv`
3. Activate virtual environment`source venv/bin/activate` then `cd venv`
4. `git clone https://github.com/AlexanderHart/BCeVote.git`
5. `cd BCeVote`
6. `pip3 install -r requirements.txt`
7. `pip3 install py-algorand-sdk`
8. Set environment variables, APP_MAIL_USERNAME and APP_MAIL_PASSWORD to your email and password, respectfully. Also, these values can be hardcoded in /project/config.py, if desired in line 24 and 25.
9. Create bash executable Within project directory: `chmod u+x autoDispense.sh`

### Part Three - Start Algodorand Processes & Update Files:
1. `sudo ./goal node start -d data`
2. `sudo ./goal kmd start -d data`
*2.1* IMPORTANT TO NOTE: Make sure to have at least 1 wallet generated locally to avoid KMD errors. 
3. Update data_dir_path in line 17 at BCeVote/project/params.py to your absoulute path name for your Algorand node location.
4. Update /project/petitions/views.py line 39 with the API for PureStake Algorand node.

### Part Four - Install Python Certificates for SSL security
1. `sudo open /Applications/Python\ 3.6/Install\ Certificates.command`

### Part Five - Run setup processes for BCeV
1. `python3 manage.py create_db`
2. `python3 manage.py db init`
3. `python3 manage.py db migrate`
4. `python3 manage.py create_admin`
5. `python3 manage.py create_trashbag`
6. `python3 manage.py runserver`
7. Navigate to 127.0.0.1:5000 to demo BCeV.

### Part Six - Depositing MicroAlgos into Petition Wallet
After a petition is submitted via the form, the admin must manually copy the data record for the appropiate 'master account' attribute from the Petitions SQL table. Following that, the admin directs himself to https://bank.testnet.algorand.network and paste the data into the textfield deposit MicroAlgos into the desired petition.

# Credit & Acknowledgement:
Credit and acknowledgement goes to GitHub user mjhea0, for his repo https://github.com/mjhea0/flask-basic-registration.git for which we used it for our user registration. 
