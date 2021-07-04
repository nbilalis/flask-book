# flask-book

A minimal social wep-app using **Python** / **Flask** and **SQlite** / **SQLAlchemy**.

## Steps to get you running

1. Run appropriate script (`_setup_venv.ps1` or `_setup_venv.sh`) to setup your virtual environment.
1. Set the `python.pythonPath` option accordingly.
1. Run `flask init-db` to initialize the database.
1. Run `flask add-data` to add some test data.
1. Run `flask run` to start the server

## Run this to initialize the DB through migrations

1. `flask db init`
1. `flask db migrate -m "Initial migration"`
1. `flask db upgrade`
