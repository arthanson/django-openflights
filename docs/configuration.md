---
layout: default
title: Configuration
nav_order: 3
---

# Configuration

All settings use the `OPENFLIGHTS_` prefix.

## Data Directory

```python
OPENFLIGHTS_DATA_DIR = '/path/to/data'
```

Default: `openflights/data/` within the package.

## Import Controls

Control what data types to import:

```python
OPENFLIGHTS_IMPORT_AIRPORTS = True   # Airports, train stations, ports
OPENFLIGHTS_IMPORT_AIRLINES = True   # Airlines
OPENFLIGHTS_IMPORT_PLANES = True     # Aircraft types
```

**Note**: Route data is not available as OpenFlights no longer maintains it.

## Geometry

Disable geometry for faster imports:

```python
OPENFLIGHTS_IMPORT_GEOMETRY = False
```

Default: `True`

## Performance

```python
OPENFLIGHTS_DOWNLOAD_TIMEOUT = 120   # Seconds
OPENFLIGHTS_MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB
OPENFLIGHTS_BATCH_SIZE = 1000
```

## Plugins

Register custom plugins:

```python
OPENFLIGHTS_PLUGINS = [
    'myapp.plugins.MyPlugin',
]
```

## Complete Example

```python
# settings.py

OPENFLIGHTS_DATA_DIR = '/var/data/openflights'
OPENFLIGHTS_IMPORT_AIRPORTS = True
OPENFLIGHTS_IMPORT_AIRLINES = True
OPENFLIGHTS_IMPORT_PLANES = True
OPENFLIGHTS_IMPORT_GEOMETRY = True
OPENFLIGHTS_BATCH_SIZE = 2000
```
