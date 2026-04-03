---
layout: default
title: Installation
nav_order: 2
---

# Installation

## Requirements

- Python 3.10+
- Django 4.2+
- PostgreSQL with PostGIS

## Install Package

```bash
pip install django-openflights
```

## Django Configuration

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.gis',
    'openflights',
]
```

Configure PostGIS database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'your_database',
        # ...
    }
}
```

## Run Migrations

```bash
python manage.py migrate openflights
```

## Verify Installation

```bash
python manage.py openflights --help
```

## Import Data

```bash
python manage.py openflights --import=all
```
