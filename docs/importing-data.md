---
layout: default
title: Importing Data
nav_order: 4
---

# Importing Data

## Basic Usage

```bash
# Import everything
python manage.py openflights --import=all

# Import specific types
python manage.py openflights --import=airport,airline
```

## Options

| Option | Description |
|--------|-------------|
| `--import=TYPE` | What to import: all, airport, airline, plane |
| `--flush=TYPE` | Delete existing data first |
| `--force` | Re-download data files |
| `--quiet` | Suppress progress output |
| `--dry-run` | Parse without saving |
| `--download-only` | Only download, don't import |
| `--list` | List cached data files |
| `--clear` | Clear download cache |

## Import Types

- `airport` - Airports, train stations, and ferry ports
- `airline` - Airlines
- `plane` - Aircraft types

**Note**: Route data is not available as OpenFlights no longer maintains it.

## Examples

```bash
# Fresh import (flush and reimport)
python manage.py openflights --flush=all --import=all

# Import airports only
python manage.py openflights --import=airport

# Import airlines and planes
python manage.py openflights --import=airline,plane

# Force re-download
python manage.py openflights --import=all --force

# Dry run to test
python manage.py openflights --import=airport --dry-run

# List cached files
python manage.py openflights --list
```

## Import Order

1. `airport` (includes train stations and ports)
2. `airline`
3. `plane`

Using `--import=all` handles this automatically.

## Data Statistics

After import:

```
Import complete!
  Processed: 14110
  Created:   14000
  Updated:   110
  Skipped:   500
  Errors:    0
```
