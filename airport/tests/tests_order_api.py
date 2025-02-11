from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Order
from airport.serializers import OrderListSerializer
from airport.tests.sample import sample_airplane


ORDER_URL = reverse("airport:order-list")

class UnauthenticatedAirportTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)

    def test_order_list(self):
        sample_airplane()

        res = self.client.get(ORDER_URL)
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data )
