"""
Django OpenFlights - Import and manage OpenFlights aviation data.

Provides models for airports, train stations, ports, airlines, and aircraft.
Data sourced from the OpenFlights database (https://openflights.org/data.php).

Note: Route data is not included as OpenFlights no longer maintains route information.

License: MIT
Data License: OpenFlights data is released under the Open Database License (ODbL).
"""

__version__ = "0.1.0"
__author__ = "Your Name"

default_app_config = "openflights.apps.OpenFlightsConfig"
