#Warbler
Warbler is a Twitter clone built using Flask with SQLAlchemy and Jinja templates.

#Features that have been implemented:
Creating a user
Profile page
Editing profiles
Following other users
Blocking other users
Writing posts
Liking posts
Libraries
Bcrypt: used for encrypting passwords
WTForms: used for form validation
SQLAlchemy: an Object Relational Mapper

#Setup
"python3 -m venv venv" at the root directory to create a virtual environment
"source venv/bin/activate" to activate the virtual environment
"pip install -r requirements.txt" to install requirements
"createdb warbler" to create a new database
"python seed.py" to seed the database
"flask run" to start the server at http://localhost:5000/

#Testing
How to run the test files:
"createdb warbler-test" to create the test database
"python seed.py" to seed the database
"python3 -m unittest -v name_of_test_file" to run one test file. The test files start with "_test". The -v flag can also be excluded if you do not want to see the status of individual tests.
