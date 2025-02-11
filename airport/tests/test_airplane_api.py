from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Airplane
from airport.serializers import AirplaneListSerializer, AirplaneSerializer
from airport.tests.sample import sample_airplane, sample_airplane_type


AIRPLANE_URL = reverse("airport:airplane-list")

class UnauthenticatedAirplaneTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)

    def test_airplane_list(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data )

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Boing",
            "rows": 6,
            "seats_in_row": 10,
            "airplane_type": sample_airplane_type(),
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@gmail.com",
            password="strong_password",
            is_staff=True,
        )
        self.client.force_authenticate(self.user, [])

    def test_create_airplane(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "Boing",
            "rows": 6,
            "seats_in_row": 10,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])
        serializer = AirplaneSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], serializer.data[key])
