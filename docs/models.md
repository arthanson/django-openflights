---
layout: default
title: Models
nav_order: 5
---

# Models

## Transport Hubs

Three models share the `TransportHub` abstract base class:

### Airport

```python
from openflights.models import Airport

sfo = Airport.objects.get(iata='SFO')
```

### TrainStation

```python
from openflights.models import TrainStation

stations = TrainStation.objects.filter(country_name='France')
```

### Port

```python
from openflights.models import Port

ports = Port.objects.filter(country_name='Greece')
```

### Shared Fields

| Field | Type | Description |
|-------|------|-------------|
| `openflights_id` | Integer | OpenFlights unique ID |
| `name` | String(200) | Hub name |
| `slug` | Slug(200) | URL-friendly name |
| `iata` | String(3) | IATA/FAA code |
| `icao` | String(4) | ICAO code |
| `city_name` | String(100) | City name |
| `country_name` | String(100) | Country name |
| `location` | PointField | Geographic coordinates |
| `latitude` | Float | Latitude |
| `longitude` | Float | Longitude |
| `altitude` | Float | Altitude in meters |
| `timezone` | String(50) | IANA timezone |
| `timezone_offset` | Float | UTC offset hours |
| `dst` | String(1) | DST zone code |
| `source` | String(50) | Data source |

## Airline

```python
from openflights.models import Airline

ua = Airline.objects.get(iata='UA')
active = Airline.objects.filter(is_active=True)
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `openflights_id` | Integer | OpenFlights unique ID |
| `name` | String(200) | Airline name |
| `alias` | String(200) | Alternative name |
| `slug` | Slug(200) | URL-friendly name |
| `iata` | String(3) | 2-letter IATA code |
| `icao` | String(4) | 3-letter ICAO code |
| `callsign` | String(50) | Radio callsign |
| `country_name` | String(100) | Country of origin |
| `is_active` | Boolean | Currently operating |

## Aircraft

```python
from openflights.models import Aircraft

b737 = Aircraft.objects.get(iata='738')
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String(200) | Full aircraft name |
| `slug` | Slug(200) | URL-friendly name |
| `iata` | String(4) | IATA type code (unique) |
| `icao` | String(4) | ICAO type designator |

**Note**: Route data is not included as OpenFlights no longer maintains route information.
