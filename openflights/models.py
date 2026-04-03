"""
Django models for OpenFlights aviation data.

Provides models for airports, train stations, ports, airlines, and aircraft.

Note: Route data is not included as OpenFlights no longer maintains route information.
"""

from django.contrib.gis.db import models as gis_models
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TransportHub(models.Model):
    """
    Abstract base model for transport hubs.

    Shared fields for airports, train stations, and ports.
    """

    # OpenFlights identifier
    openflights_id = models.PositiveIntegerField(
        _("OpenFlights ID"),
        unique=True,
        help_text=_("Unique identifier from OpenFlights database"),
    )

    # Basic info
    name = models.CharField(
        _("name"),
        max_length=200,
        db_index=True,
    )
    slug = models.SlugField(
        _("slug"),
        max_length=200,
        blank=True,
    )

    # Transportation codes
    iata = models.CharField(
        _("IATA code"),
        max_length=3,
        blank=True,
        db_index=True,
        validators=[MinLengthValidator(3)],
        help_text=_("3-letter IATA/FAA code"),
    )
    icao = models.CharField(
        _("ICAO code"),
        max_length=4,
        blank=True,
        db_index=True,
        validators=[MinLengthValidator(4)],
        help_text=_("4-letter ICAO code"),
    )

    # Location
    city_name = models.CharField(
        _("city name"),
        max_length=100,
        blank=True,
        help_text=_("City name from OpenFlights"),
    )
    country_name = models.CharField(
        _("country name"),
        max_length=100,
        blank=True,
        db_index=True,
        help_text=_("Country name from OpenFlights"),
    )

    # Geometry
    location = gis_models.PointField(
        _("location"),
        srid=4326,
        null=True,
        blank=True,
        help_text=_("Geographic coordinates (WGS 84)"),
    )
    latitude = models.FloatField(
        _("latitude"),
        null=True,
        blank=True,
    )
    longitude = models.FloatField(
        _("longitude"),
        null=True,
        blank=True,
    )
    altitude = models.FloatField(
        _("altitude"),
        default=0,
        help_text=_("Altitude in meters"),
    )

    # Timezone
    timezone = models.CharField(
        _("timezone"),
        max_length=50,
        blank=True,
        help_text=_("IANA timezone name"),
    )
    timezone_offset = models.FloatField(
        _("timezone offset"),
        null=True,
        blank=True,
        help_text=_("Hours offset from UTC"),
    )
    dst = models.CharField(
        _("DST"),
        max_length=1,
        blank=True,
        help_text=_("Daylight savings time zone"),
    )

    # Source tracking
    source = models.CharField(
        _("data source"),
        max_length=50,
        blank=True,
        help_text=_("OurAirports, Legacy, User, etc."),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        if self.iata:
            return f"{self.name} ({self.iata})"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from .util import slugify

            base_slug = slugify(self.name)
            if self.iata:
                self.slug = f"{base_slug}-{self.iata.lower()}"
            else:
                self.slug = base_slug or str(self.openflights_id)
        super().save(*args, **kwargs)


class Airport(TransportHub):
    """
    Airport model.

    Includes international airports, regional airports, and airfields.
    """

    class Meta(TransportHub.Meta):
        verbose_name = _("airport")
        verbose_name_plural = _("airports")


class TrainStation(TransportHub):
    """
    Train station model.

    Rail stations with IATA codes (primarily European high-speed rail).
    """

    class Meta(TransportHub.Meta):
        verbose_name = _("train station")
        verbose_name_plural = _("train stations")


class Port(TransportHub):
    """
    Port/ferry terminal model.

    Ferry terminals and ports with IATA codes.
    """

    class Meta(TransportHub.Meta):
        verbose_name = _("port")
        verbose_name_plural = _("ports")


class Airline(models.Model):
    """
    Airline model.

    Contains airline identification codes and operational status.
    """

    # OpenFlights identifier
    openflights_id = models.PositiveIntegerField(
        _("OpenFlights ID"),
        unique=True,
        help_text=_("Unique identifier from OpenFlights database"),
    )

    # Basic info
    name = models.CharField(
        _("name"),
        max_length=200,
        db_index=True,
    )
    alias = models.CharField(
        _("alias"),
        max_length=200,
        blank=True,
        help_text=_("Alternative name or abbreviation"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=200,
        blank=True,
    )

    # Codes
    iata = models.CharField(
        _("IATA code"),
        max_length=3,
        blank=True,
        db_index=True,
        help_text=_("2-letter IATA code"),
    )
    icao = models.CharField(
        _("ICAO code"),
        max_length=4,
        blank=True,
        db_index=True,
        help_text=_("3-letter ICAO code"),
    )
    callsign = models.CharField(
        _("callsign"),
        max_length=50,
        blank=True,
        help_text=_("Radio callsign"),
    )

    # Location
    country_name = models.CharField(
        _("country"),
        max_length=100,
        blank=True,
        db_index=True,
    )

    # Status
    is_active = models.BooleanField(
        _("active"),
        default=True,
        db_index=True,
        help_text=_("Whether airline is currently operating"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("airline")
        verbose_name_plural = _("airlines")
        ordering = ["name"]

    def __str__(self):
        if self.iata:
            return f"{self.name} ({self.iata})"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from .util import slugify

            base_slug = slugify(self.name)
            if self.iata:
                self.slug = f"{base_slug}-{self.iata.lower()}"
            else:
                self.slug = base_slug or str(self.openflights_id)
        super().save(*args, **kwargs)


class Aircraft(models.Model):
    """
    Aircraft type model.

    Contains aircraft type codes and names.
    """

    # Basic info
    name = models.CharField(
        _("name"),
        max_length=200,
        db_index=True,
        help_text=_("Full aircraft name including manufacturer"),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=200,
        blank=True,
    )

    # Codes
    iata = models.CharField(
        _("IATA code"),
        max_length=4,
        blank=True,
        db_index=True,
        unique=True,
        help_text=_("IATA aircraft type code"),
    )
    icao = models.CharField(
        _("ICAO code"),
        max_length=4,
        blank=True,
        db_index=True,
        help_text=_("ICAO aircraft type designator"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("aircraft")
        verbose_name_plural = _("aircraft")
        ordering = ["name"]

    def __str__(self):
        if self.iata:
            return f"{self.name} ({self.iata})"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from .util import slugify

            self.slug = slugify(self.name) or self.iata or "unknown"
        super().save(*args, **kwargs)
