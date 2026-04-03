# django-openflights

A Django application for importing and managing [OpenFlights](https://openflights.org/) aviation data.

Provides models for airports, train stations, ferry ports, airlines, and aircraft types.

## Features

- **Transport Hubs**: Airports, train stations, and ferry ports with coordinates and codes
- **Airlines**: Airline information with IATA/ICAO codes and operational status
- **Aircraft**: Aircraft type codes and names
- **PostGIS Support**: Full geometry support for spatial queries
- **Extensible**: Plugin system for custom import processing

**Note**: Route data is not included as OpenFlights no longer maintains route information.

## Compatibility

| Python | Django | Database |
|--------|--------|----------|
| 3.10+  | 4.2+   | PostgreSQL with PostGIS |
| 3.11+  | 5.0+   | |
| 3.12+  | 5.1+   | |

## Quick Start

```bash
# Install
pip install django-openflights

# Add to INSTALLED_APPS
# 'django.contrib.gis',
# 'openflights',

# Run migrations
python manage.py migrate openflights

# Import all data
python manage.py openflights --import=all
```

## Installation

```bash
pip install django-openflights
```

Add to your Django settings:

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.gis',
    'openflights',
]
```

Run migrations:

```bash
python manage.py migrate openflights
```

## Usage

### Import Data

```bash
# Import everything
python manage.py openflights --import=all

# Import specific data types
python manage.py openflights --import=airport,airline

# Import airports only (includes train stations and ports)
python manage.py openflights --import=airport

# Force re-download
python manage.py openflights --import=all --force

# Flush existing data before import
python manage.py openflights --flush=all --import=all
```

### Query Data

```python
from openflights.models import Airport, Airline

# Find airports by IATA code
sfo = Airport.objects.get(iata='SFO')
jfk = Airport.objects.get(iata='JFK')

# Find airports in a country
us_airports = Airport.objects.filter(country_name='United States')

# Find active airlines
active_airlines = Airline.objects.filter(is_active=True)
```

### Spatial Queries

```python
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

# Find airports near a point
point = Point(-122.4194, 37.7749, srid=4326)
nearby = Airport.objects.filter(
    location__isnull=False
).annotate(
    distance=Distance('location', point)
).order_by('distance')[:10]
```

## Models

### Airport / TrainStation / Port

Transport hub models with shared fields:

| Field | Type | Description |
|-------|------|-------------|
| `openflights_id` | Integer | OpenFlights unique ID |
| `name` | String | Hub name |
| `iata` | String | 3-letter IATA code |
| `icao` | String | 4-letter ICAO code |
| `location` | Point | Geographic coordinates |
| `altitude` | Float | Altitude in meters |
| `city_name` | String | City name |
| `country_name` | String | Country name |
| `timezone` | String | IANA timezone |

### Airline

| Field | Type | Description |
|-------|------|-------------|
| `openflights_id` | Integer | OpenFlights unique ID |
| `name` | String | Airline name |
| `iata` | String | 2-letter IATA code |
| `icao` | String | 3-letter ICAO code |
| `callsign` | String | Radio callsign |
| `country_name` | String | Country of origin |
| `is_active` | Boolean | Currently operating |

### Aircraft

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Full aircraft name |
| `iata` | String | IATA type code |
| `icao` | String | ICAO type designator |

## Configuration

```python
# Data directory for downloads
OPENFLIGHTS_DATA_DIR = '/path/to/data'

# What to import by default
OPENFLIGHTS_IMPORT_AIRPORTS = True
OPENFLIGHTS_IMPORT_AIRLINES = True
OPENFLIGHTS_IMPORT_PLANES = True

# Import geometry (disable for faster imports)
OPENFLIGHTS_IMPORT_GEOMETRY = True

# Custom plugins
OPENFLIGHTS_PLUGINS = ['myapp.plugins.MyPlugin']
```

## Data Source

Data is sourced from [OpenFlights](https://openflights.org/data.php), which provides:
- ~14,000+ airports, train stations, and ferry terminals
- ~6,000+ airlines
- ~300+ aircraft types

**Note**: Route data was previously available but is no longer maintained by OpenFlights.

OpenFlights data is released under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/1.0/).

## Disclaimer

This project is not affiliated with, endorsed by, or associated with [OpenFlights](https://openflights.org/) or its maintainers. It is an independent, third-party Django integration that consumes publicly available OpenFlights data.

## License

MIT License

## Links

- [GitHub Repository](https://github.com/arthanson/django-openflights)
- [OpenFlights](https://openflights.org/)
- [OpenFlights Data](https://openflights.org/data.php)
