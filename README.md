# ESPHome · Guition ESP32-S3-4848S040
### A fully-featured smart home display — built on ESPHome + LVGL

---

## Overview

A complete, production-ready smart home dashboard for the **Guition ESP32-S3-4848S040** 480×480 touch display. Built on top of ESPHome and LVGL, this firmware turns the panel into a rich control center for Home Assistant — with real-time weather, calendar, HVAC, lights with colour temperature, fans, covers/blinds, media, vacuum, alarm, scene shortcuts, presence indicators, screensaver, and notification banners.

> Original credit: [alaltitov](https://github.com/alaltitov/Guition-ESP32-S3-4848S040).

---

## Features

| Category | Details |
|---|---|
| **Home screen** | Time (12h/24h), date, indoor temp (°F/°C), weather icon + condition, upcoming calendar events |
| **Presence indicators** | Up to 4 person entities shown as initials in the top bar — green when home, dim when away |
| **Screensaver** | Minimal floating clock activates on idle; tap anywhere to wake |
| **Notification banner** | Write any text to an `input_text` entity in HA — a toast banner appears on screen for 10 s |
| **Weather** | Current conditions + 5-day forecast with high/low temps and weather icons |
| **Calendar** | Up to 4 upcoming events pulled live from Home Assistant |
| **HVAC** | Combined heating + cooling widget with arc temperature control; or separate thermostat / AC widgets |
| **Lights** | Up to 6 configurable slots (light / switch / input_boolean); brightness slider; auto-detected colour temperature slider |
| **Fans** | Up to 6 configurable fan slots with speed control |
| **Covers** | Up to 6 cover/blind/shutter slots — position bar, Open/Stop/Close buttons, position slider |
| **Scene shortcuts** | Up to 6 scene/script/automation tiles with configurable labels |
| **Media Player** | Album art, track info, progress bar, playback controls, volume slider |
| **Vacuum** | Animated robot body, battery, state, start/pause/dock controls |
| **Alarm Panel** | Disarm / Home / Away / Night / Vacation modes with PIN entry |
| **Devices hub** | Navigation to Alarm, Media, Vacuum, HVAC, Fans, Shortcuts, and Covers |
| **Settings** | Language selector (9 languages), colour theme picker, 12h/24h clock, °F/°C unit, backlight brightness, auto-sleep timer |
| **Themes** | 6 built-in themes: Cherry Blossom, Dark, Espeon, Ocean, Paris, Patriotic |
| **Multi-device** | Copy `main.yaml` and rename — each file is a fully independent device |
| **OTA overlay** | On-screen progress bar and status during firmware updates |
| **Localisation** | Translations fetched live from Home Assistant for weather, HVAC, vacuum, alarm, and cover states |

---

## Themes

6 built-in themes selectable from the Settings page: **Cherry Blossom**, **Dark**, **Espeon**, **Ocean**, **Paris**, **Patriotic**.

---

## Requirements

- **Hardware** — Guition ESP32-S3-4848S040 (480×480 capacitive touch display)
- **ESPHome** — 2024.6.0 or later
- **Home Assistant** — any recent version with the ESPHome integration
- **HA Custom Component** — [display-tools](https://github.com/alaltitov/homeassistant-display-tools) (required for translations and cover/media support)

---

## Installation

### 1 · Copy files

Download or clone this repository into your ESPHome config directory:

```
/config/esphome/
├── Guition-ESP32/          ← widget engine (do not edit)
├── main.yaml               ← template — copy this for each device
└── configuration.yaml      ← HA template sensors to paste into Home Assistant
```

### 2 · Create your device file

Copy `main.yaml` and rename it to your device (e.g. `living-room.yaml`).
**Edit only the `substitutions:` block at the top** — everything below is the engine.

```yaml
substitutions:

  # ── 1 │ DEVICE ────────────────────────────────────────────────
  esphome_name:          "living-room"
  esphome_friendly_name: "Living Room Display"
  ha_server:             "http://homeassistant.local:8123"
  time_zone:             "America/New_York"

  # ── 2 │ CORE ENTITIES ─────────────────────────────────────────
  weather_entity:      "weather.forecast_home"
  temperature_entity:  "sensor.living_room_temperature"
  ...
```

### 3 · Home Assistant setup

1. **Enable device actions** — In the ESPHome integration, open the device and enable
   *"Allow the device to perform Home Assistant actions"*

2. **Install display-tools** — Add [alaltitov/homeassistant-display-tools](https://github.com/alaltitov/homeassistant-display-tools) via HACS or manually

3. **Add template sensors** — Paste the contents of `configuration.yaml` into your Home Assistant `configuration.yaml` under the `template:` section and restart HA

4. **Create the notification helper** — The notification banner requires an `input_text` helper in Home Assistant:
   - Go to **Settings → Devices & Services → Helpers → Create Helper → Text**
   - Set the name to `display_notification` (entity ID will become `input_text.display_notification`)
   - Leave max length at the default (100) and save
   - Reference this entity in your device file as `notification_entity: "input_text.display_notification"`
   - Trigger notifications from HA automations by calling the `input_text.set_value` service on this entity

### 4 · Flash

Compile and flash from the ESPHome dashboard or CLI:

```bash
esphome run living-room.yaml
```

---

## HVAC Options

Pick the configuration that matches your system by uncommenting the correct block in your device file:

| Option | Use when… |
|---|---|
| **Option 1** (default) | Single HA climate entity handles both heat and cool |
| **Option 2** | Thermostat only (heat) |
| **Option 3** | Air conditioner only (cool) |
| **Option 4** | Separate thermostat + AC entities |

---

## Light, Fan & Cover Slots

Up to **6 lights**, **6 fans**, and **6 covers** can be configured. Set unused slots to `sensor.disabled`:

```yaml
# Lights
light_entity_1:     "light.living_room"
light_label_name_1: "Living Room"
light_type_1:       "light"          # light | switch | input_boolean
light_icon_1:       "ceiling_lamp"   # ceiling_lamp | night_lamp | bed | tv | …

# Covers / blinds
cover_entity_1:     "cover.living_room_blinds"
cover_label_name_1: "Living Room"
```

The light detail page automatically detects colour temperature support — the colour temp slider appears the first time HA sends a `color_temp` attribute value.

---

## Presence, Notifications & Shortcuts

```yaml
# Up to 4 person entities — shown as initials in the top bar
person_entity_1:   "person.yourname"
person_initials_1: "A"

# Notification banner — write text to this entity from HA automations
notification_entity: "input_text.display_notification"

# Up to 6 scene/script/automation shortcuts
scene_entity_1:  "scene.movie_night"
scene_label_1:   "Movie Night"
scene_type_1:    "scene"           # scene | script | automation
```

---

## 3D Print Stand

A desk stand for this display is available on MakerWorld:
[Guition ESP32-S3 4848S040 Desk Stand](https://makerworld.com/en/models/1587503-guition-esp32-se-4848s040-desk-stand#profileId-1671461)

---

## Credits

- Original project: [alaltitov/Guition-ESP32-S3-4848S040](https://github.com/alaltitov/Guition-ESP32-S3-4848S040)
- Built with [ESPHome](https://esphome.io) and [LVGL](https://lvgl.io)
