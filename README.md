# ESPHome-Guition-ESP32-S3-4848S040
Original credit goes to alaltitov (https://github.com/alaltitov/Guition-ESP32-S3-4848S040) who credited the original baseline for creativity.  I encourage you to view his latest project.  All the code in this repository have been drastically modified from the original solution.  There is only 30% of the authors original code.

Changes:
- New home screen interface
- 5-day Weather Forecast
- Upcoming calendar events
- Addition of HVAC widget
- Icon color changes based on HVAC, Air Conditioning or Thermostat state in Home Assistant
- Fan control
- Light additions
- Ability to add lights and fans quickly without significant code revision
- Support for multiple unique device deployment
- and much, much more

Installation:
- Download repository and copy into your /config/esphome directory
- Create a copy of main.yaml and name it as your new device name
- Edit the entity_ids within the copies yaml file

Other installation notes:
- You must enable the "Allow the device to perform Home Assistant actions." option in the ESPHome integration to Home Assistant to control devices.
- Install custom component for translations and covers for media player from here.
- You must add the following code to your homeassitant configuration.yaml file

 template:
   - trigger:
       - platform: time_pattern
         minutes: "/15"
       - platform: homeassistant
         event: start
     action:
       - action: calendar.get_events
         target:
           entity_id: calendar.yourcalendar
         data:
           start_date_time: "{{ now().isoformat() }}"
           duration:
             days: 30
         response_variable: agenda
       - variables:
           events: >
             {{ agenda['calendar.yourcalendar']['events']
                | selectattr('start', 'search', 'T')
                | list }}
     sensor:
       - name: "Calendar Upcoming Event 1"
         unique_id: calendar_upcoming_event_1
         state: "{{ events[0].summary if events | length > 0 else 'No event' }}"
         attributes:
           message:    "{{ events[0].summary if events | length > 0 else '' }}"
           start_time: "{{ events[0].start   if events | length > 0 else '' }}"
           end_time:   "{{ events[0].end     if events | length > 0 else '' }}"

       - name: "Calendar Upcoming Event 2"
         unique_id: calendar_upcoming_event_2
         state: "{{ events[1].summary if events | length > 1 else 'No event' }}"
         attributes:
           message:    "{{ events[1].summary if events | length > 1 else '' }}"
           start_time: "{{ events[1].start   if events | length > 1 else '' }}"
           end_time:   "{{ events[1].end     if events | length > 1 else '' }}"

       - name: "Calendar Upcoming Event 3"
         unique_id: calendar_upcoming_event_3
         state: "{{ events[2].summary if events | length > 2 else 'No event' }}"
         attributes:
           message:    "{{ events[2].summary if events | length > 2 else '' }}"
           start_time: "{{ events[2].start   if events | length > 2 else '' }}"
           end_time:   "{{ events[2].end     if events | length > 2 else '' }}"
