"""
Plugin system for OpenFlights import customization.

Plugins allow you to hook into the import process to:
- Filter records before import
- Modify data during import
- Add custom processing after import

Usage:
1. Create a plugin class with hook methods
2. Add the class path to OPENFLIGHTS_PLUGINS in Django settings

Example:
    # myapp/plugins.py
    from openflights.exceptions import HookException

    class MyPlugin:
        def airport_pre(self, command, item):
            '''Called before parsing each airport.

            Args:
                command: Management command instance
                item: Raw data dict from parser

            Raises:
                HookException: To skip this item
            '''
            # Skip airports without IATA code
            if not item.get("iata"):
                raise HookException("No IATA code")

        def airport_post(self, command, obj, item):
            '''Called after saving each airport.

            Args:
                command: Management command instance
                obj: Saved model instance
                item: Raw data dict
            '''
            pass

    # settings.py
    OPENFLIGHTS_PLUGINS = ["myapp.plugins.MyPlugin"]

Available Hooks:
    airport_pre(command, item) - Before parsing an airport/station/port
    airport_post(command, obj, item) - After saving an airport/station/port
    airline_pre(command, item) - Before parsing an airline
    airline_post(command, obj, item) - After saving an airline
    aircraft_pre(command, item) - Before parsing an aircraft
    aircraft_post(command, obj, item) - After saving an aircraft
"""

from ..exceptions import HookException

__all__ = ["HookException"]
