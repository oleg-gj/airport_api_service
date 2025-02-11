from datetime import datetime
from django.contrib.auth import get_user_model
from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Flight,
    Route,
    Crew,
    Order,
    Ticket
)


def sample_user(**params):
    defaults = {
        "email": "email@gmail.com",
        "password": "<PASSWORD>",
    }
    defaults.update(params)
    return get_user_model().objects.create(**defaults)

def sample_order(**params) -> Order:
    defaults = {
        "created": datetime.now(),
        "user": sample_user(email="new_user@gmail.com"),
    }
    defaults.update(params)

    return Order.objects.create(**defaults)

def sample_route(**params) -> Route:
    defaults = {
        "source": sample_airport(),
        "destination": sample_airport(name="Kyiv"),
        "distance": 1200
    }
    defaults.update(params)

    return Route.objects.create(**defaults)

def sample_airplane_type(**params) -> AirplaneType:
    defaults = {
        "name": "Passenger"
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)

def sample_airport(**params) -> Airport:
    defaults = {
        "name": "Modlin",
        "closest_big_city": "Warshawa"
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)

def sample_airplane(**params) -> Airplane:
    defaults = {
        "name": "Boing 777",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": sample_airplane_type(),
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)

def sample_crew(**params) -> Crew:
    defaults = {
        "first_name": "Peter",
        "last_name": "Mitchell",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)

def sample_flight(**params) -> Flight:
    defaults = {
        "route": sample_route(),
        "airplane": sample_airplane(name="Boing"),
        "departure_time": "2020-10-10",
        "arrival_time": "2020-10-11",
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)

def sample_ticket(**params) -> Ticket:
    defaults = {
        "row": 10,
        "seat": 10,
        "flight": sample_flight(),
        "order": sample_order(),
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)
