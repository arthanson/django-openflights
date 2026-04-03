# Changelog

## [0.1.0] - 2024-XX-XX

### Added

- Initial release
- Models:
  - `Airport` - Airports with IATA/ICAO codes and coordinates
  - `TrainStation` - Train stations with IATA codes
  - `Port` - Ferry terminals and ports
  - `Airline` - Airlines with codes and operational status
  - `Aircraft` - Aircraft type codes
- Management command: `openflights`
  - `--import=all,airport,airline,plane`
  - `--flush=all,airport,airline,plane`
  - `--force` to re-download data
  - `--dry-run` for testing
- Plugin system for import customization
- Django admin integration
- PostGIS geometry support

### Data Sources

- OpenFlights airports-extended.dat
- OpenFlights airlines.dat
- OpenFlights planes.dat

### Notes

- Route data is not included as OpenFlights no longer maintains route information
