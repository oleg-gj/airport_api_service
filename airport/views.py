from datetime import datetime
from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    Airport,
    Route,
    Flight,
    Crew,
    Airplane,
    AirplaneType,
    Ticket,
    Order,
)
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    TicketSerializer,
    OrderSerializer,
    CrewSerializer,
    FlightSerializer,
    AirplaneListSerializer,
    TicketListSerializer,
    OrderListSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return self.serializer_class


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        departure_date = self.request.query_params.get("departure_date")
        arrival_date = self.request.query_params.get("arrival_date")
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")

        if self.action in ("retrieve", "list"):
            queryset = (
                queryset.select_related("airplane").annotate(
                    tickets_available=F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            ).order_by("id")

        if departure_date:
            departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure_date)

        if arrival_date:
            arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_date)

        if source_city:
            queryset = queryset.filter(
                route__source__closest_big_city__icontains=source_city
            )

        if destination_city:
            queryset = queryset.filter(
                route__destination__closest_big_city__icontains=destination_city
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_date",
                type=OpenApiTypes.DATE,
                description="Filter by departure date (ex. ?departure_date=2019-01-10)",
            ),
            OpenApiParameter(
                "arrival_date",
                type=OpenApiTypes.DATE,
                description="Filter by arrival date (ex. ?arrival_date=2019-01-10)",
            ),
            OpenApiParameter(
                "source_city",
                type=OpenApiTypes.STR,
                description="Filter by source city (ex. ?source_city=Kyiv)",
            ),
            OpenApiParameter(
                "destination_city",
                type=OpenApiTypes.STR,
                description="Filter by destination city (ex. ?destination_city=Kyiv)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return self.serializer_class


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        airplane = self.request.query_params.get("airplane")
        source_city = self.request.query_params.get("source_city")
        destination_city = self.request.query_params.get("destination_city")

        queryset = self.queryset

        if airplane:
            airplane_ids = [int(str_id) for str_id in airplane.split(",")]
            queryset = queryset.filter(flight__airplane_id__in=airplane_ids)

        if source_city:
            queryset = queryset.filter(
                flight__route__source__closest_big_city__icontains=source_city
            )

        if destination_city:
            queryset = queryset.filter(
                flight__route__destination__closest_big_city__icontains=destination_city
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TicketListSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by airplane ID (ex. ?airplane=2,3)",
            ),
            OpenApiParameter(
                "source_city",
                type=str,
                description="Filter by source city (ex. ?source_city=Kyiv)",
            ),
            OpenApiParameter(
                "destination_city",
                type=str,
                description="Filter by destination city (ex. ?destination_city=Kyiv)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return self.serializer_class
