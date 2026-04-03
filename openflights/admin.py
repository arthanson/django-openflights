"""Django admin configuration for OpenFlights models."""

from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Aircraft, Airline, Airport, Port, TrainStation


class TransportHubAdmin(GISModelAdmin):
    """Base admin for transport hub models."""

    list_display = (
        "id",
        "openflights_id",
        "name",
        "iata",
        "icao",
        "city_name",
        "country_name",
        "timezone",
    )
    list_filter = ("country_name", "source")
    search_fields = ("name", "iata", "icao", "city_name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Airport)
class AirportAdmin(TransportHubAdmin):
    """Admin for Airport model."""

    pass


@admin.register(TrainStation)
class TrainStationAdmin(TransportHubAdmin):
    """Admin for TrainStation model."""

    pass


@admin.register(Port)
class PortAdmin(TransportHubAdmin):
    """Admin for Port model."""

    pass


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    """Admin for Airline model."""

    list_display = (
        "id",
        "openflights_id",
        "name",
        "iata",
        "icao",
        "callsign",
        "country_name",
        "is_active",
    )
    list_filter = ("is_active", "country_name")
    search_fields = ("name", "iata", "icao", "callsign", "alias")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    """Admin for Aircraft model."""

    list_display = ("id", "name", "iata", "icao")
    search_fields = ("name", "iata", "icao")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)
