from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.reverse import reverse

from airport.models import Ticket
from airport.serializers import TicketListSerializer
from airport.tests.sample import sample_ticket, sample_flight, sample_order


TICKET_URL = reverse("airport:ticket-list")

class UnauthenticatedTicketTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email@gmail.com",
            password="<PASSWORD>",
        )
        self.client.force_authenticate(user=self.user)

    def test_ticket_list(self):
        sample_ticket()

        res = self.client.get(TICKET_URL)
        tickets = Ticket.objects.all()
        serializer = TicketListSerializer(tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data )

    def test_create_ticket(self):
        flight = sample_flight()
        order = sample_order()
        payload = {
            "row": 9,
            "seat": 9,
            "flight": flight.id,
            "order": order.id,
        }

        res = self.client.post(TICKET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AdminTicketApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_ticket(self):
        flight = sample_flight()
        order = sample_order()
        payload = {
            "row": 9,
            "seat": 9,
            "flight": flight.id,
            "order": order.id,
        }

        res = self.client.post(TICKET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
