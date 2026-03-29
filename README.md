# ESPHome · Guition ESP32-S3-4848S040
### A fully-featured smart home display — built on ESPHome + LVGL

---

## Overview

A complete, production-ready smart home dashboard for the **Guition ESP32-S3-4848S040** 480×480 touch display. Built on top of ESPHome and LVGL, this firmware turns the panel into a rich control center for Home Assistant — with real-time weather, calendar, HVAC, lights, fans, media, vacuum, alarm, and more.

> Original baseline credit: [alaltitov](https://github.com/alaltitov/Guition-ESP32-S3-4848S040).
> This repository is a major fork — approximately 70% of the code has been rewritten or added from scratch.

---

## Features

| Category | Details |
|---|---|
| **Home screen** | Time, date, indoor temperature, weather icon + condition, upcoming calendar events |
| **Weather** | Current conditions + 5-day forecast with high/low temps and weather icons |
| **Calendar** | Up to 4 upcoming events pulled live from Home Assistant |
| **HVAC** | Combined heating + cooling widget with arc temperature control; or separate thermostat / AC widgets |
| **Lights** | Up to 6 configurable light slots (light, switch, or input_boolean); icon reflects on/off state |
| **Fans** | Up to 6 configurable fan slots with speed control |
| **Media Player** | Album art, track info, progress bar, playback controls, volume slider |
| **Vacuum** | Animated robot body, battery, state, start/pause/dock controls |
| **Alarm Panel** | Disarm / Home / Away / Night / Vacation modes with PIN entry |
| **Devices hub** | Single-tap navigation to Alarm, Media, Vacuum, HVAC, and Fans |
| **Settings** | Language selector (9 languages), colour theme picker, backlight brightness, auto-sleep timer |
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

## Light & Fan Slots

Up to **6 lights** and **6 fans** can be configured. Set unused slots to `sensor.disabled`:

```yaml
light_entity_1:     "light.living_room"
light_label_name_1: "Living Room"
light_type_1:       "light"          # light | switch | input_boolean
light_icon_1:       "ceiling_lamp"   # ceiling_lamp | night_lamp | bed | tv | …
```

---

## 3D Print Stand

A desk stand for this display is available on MakerWorld:
[Guition ESP32-S3 4848S040 Desk Stand](https://makerworld.com/en/models/1587503-guition-esp32-se-4848s040-desk-stand#profileId-1671461)

---

## Credits

- Original project: [alaltitov/Guition-ESP32-S3-4848S040](https://github.com/alaltitov/Guition-ESP32-S3-4848S040)
- Built with [ESPHome](https://esphome.io) and [LVGL](https://lvgl.io)
