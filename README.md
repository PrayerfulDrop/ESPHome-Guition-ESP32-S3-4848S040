# ESPHome-Guition-ESP32-S3-4848S040
Original credit goes to alaltitov (https://github.com/alaltitov/Guition-ESP32-S3-4848S040) who credited the original baseline for creativity.  I encourage you to view his latest project.  All the code in this repository have been drastically modified from the original solution.  There is only 30% of the authors original code.

Changes:
- New home screen interface
- 5-day Weather Forecast
- Upcoming calendar events
- Addition of HVAC widget (heating and cooling in one location)
- Icon color changes based on HVAC, Air Conditioning or Thermostat state in Home Assistant
- Fan controls
- Light controls
- Ability to add lights and fans quickly without significant code revision
- Support for multiple unique device deployments
- Color themes
- and much, much more

Installation:
- Download repository and copy into your /config/esphome directory
- Create a copy of main.yaml and name it as your new device name
- Edit the entity_ids within the copies yaml file

Other installation notes:
- You must enable the "Allow the device to perform Home Assistant actions." option in the ESPHome integration to Home Assistant to control devices.
- Install custom component for translations and covers for media player from https://github.com/alaltitov/homeassistant-display-tools"
- Add the code in the configuration.yaml into your homeassistant configuration.yaml template section.
