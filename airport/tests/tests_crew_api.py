from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Crew
from airport.serializers import CrewSerializer
from airport.tests.sample import sample_crew


CREW_URL = reverse("airport:crew-list")

class UnauthenticatedCrewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)

    def test_crew_list(self):
        sample_crew()

        res = self.client.get(CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data )

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Mark",
            "last_name": "Mitchell"
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "Mark",
            "last_name": "Mitchell"
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(id=res.data["id"])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(crew, key))
