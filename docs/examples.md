---
layout: default
title: Examples
nav_order: 6
---

# Examples

## Basic Queries

### Find Airports

```python
from openflights.models import Airport

# By IATA code
sfo = Airport.objects.get(iata='SFO')
jfk = Airport.objects.get(iata='JFK')

# By country
us_airports = Airport.objects.filter(country_name='United States')

# By city
london_airports = Airport.objects.filter(city_name='London')

# Search by name
airports = Airport.objects.filter(name__icontains='international')
```

### Find Airlines

```python
from openflights.models import Airline

# Active airlines only
active = Airline.objects.filter(is_active=True)

# By country
us_airlines = Airline.objects.filter(
    country_name='United States',
    is_active=True
)

# By IATA code
united = Airline.objects.get(iata='UA')
```

## Spatial Queries

### Find Nearby Airports

```python
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from openflights.models import Airport

# San Francisco coordinates
point = Point(-122.4194, 37.7749, srid=4326)

# Find 10 nearest airports
nearby = Airport.objects.filter(
    location__isnull=False
).annotate(
    distance=Distance('location', point)
).order_by('distance')[:10]

for airport in nearby:
    print(f"{airport.iata}: {airport.name} - {airport.distance.km:.1f} km")
```

### Airports Within Distance

```python
from django.contrib.gis.measure import D

# Airports within 100km of point
nearby = Airport.objects.filter(
    location__distance_lte=(point, D(km=100))
)
```

### Airports in Bounding Box

```python
from django.contrib.gis.geos import Polygon

# Bay Area bounding box
bbox = Polygon.from_bbox((-122.6, 37.2, -121.8, 38.0))

bay_area = Airport.objects.filter(location__within=bbox)
```

## Aircraft Queries

```python
from openflights.models import Aircraft

# Find aircraft type
b737 = Aircraft.objects.get(iata='738')

# All Boeing aircraft
boeing = Aircraft.objects.filter(name__startswith='Boeing')
```

## Train Stations and Ports

```python
from openflights.models import TrainStation, Port

# French train stations
french_stations = TrainStation.objects.filter(
    country_name='France'
)

# Greek ferry ports
greek_ports = Port.objects.filter(country_name='Greece')
```
