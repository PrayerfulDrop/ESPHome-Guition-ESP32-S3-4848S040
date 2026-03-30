# ESPHome · Guition ESP32-S3-4848S040
### A fully-featured smart home display — built on ESPHome + LVGL

---

## Overview

A complete, production-ready smart home dashboard for the **Guition ESP32-S3-4848S040** 480×480 touch display. Built on top of ESPHome and LVGL, this firmware turns the panel into a rich control centre for Home Assistant — with real-time weather, calendar, HVAC, lights with colour temperature, fans, covers/blinds, media player, vacuum, alarm, scene shortcuts, presence indicators, screensaver, and notification banners.

> Original credit: [alaltitov](https://github.com/alaltitov/Guition-ESP32-S3-4848S040).

---

## Features

| Category | Details |
|---|---|
| **Home screen** | Time (12h/24h), date, indoor temp (°F/°C), weather icon + title-cased condition, up to 4 upcoming calendar events |
| **Presence indicators** | Up to 4 person entities shown as initials in the top bar — green when home, dim when away; tap to open full People page |
| **People page** | Card per person showing avatar initials, full name from HA, and home/away status |
| **Screensaver** | Activates on idle — Digital clock, Flip clock (Gluqlo retro style), Calendar view, or None (screen off); tap anywhere to wake and return to home |
| **Notification banner** | Write any text to an `input_text` entity in HA — a toast banner appears for 10 s; tap to dismiss early |
| **Weather** | Current conditions with title-cased state + 5-day forecast with high/low temps and weather icons |
| **Calendar** | Up to 4 upcoming events pulled live from Home Assistant via template sensors |
| **HVAC** | Combined heating + cooling widget with arc temperature control; or separate thermostat / AC widgets |
| **Lights** | Up to 6 configurable slots (`light` / `switch` / `input_boolean`); brightness slider; auto-detected colour temperature slider |
| **Fans** | Up to 6 configurable fan slots (`fan` / `switch`) with speed control |
| **Covers** | Up to 6 cover/blind/shutter slots — position bar, Open/Stop/Close buttons, position slider |
| **Scene shortcuts** | Up to 6 scene/script/automation tiles with configurable labels |
| **Media Player** | Album art, track info, progress bar, playback controls, volume slider |
| **Vacuum** | Animated robot body, battery, state, start/pause/dock controls |
| **Alarm Panel** | Disarm / Home / Away / Night / Vacation modes with PIN entry |
| **Devices hub** | Navigation to Alarm, Media, Vacuum, HVAC, Fans, Shortcuts, and Covers |
| **Settings** | Language (9 languages), colour theme, 12h/24h clock, °F/°C unit, backlight brightness, auto-sleep timer, screensaver style |
| **Settings defaults** | Language: English (US) · Theme: Dark · Backlight: 100% · Sleep: 120 s · Clock: 12h · Temp: °F · Screensaver: Digital clock |
| **Themes** | 6 built-in themes: Cherry Blossom, Dark, Espeon, Ocean, Paris, Patriotic |
| **Navigation** | Persistent bottom nav bar (Home / Lights / Devices / Settings); entity detail pages hide the bar and show a back button |
| **Multi-device** | Copy `main.yaml` and rename — each file is a fully independent device |
| **OTA overlay** | Backlight dims smoothly during firmware uploads — no screen corruption or tearing |
| **Remote screenshot** | HTTP endpoint at `http://<device>.local/screenshot` returns a live BMP of the current screen; `/screenshot/info` returns JSON metadata |
| **Localisation** | Translations fetched live from Home Assistant for weather, HVAC, vacuum, alarm, and cover states |

---

## Widgets

| Alarm Panel | Media Player | Vacuum |
|:---:|:---:|:---:|
| ![Alarm Panel](screenshots/alarm_panel-widget.png) | ![Media Player](screenshots/mediaplayer-widget.png) | ![Vacuum](screenshots/vacuum-widget.png) |

| Devices Hub | Settings (1) | Settings (2) |
|:---:|:---:|:---:|
| ![Devices](screenshots/devices-widget.png) | ![Settings 1](screenshots/settings-widget1.png) | ![Settings 2](screenshots/settings-widget2.png) |

| 5-Day Weather Forecast | People |
|:---:|:---:|
| ![5-Day Weather](screenshots/5-day-weather.png) | ![People Widget](screenshots/people-widget.png) |

---

## Themes

6 built-in themes selectable from the Settings page:

| Cherry Blossom | Dark | Espeon |
|:---:|:---:|:---:|
| ![Cherry Blossom](screenshots/cherry-blossom-theme.png) | ![Dark](screenshots/dark-theme-home.png) | ![Espeon](screenshots/espeon-theme.png) |

| Ocean | Paris | Patriotic |
|:---:|:---:|:---:|
| ![Ocean](screenshots/ocean-theme.png) | ![Paris](screenshots/paris-theme.png) | ![Patriotic](screenshots/patriotic-theme.png) |

---

## Requirements

- **Hardware** — Guition ESP32-S3-4848S040 (480×480 capacitive touch display)
- **ESPHome** — 2024.6.0 or later
- **Home Assistant** — any recent version with the ESPHome integration
- **HA Custom Component** — [display-tools](https://github.com/alaltitov/homeassistant-display-tools) (required for translations and cover/media support)

---

## File Structure

```
/config/esphome/
├── Guition-ESP32/
│   ├── hardware.yaml           ← board-level config (display, touch, OTA, screensaver)
│   ├── widgets/                ← widget engine — do not edit
│   ├── fonts/
│   └── images/
├── main.yaml                   ← template — copy this for each device
├── configuration.yaml          ← HA template sensors (calendar events)
└── secrets.yaml                ← OTA password, WiFi, PIN code
```

`main.yaml` contains **only** the `substitutions:` block and `packages:` list.  All hardware and engine logic lives in `Guition-ESP32/`.

---

## Installation

### 1 · Copy files

Download or clone this repository into your ESPHome config directory so the folder structure matches the tree above.

### 2 · Create your device file

Copy `main.yaml` and rename it (e.g. `living-room.yaml`). **Edit only the `substitutions:` block** — everything below is the engine.

```yaml
substitutions:

  # ── 1 │ DEVICE ────────────────────────────────────────────────────
  esphome_name:          "living-room"          # hostname — lowercase, hyphens only
  esphome_friendly_name: "Living Room Display"
  ha_server:             "http://homeassistant.local:8123"
  time_zone:             "America/New_York"     # IANA tz name

  # ── 2 │ CORE ENTITIES ─────────────────────────────────────────────
  notification_entity: "input_text.display_notification"
  weather_entity:      "weather.forecast_home"
  temperature_entity:  "sensor.living_room_temperature"
  vacuum_entity:       "vacuum.roomba"
  media_player_entity: "media_player.living_room"
  alarm_panel_entity:  "alarm_control_panel.system"
  pin_code:            !secret security_pin_code

  # ── 3 │ PRESENCE  (up to 4) ───────────────────────────────────────
  person_entity_1:   "person.yourname"
  person_initials_1: "A"
  # unused → person_entity_N: "sensor.disabled"

  # ── LIGHTS / FANS / COVERS — see main.yaml for full slot options ──
```

### 3 · Home Assistant setup

**a) Enable device actions**
In the ESPHome integration, open the device page and enable *"Allow the device to perform Home Assistant actions"*.

**b) Install display-tools**
Add [alaltitov/homeassistant-display-tools](https://github.com/alaltitov/homeassistant-display-tools) via HACS or manually to your HA instance.

**c) Add calendar template sensors**
Copy the contents of `configuration.yaml` (included in this repo) into your Home Assistant `configuration.yaml`, then restart HA.  Replace every occurrence of `calendar.yourcalendar_calendar` with your actual calendar entity ID (HA calendar entity IDs typically end in `_calendar`).

```yaml
template:
  - trigger:
      - platform: time_pattern
        minutes: "/15"
      - platform: homeassistant
        event: start
    action:
      - action: calendar.get_events
        target:
          entity_id: calendar.yourcalendar_calendar          # ← change this
        data:
          start_date_time: "{{ now().isoformat() }}"
          duration:
            days: 30
        response_variable: agenda
      - variables:
          events: >
            {{ agenda['calendar.yourcalendar_calendar']['events']
               | rejectattr('start', 'match', '^\d{4}-\d{2}-\d{2}$')
               | sort(attribute='start')
               | list }}
          e1_summary: "{{ events[0].summary if events | length > 0 else 'No event' }}"
          e1_start:   "{{ events[0].start | as_datetime | as_local | as_timestamp | timestamp_custom('%Y-%m-%d %H:%M:%S') if events | length > 0 else '' }}"
          e1_end:     "{{ events[0].end   | as_datetime | as_local | as_timestamp | timestamp_custom('%Y-%m-%d %H:%M:%S') if events | length > 0 else '' }}"
          # e2, e3, e4 follow the same pattern — see configuration.yaml
    sensor:
      - name: "Calendar Upcoming Event 1"
        unique_id: calendar_upcoming_event_1
        state: "{{ e1_summary }}"
        attributes:
          message:    "{{ e1_summary }}"
          start_time: "{{ e1_start }}"
          end_time:   "{{ e1_end }}"
      # repeat for events 2, 3, 4 — see configuration.yaml
```

> **Timezone note:** Event times are converted to your local timezone using `as_local` before formatting. No UTC conversion is needed — HA handles the local offset automatically.

Then set the calendar entities in your device file:

```yaml
  calendar_entity:   "sensor.calendar_upcoming_event_1"
  calendar_entity_2: "sensor.calendar_upcoming_event_2"
  calendar_entity_3: "sensor.calendar_upcoming_event_3"
  calendar_entity_4: "sensor.calendar_upcoming_event_4"
```

**d) Create the notification helper**
- Go to **Settings → Devices & Services → Helpers → Create Helper → Text**
- Name: `display_notification` (entity ID: `input_text.display_notification`)
- Leave max length at the default (100)
- Trigger notifications from automations via `input_text.set_value`; the banner dismisses after 10 s or when tapped

**e) Add secrets**

```yaml
# secrets.yaml
display_ota: "your-ota-password"
wifi_ssid:   "YourWiFi"
wifi_password: "YourPassword"
security_pin_code: "1234"
```

### 4 · Flash

```bash
esphome run living-room.yaml
```

---

## HVAC Options

![HVAC Widget](screenshots/hvac-widget.png)

Uncomment the block that matches your system in both the `substitutions:` section and the `packages:` section of your device file:

| Option | Use when… | packages key |
|---|---|---|
| **Option 1** (default) | Single HA `climate` entity handles heat + cool | `hvac: hvac_widget.yaml` |
| **Option 2** | Thermostat only (heat) | `hvac: thermostat_widget.yaml` |
| **Option 3** | Air conditioner only (cool) | `hvac: air_conditioner_widget.yaml` |
| **Option 4** | Separate thermostat + AC entities | `thermostat:` + `ac:` + `devices: devices_thermostat_ac.yaml` |

---

## Lights, Fans & Covers

| Lights | Fans | Covers |
|:---:|:---:|:---:|
| ![Lights Widget](screenshots/lights-widget.png) | ![Fan Widget](screenshots/fan-widget.png) | ![Covers Widget](screenshots/covers-widget.png) |

Up to **6 lights**, **6 fans**, and **6 covers** can be configured. Set unused slots to `sensor.disabled`.

```yaml
# Light slot
light_entity_1:     "light.living_room"
light_label_name_1: "Living Room"
light_type_1:       "light"          # light | switch | input_boolean
light_icon_1:       "ceiling_lamp"   # ceiling_lamp | ceiling_lamp_variant | night_lamp
                                     # lightbulb | spotlights_group | desk_lamp
                                     # pendant_lamp | bed | heart | tv

# Fan slot
fan_entity_1:     "fan.ceiling_fan"
fan_label_name_1: "Ceiling Fan"
fan_type_1:       "fan"              # fan | switch | input_boolean
fan_icon_1:       "ceiling_fan"      # ceiling_fan | floor_fan

# Cover slot
cover_entity_1:     "cover.living_room_blinds"
cover_label_name_1: "Living Room"
```

The light detail page automatically shows a colour temperature slider the first time HA sends a `color_temp` attribute.

---

## Presence & People

![People Widget](screenshots/people-widget.png)

Up to 4 person entities are tracked in real time.  Initials appear in the top indicator bar coloured green when home and dim when away.  Tapping the indicator bar opens the People page, which shows a card per person with:

- **Avatar circle** with initials (coloured green when home)
- **Full name** fetched automatically from the HA `friendly_name` attribute
- **Status dot + label** (Home / Away)

Cards for `sensor.disabled` slots are hidden automatically.

```yaml
person_entity_1:   "person.yourname"
person_initials_1: "A"               # shown in the top bar + on the avatar

person_entity_2:   "person.partner"
person_initials_2: "K"

# Unused slots
person_entity_3:   "sensor.disabled"
person_initials_3: ""
```

---

## Weather

![5-Day Weather Forecast](screenshots/5-day-weather.png)

Displays current conditions with a title-cased state and a **5-day forecast** showing high/low temperatures and weather icons. Set the `weather_entity` substitution to your Home Assistant weather entity (e.g. `weather.forecast_home`).

---

## Screensaver

![Screensaver Clock](screenshots/screensaver-clock.png)

Four screensaver styles are available, selectable from **Settings → Screensaver** (the Analog clock style has been replaced by the Flip Clock):

| Style | Behaviour |
|---|---|
| **Digital** (default) | Large digital clock + date |
| **Flip Clock** | Retro Gluqlo-style flip clock — hour and minute panels with date below |
| **Calendar** | Digital clock + next 3 upcoming events |
| **None** | Screen dims to near-off (backlight ~1%) |

- The screensaver activates after the configured idle timeout (default **120 s**)
- **Digital / Flip Clock / Calendar**: display stays at normal brightness showing the selected clock
- **None**: backlight dims to ~1% — the screen is effectively off but touch still works
- Tapping anywhere dismisses the screensaver, restores backlight to the saved brightness level, and navigates directly to the **Home** page

---

## Notifications

Write any text to the configured `input_text` entity from a HA automation:

```yaml
- action: input_text.set_value
  target:
    entity_id: input_text.display_notification
  data:
    value: "Front door open"
```

The banner appears at the bottom of the screen for 10 seconds then auto-dismisses. Tap the banner to dismiss early. Setting the entity value to an empty string also clears it. Blank, `unknown`, and `unavailable` states are ignored.

---

## Remote Screenshot

The `display_capture` external component exposes two HTTP endpoints on the device's built-in web server:

| Endpoint | Method | Description |
|---|---|---|
| `/screenshot` | GET | Returns a BMP image of the current screen |
| `/screenshot?page=N` | GET | Switches to page N, captures, then restores |
| `/screenshot/info` | GET | Returns JSON metadata (width, height, page count, mode) |

**Requirements** — add these to `hardware.yaml` (already included in this repo):

```yaml
web_server:
  port: 80

external_components:
  - source:
      type: local
      path: Guition-ESP32/components
    components: [display_capture]

display_capture:
  display_id: my_display
  backend: st7701s
```

**Usage:**

```bash
# Save a screenshot to disk
curl http://living-room.local/screenshot --output screen.bmp

# Get display info
curl http://living-room.local/screenshot/info
# → {"width":480,"height":480,"pages":1,"mode":"single"}
```

The component reads the framebuffer directly from the ESP-IDF RGB panel driver (`esp_lcd_rgb_panel_get_frame_buffer`) — no display redraw or flicker occurs during capture.

---

## Settings Defaults

| Setting | Default |
|---|---|
| Language | English (US) |
| Theme | Dark |
| Backlight | 100% |
| Sleep mode | 120 s |
| Clock format | 12h (AM/PM) |
| Temperature unit | °F |
| Screensaver | Digital |

All settings are persisted across reboots via NVS flash storage.

---

## 3D Print Stand

A desk stand for this display is available on MakerWorld:
[Guition ESP32-S3 4848S040 Desk Stand](https://makerworld.com/en/models/1587503-guition-esp32-se-4848s040-desk-stand#profileId-1671461)

---

## Credits

- Original project: [alaltitov/Guition-ESP32-S3-4848S040](https://github.com/alaltitov/Guition-ESP32-S3-4848S040)
- Built with [ESPHome](https://esphome.io) and [LVGL](https://lvgl.io)
