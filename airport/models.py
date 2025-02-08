from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from rest_framework.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    closest_big_city = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.name} ({self.closest_big_city})"

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="sours_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_route"
    )
    distance = models.IntegerField()

    @property
    def name(self):
        return f"{self.source} -> {self.destination}"

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        "Airplane", on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField("Crew", related_name="flights")

    @property
    def name(self):
        return f"{self.route}: {self.airplane.name}"

    def __str__(self):
        return f"{self.route}: {self.airplane.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.first_name + " " + self.last_name


class Airplane(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType", on_delete=models.CASCADE, related_name="airplane_types"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="tickets", blank=True, null=True
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=["row", "seat", "flight"], name="unique_ticket")
        ]

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range:"
                        f" (1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    @property
    def taken_places(self):
        return f"row:{self.row} seat:{self.seat}"

    @property
    def name(self):
        return f"{self.flight}: {self.order} (row:{self.row} seats:{self.seat})"

    def __str__(self):
        return f"{self.flight}: {self.order} (row:{self.row} seats:{self.seat})"


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    @property
    def name(self):
        return f"{self.user}: {self.created.isoformat()}"

    def __str__(self):
        return f"{self.user.username} ({self.created})"
