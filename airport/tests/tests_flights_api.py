from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Flight
from airport.serializers import FlightListSerializer, FlightSerializer
from airport.tests.sample import (
    sample_flight,
    sample_airplane,
    sample_route,
    sample_crew,
)


FLIGHT_URL = reverse("airport:flight-list")

class UnauthenticatedFlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFightTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)

    def test_flight_list(self):
        sample_flight()

        res = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)
        serial_data = serializer.data
        serial_data[0]["tickets_available"] = 100

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serial_data )

    def test_create_flights_forbidden(self):
        payload = {
            "route": 123,
            "airplane":"Boing",
            "departure_time": "2020-10-10",
            "arrival_time": "2020-10-11",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        payload = {
            "route": sample_route().id,
            "airplane": sample_airplane().id,
            "departure_time": "2020-10-10T00:00:00Z",
            "arrival_time": "2020-10-11T00:00:00Z",
            "crews": [sample_crew().id,]
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        serializer = FlightSerializer(flight)

        for key in payload:
            self.assertEqual(payload[key], serializer.data[key])
