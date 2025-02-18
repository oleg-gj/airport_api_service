from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Route
from airport.serializers import RouteListSerializer, RouteSerializer
from airport.tests.sample import sample_route, sample_airport


ROUTE_URL = reverse("airport:route-list")

class UnauthenticatedRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)

    def test_route_list(self):
        sample_route()

        res = self.client.get(ROUTE_URL)
        routs = Route.objects.all()
        serializer = RouteListSerializer(routs, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data )

    def test_create_route_forbidden(self):
        payload = {
            "source": "Kyiv",
            "destination": "Zhitomyr",
            "distance": 1200
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        payload = {
            "source": sample_airport(name="Shopen").id,
            "destination": sample_airport().id,
            "distance": 1200
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        serializer = RouteSerializer(route)

        for key in payload.keys():
            self.assertEqual(payload[key], serializer.data.get(key))
