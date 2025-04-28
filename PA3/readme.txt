step 1:
git clone

step 2:
cd PA3

step 3:
python3 --version
maks sure using 3.10.8, for pylint test
if no python go install it

step 4: create environment
python3 -m venv venv
source venv/bin/activate

step 5:
pip install -r requirements.txt

step 6:
flask --app flaskr run

TEST

install test:
pip install pytest coverage

run test:
coverage run -m pytest

see coverage report:
coverage report -m


pip install mypy

mypy flaskr

mypy tests


pip install pylint


# if use conda
python -m pylint flaskr