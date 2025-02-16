# Api Airport Service

## Description
API service for airport management written on DRF

## Features
* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing orders and tickets
* Creating airplane with airplane type
* Creating route and flight
* Adding crew
* Filtering tickets and flight

## Installing using GitHub

Check .env

Install PostgresSQL and create db

```shell
git clone https://github.com/oleg-gj/Service-for-the-restaurant-kitchen
cd airport_API
python3 -m venv venv
source venv/Script/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

```
## Loading Initial Data (Optional)

To load initial sample data into your database, you can use the following command:

```shell
python manage.py loaddata db.json
```


## Run with docker
Docker should be installed

```shell
docker compose build
docker compose up
```

Create Admin

```shell
docker compose run airport python manage.py createsuperuser
```

Loading Initial Data (Optional)

```shell
docker compose run airport python manage.py loaddata db.json
```

## Getting access
* create user via /api/user/register
* get access token via /api/user/token/

## Licensing

This project is licensed under an Unlicense license. This license does not require
you to take the license with you to your project.
