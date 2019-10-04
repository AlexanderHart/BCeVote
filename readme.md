# Brooklyn College eVote
<img width="496" alt="screenshot" src="https://user-images.githubusercontent.com/10848641/65827844-8a82a180-e262-11e9-9bcc-98cd4eafcf1c.png">
(Fig.) Default index page.

<img width="498" alt="createPetition" src="https://user-images.githubusercontent.com/10848641/65838085-4a0c3d80-e2cd-11e9-99a1-af29eab94e2f.png">
(Fig.) Create petition page.

<img width="843" alt="votes" src="https://user-images.githubusercontent.com/10848641/65838013-44622800-e2cc-11e9-8bf1-8672a7e5aa41.png">
(Fig.) View more details page.

# Dev Environment Specifications:
-Ubuntu 18.04.03

-VirtualBox v5.50.20

-Python3 

### How to install and setup locally:
1. Create empty parent directory.
2. `$ python3 -m venv venv`
3. Clone repo into venv directory.
4. `$ source venv/bin/activate`
5. `$ pip3 -r install requirements.txt`
6. `$ pip3 install py-algorand-sdk`
7. Set environment variables, APP_MAIL_USERNAME and APP_MAIL_PASSWORD to your email and password, respectfully.
8. `$ python manage.py create_db`
`$ python manage.py db init`
`$ python manage.py db migrate`
`$ python manage.py create_admin`
`$ python manage.py create_trashbag`
`$ python manage.py runserver`

# Credit & Acknowledgement:
Credit and acknowledgement goes to GitHub user mjhea0, for his repo https://github.com/mjhea0/flask-basic-registration.git for which we used it for our user registration. 
