"""Initial migration for OpenFlights models."""

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Airport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "openflights_id",
                    models.PositiveIntegerField(
                        help_text="Unique identifier from OpenFlights database",
                        unique=True,
                        verbose_name="OpenFlights ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="name"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=200, verbose_name="slug"),
                ),
                (
                    "iata",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="3-letter IATA/FAA code",
                        max_length=3,
                        validators=[django.core.validators.MinLengthValidator(3)],
                        verbose_name="IATA code",
                    ),
                ),
                (
                    "icao",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="4-letter ICAO code",
                        max_length=4,
                        validators=[django.core.validators.MinLengthValidator(4)],
                        verbose_name="ICAO code",
                    ),
                ),
                (
                    "city_name",
                    models.CharField(
                        blank=True,
                        help_text="City name from OpenFlights",
                        max_length=100,
                        verbose_name="city name",
                    ),
                ),
                (
                    "country_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="Country name from OpenFlights",
                        max_length=100,
                        verbose_name="country name",
                    ),
                ),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        help_text="Geographic coordinates (WGS 84)",
                        null=True,
                        srid=4326,
                        verbose_name="location",
                    ),
                ),
                (
                    "latitude",
                    models.FloatField(blank=True, null=True, verbose_name="latitude"),
                ),
                (
                    "longitude",
                    models.FloatField(blank=True, null=True, verbose_name="longitude"),
                ),
                (
                    "altitude",
                    models.FloatField(
                        default=0,
                        help_text="Altitude in meters",
                        verbose_name="altitude",
                    ),
                ),
                (
                    "timezone",
                    models.CharField(
                        blank=True,
                        help_text="IANA timezone name",
                        max_length=50,
                        verbose_name="timezone",
                    ),
                ),
                (
                    "timezone_offset",
                    models.FloatField(
                        blank=True,
                        help_text="Hours offset from UTC",
                        null=True,
                        verbose_name="timezone offset",
                    ),
                ),
                (
                    "dst",
                    models.CharField(
                        blank=True,
                        help_text="Daylight savings time zone",
                        max_length=1,
                        verbose_name="DST",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        help_text="OurAirports, Legacy, User, etc.",
                        max_length=50,
                        verbose_name="data source",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "airport",
                "verbose_name_plural": "airports",
                "ordering": ["name"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TrainStation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "openflights_id",
                    models.PositiveIntegerField(
                        help_text="Unique identifier from OpenFlights database",
                        unique=True,
                        verbose_name="OpenFlights ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="name"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=200, verbose_name="slug"),
                ),
                (
                    "iata",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="3-letter IATA/FAA code",
                        max_length=3,
                        validators=[django.core.validators.MinLengthValidator(3)],
                        verbose_name="IATA code",
                    ),
                ),
                (
                    "icao",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="4-letter ICAO code",
                        max_length=4,
                        validators=[django.core.validators.MinLengthValidator(4)],
                        verbose_name="ICAO code",
                    ),
                ),
                (
                    "city_name",
                    models.CharField(
                        blank=True,
                        help_text="City name from OpenFlights",
                        max_length=100,
                        verbose_name="city name",
                    ),
                ),
                (
                    "country_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="Country name from OpenFlights",
                        max_length=100,
                        verbose_name="country name",
                    ),
                ),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        help_text="Geographic coordinates (WGS 84)",
                        null=True,
                        srid=4326,
                        verbose_name="location",
                    ),
                ),
                (
                    "latitude",
                    models.FloatField(blank=True, null=True, verbose_name="latitude"),
                ),
                (
                    "longitude",
                    models.FloatField(blank=True, null=True, verbose_name="longitude"),
                ),
                (
                    "altitude",
                    models.FloatField(
                        default=0,
                        help_text="Altitude in meters",
                        verbose_name="altitude",
                    ),
                ),
                (
                    "timezone",
                    models.CharField(
                        blank=True,
                        help_text="IANA timezone name",
                        max_length=50,
                        verbose_name="timezone",
                    ),
                ),
                (
                    "timezone_offset",
                    models.FloatField(
                        blank=True,
                        help_text="Hours offset from UTC",
                        null=True,
                        verbose_name="timezone offset",
                    ),
                ),
                (
                    "dst",
                    models.CharField(
                        blank=True,
                        help_text="Daylight savings time zone",
                        max_length=1,
                        verbose_name="DST",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        help_text="OurAirports, Legacy, User, etc.",
                        max_length=50,
                        verbose_name="data source",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "train station",
                "verbose_name_plural": "train stations",
                "ordering": ["name"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Port",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "openflights_id",
                    models.PositiveIntegerField(
                        help_text="Unique identifier from OpenFlights database",
                        unique=True,
                        verbose_name="OpenFlights ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="name"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=200, verbose_name="slug"),
                ),
                (
                    "iata",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="3-letter IATA/FAA code",
                        max_length=3,
                        validators=[django.core.validators.MinLengthValidator(3)],
                        verbose_name="IATA code",
                    ),
                ),
                (
                    "icao",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="4-letter ICAO code",
                        max_length=4,
                        validators=[django.core.validators.MinLengthValidator(4)],
                        verbose_name="ICAO code",
                    ),
                ),
                (
                    "city_name",
                    models.CharField(
                        blank=True,
                        help_text="City name from OpenFlights",
                        max_length=100,
                        verbose_name="city name",
                    ),
                ),
                (
                    "country_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="Country name from OpenFlights",
                        max_length=100,
                        verbose_name="country name",
                    ),
                ),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        help_text="Geographic coordinates (WGS 84)",
                        null=True,
                        srid=4326,
                        verbose_name="location",
                    ),
                ),
                (
                    "latitude",
                    models.FloatField(blank=True, null=True, verbose_name="latitude"),
                ),
                (
                    "longitude",
                    models.FloatField(blank=True, null=True, verbose_name="longitude"),
                ),
                (
                    "altitude",
                    models.FloatField(
                        default=0,
                        help_text="Altitude in meters",
                        verbose_name="altitude",
                    ),
                ),
                (
                    "timezone",
                    models.CharField(
                        blank=True,
                        help_text="IANA timezone name",
                        max_length=50,
                        verbose_name="timezone",
                    ),
                ),
                (
                    "timezone_offset",
                    models.FloatField(
                        blank=True,
                        help_text="Hours offset from UTC",
                        null=True,
                        verbose_name="timezone offset",
                    ),
                ),
                (
                    "dst",
                    models.CharField(
                        blank=True,
                        help_text="Daylight savings time zone",
                        max_length=1,
                        verbose_name="DST",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        help_text="OurAirports, Legacy, User, etc.",
                        max_length=50,
                        verbose_name="data source",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "port",
                "verbose_name_plural": "ports",
                "ordering": ["name"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Airline",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "openflights_id",
                    models.PositiveIntegerField(
                        help_text="Unique identifier from OpenFlights database",
                        unique=True,
                        verbose_name="OpenFlights ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="name"
                    ),
                ),
                (
                    "alias",
                    models.CharField(
                        blank=True,
                        help_text="Alternative name or abbreviation",
                        max_length=200,
                        verbose_name="alias",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=200, verbose_name="slug"),
                ),
                (
                    "iata",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="2-letter IATA code",
                        max_length=3,
                        verbose_name="IATA code",
                    ),
                ),
                (
                    "icao",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="3-letter ICAO code",
                        max_length=4,
                        verbose_name="ICAO code",
                    ),
                ),
                (
                    "callsign",
                    models.CharField(
                        blank=True,
                        help_text="Radio callsign",
                        max_length=50,
                        verbose_name="callsign",
                    ),
                ),
                (
                    "country_name",
                    models.CharField(
                        blank=True, db_index=True, max_length=100, verbose_name="country"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Whether airline is currently operating",
                        verbose_name="active",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "airline",
                "verbose_name_plural": "airlines",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Aircraft",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="Full aircraft name including manufacturer",
                        max_length=200,
                        verbose_name="name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=200, verbose_name="slug"),
                ),
                (
                    "iata",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="IATA aircraft type code",
                        max_length=4,
                        unique=True,
                        verbose_name="IATA code",
                    ),
                ),
                (
                    "icao",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="ICAO aircraft type designator",
                        max_length=4,
                        verbose_name="ICAO code",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "aircraft",
                "verbose_name_plural": "aircraft",
                "ordering": ["name"],
            },
        ),
    ]
