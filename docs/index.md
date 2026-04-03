---
layout: default
title: Home
nav_order: 1
---

# django-openflights

A Django application for importing and managing [OpenFlights](https://openflights.org/) aviation data.

## Features

- **Transport Hubs**: Airports, train stations, and ferry ports
- **Airlines**: Airline codes and operational status
- **Aircraft**: Aircraft type codes and names
- **PostGIS Support**: Full geometry support for spatial queries
- **Plugin System**: Customizable import processing

**Note**: Route data is not included as OpenFlights no longer maintains route information.

## Compatibility

| Python | Django | Database |
|--------|--------|----------|
| 3.10+  | 4.2+   | PostgreSQL with PostGIS |
| 3.11+  | 5.0+   | |
| 3.12+  | 5.1+   | |

## Quick Start

```bash
pip install django-openflights
python manage.py migrate openflights
python manage.py openflights --import=all
```

## Documentation

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Importing Data](importing-data.md)
- [Models](models.md)
- [Examples](examples.md)
- [Writing Plugins](writing-plugins.md)

## Data Source

Data from [OpenFlights](https://openflights.org/data.php) under the [Open Database License](https://opendatacommons.org/licenses/odbl/1.0/).
