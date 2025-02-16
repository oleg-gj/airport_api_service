from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    Route,
    Flight,
    Crew,
    AirplaneType,
    Ticket,
    Order,
    Airplane,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        slug_field="full_name",
        read_only=True
    )
    destination = serializers.SlugRelatedField(
        slug_field="full_name",
        read_only=True
    )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class FlightSerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crews",
            "tickets_available",
        )


class FlightListSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(slug_field="name", read_only=True)
    airplane = serializers.SlugRelatedField(slug_field="name", read_only=True)
    crews = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=True
    )


class FlightDetailSerializer(FlightListSerializer):
    taken_places = serializers.SlugRelatedField(
        source="tickets", many=True, read_only=True, slug_field="taken_places"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crews",
            "tickets_available",
            "taken_places",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity"
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketListSerializer(TicketSerializer):
    flight = serializers.SlugRelatedField(slug_field="name", read_only=True)
    order = serializers.SlugRelatedField(slug_field="name", read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    tickets = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=True,
    )

    class Meta:
        model = Order
        fields = ("id", "created", "user", "tickets")
