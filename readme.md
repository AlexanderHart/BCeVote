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

### Local Setup/Installation Process:
### Part One - Install Algorand Node:
1. Click on this link and follow instructions for your specific operating system: https://developer.algorand.org/docs/introduction-installing-node

### Part Two - Install BCeV:
1. Create empty parent directory.
2. Create Python virtual environment `$ python3 -m venv venv`
3. Clone repo into venv directory.
4. Activate virtual environment`$ source venv/bin/activate`
5. `$ pip3 -r install requirements.txt`
6. `$ pip3 install py-algorand-sdk`
7. Set environment variables, APP_MAIL_USERNAME and APP_MAIL_PASSWORD to your email and password, respectfully. Also, these values can be hardcoded in /project/config.py, if desired.

### Part Three - Create and run Private Network/Algod Processes & Update Config:
1. Create a private network with `./goal network create -r ~/algodNet -n private -t <path_to_template.json>`
NOTICE: We supply the template JSON file (from the Algorand developer page) that can be used in the above step. Locate the file at the following path: <YourParentDirectory>/venv/BCeV-master/project/privateNetwork.json
2. `./goal network start -r ~/algodNet`
3. `./goal kmd start -d ~/algodNet/Primary`
4. Using the API keys in files: algod.net algod.token kmd.net kmd.token in ~/algodNet/Primary and ~/algodNet/Primary/kmd, respectfully, then open config.py located at <YourParentDirectory>/venv/BCeV-master/project/config.py and update the API credentials where neccesary. 

### Part Four - Run setup processes for Flask
1. `$ python manage.py create_db`
2. `$ python manage.py db init`
3. `$ python manage.py db migrate`
4. `$ python manage.py create_admin`
5. `$ python manage.py create_trashbag`
6. `$ python manage.py runserver`
7. Navigate to 127.0.0.1:5000 to demo BCeV.

# Credit & Acknowledgement:
Credit and acknowledgement goes to GitHub user mjhea0, for his repo https://github.com/mjhea0/flask-basic-registration.git for which we used it for our user registration. 
