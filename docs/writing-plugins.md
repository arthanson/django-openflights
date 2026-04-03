---
layout: default
title: Writing Plugins
nav_order: 7
---

# Writing Plugins

Customize the import process with plugins.

## Plugin Structure

```python
# myapp/plugins.py
from openflights.exceptions import HookException

class MyPlugin:
    def airport_pre(self, command, item):
        """Before parsing each airport."""
        pass

    def airport_post(self, command, obj, item):
        """After saving each airport."""
        pass
```

## Registration

```python
# settings.py
OPENFLIGHTS_PLUGINS = ['myapp.plugins.MyPlugin']
```

## Available Hooks

| Hook | Description |
|------|-------------|
| `airport_pre(command, item)` | Before parsing airport/station/port |
| `airport_post(command, obj, item)` | After saving airport/station/port |
| `airline_pre(command, item)` | Before parsing airline |
| `airline_post(command, obj, item)` | After saving airline |
| `aircraft_pre(command, item)` | Before parsing aircraft |
| `aircraft_post(command, obj, item)` | After saving aircraft |

## Skipping Records

Raise `HookException` to skip a record:

```python
from openflights.exceptions import HookException

class FilterPlugin:
    def airport_pre(self, command, item):
        # Skip airports without IATA code
        if not item.get('iata'):
            raise HookException("No IATA code")
```

## Example: Country Filter

```python
class USOnlyPlugin:
    ALLOWED = {'United States', 'Canada', 'Mexico'}

    def airport_pre(self, command, item):
        country = item.get('country')
        if country and country not in self.ALLOWED:
            raise HookException(f"Skipping {country}")
```

## Example: Logging

```python
import logging

class LoggingPlugin:
    def __init__(self):
        self.logger = logging.getLogger('openflights.import')
        self.counts = {}

    def airport_post(self, command, obj, item):
        country = obj.country_name
        self.counts[country] = self.counts.get(country, 0) + 1

        total = sum(self.counts.values())
        if total % 1000 == 0:
            self.logger.info("Imported %d airports", total)
```
