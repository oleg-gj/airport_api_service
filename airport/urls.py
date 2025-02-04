from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    TicketViewSet,
    OrderViewSet,
    CrewViewSet,
    FlightViewSet
)

router = routers.DefaultRouter()
router.register("airport", AirportViewSet)
router.register("route", RouteViewSet)
router.register("airplane", AirplaneViewSet)
router.register("airplane_type", AirplaneTypeViewSet)
router.register("ticket", TicketViewSet)
router.register("order", OrderViewSet)
router.register("crew", CrewViewSet)
router.register("flight", FlightViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "airport"
