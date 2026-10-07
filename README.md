# Flight Board Card

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Validate](https://github.com/pmnilsson/flight-board-card/actions/workflows/validate.yml/badge.svg)](https://github.com/pmnilsson/flight-board-card/actions/workflows/validate.yml)

An airport **departures and arrivals board** for your Home Assistant dashboard. It is built for wall panels and tablets: large, readable text, live status and six classic board styles, including a split-flap board with flipping letters.

It shows the flights from the [Flightradar24 integration](https://github.com/AlexandrErohin/home-assistant-flightradar24). No Flightradar24 subscription is needed.

![Split-flap style with flipping letters](https://raw.githubusercontent.com/pmnilsson/flight-board-card/main/images/splitflap-demo.gif)

## Features

- Departures and arrivals side by side (or stacked, or only one of them)
- Six board styles, selectable from a menu on the card itself:
  - **Classic**: black and yellow
  - **Split-flap**: every letter on its own flap, letters flip when something changes
  - **Digital flaps**: modern flap-look panels
  - **Amsterdam style**: dark blue and yellow, clean and very readable
  - **London style**: black and yellow
  - **LED dot-matrix**: glowing amber retro display
- Airport search on the card: type a name, city, IATA or ICAO code and pick from about 8,000 airports worldwide, with no setup or API key needed
- A short list of favourite airports is shown when you tap the search field. Use the built-in list or set your own.
- Times and clock in the airport's own local time zone, 24-hour or 12-hour format
- Expected, delayed and landed times aligned in their own column
- Colour-coded status: on time, expected, delayed, boarding, landed / departed, cancelled, diverted
- Visual editor: all settings can be changed in the card editor, no YAML needed
- Scales to fit any screen width
- The selected style is remembered per device, so each screen can have its own look

| Classic | Digital flaps |
|---|---|
| ![Classic](https://raw.githubusercontent.com/pmnilsson/flight-board-card/main/images/classic.png) | ![Digital flaps](https://raw.githubusercontent.com/pmnilsson/flight-board-card/main/images/digital.png) |
| **Amsterdam style** | **London style** |
| ![Amsterdam style](https://raw.githubusercontent.com/pmnilsson/flight-board-card/main/images/amsterdam.png) | ![London style](https://raw.githubusercontent.com/pmnilsson/flight-board-card/main/images/london.png) |
| **LED dot-matrix** | |
| ![LED dot-matrix](https://raw.githubusercontent.com/pmnilsson/flight-board-card/main/images/led.png) | |

## Requirements

1. Home Assistant 2024.1 or newer.
2. The **Flightradar24** integration ([AlexandrErohin/home-assistant-flightradar24](https://github.com/AlexandrErohin/home-assistant-flightradar24)), installed via HACS and added under Settings > Devices & services.

The integration creates these entities, which the card uses by default:

| Entity | Used for |
|---|---|
| `sensor.flightradar24_airport_departures` | departures |
| `sensor.flightradar24_airport_arrivals` | arrivals |
| `text.flightradar24_airport_track` | which airport is shown (ICAO code, e.g. `ESSA`) |

If the integration is missing, the card shows a message telling you what to install.

## Installation

### HACS (recommended)

1. Open HACS, click the three dots in the top right and choose **Custom repositories**.
2. Add `https://github.com/pmnilsson/flight-board-card` with type **Dashboard**.
3. Search for **Flight Board Card** and click **Download**.
4. Reload your browser.

### Manual

1. Download `flight-board-card.js` from the latest release.
2. Copy it to `/config/www/flight-board-card.js`.
3. Add it as a resource: Settings > Dashboards > three dots > Resources > Add, URL `/local/flight-board-card.js`, type **JavaScript module**.

## Usage

Add the card from the card picker (search for "Flight Board") and change the settings in the visual editor, or use YAML:

```yaml
type: custom:flight-board-card
```

Full example:

```yaml
type: custom:flight-board-card
theme: splitflap
time_format: 24h
rows: 12
font_size: 22
show: both
layout: auto
past_minutes: 15
show_airline: true
show_selector: true
show_airport_selector: true
```

The board looks best on its own dashboard view with the **Panel (single card)** layout. In a **Sections** view it automatically takes the full width.

### Options

| Option | Default | Description |
|---|---|---|
| `theme` | `classic` | Starting style: `classic`, `splitflap`, `digital`, `amsterdam`, `london`, `led`. A style picked in the menu on the card overrides this on that device. |
| `time_format` | `24h` | `24h` (18:30) or `12h` (6:30 PM) |
| `rows` | `12` | Number of flights shown in each list |
| `font_size` | `22` | Base text size in pixels |
| `show` | `both` | `both`, `departures` or `arrivals` |
| `layout` | `auto` | `auto` (side by side on wide screens) or `stacked` |
| `past_minutes` | `15` | How long departed or landed flights stay on the board |
| `show_airline` | `true` | Show the airline and airport code under the flight number and city |
| `show_selector` | `true` | Show the style menu on the card |
| `show_airport_selector` | `true` | Show the airport search field on the card |
| `show_airline_selector` | `true` | Show the airline filter dropdown (All / AA / DL / UA ...) on the card |
| `airlines` | AA, DL, UA | Airlines in the dropdown. Plain codes (`- AA`) or `{iata: AA, name: American}` entries |
| `airline` | (all) | Airline pre-selected at start. A choice made in the dropdown overrides it on that device |
| `allow_add_airlines` | `true` | Lets you add airlines to the dropdown on the card: pick one from "On the board now" or type a 2-letter code. Added airlines are saved on that device and can be removed with the x |
| `show_window_selector` | `true` | Show the time window dropdown (Any time / Next 1h ... 24h) on the card |
| `time_windows` | 1, 2, 4, 8, 12, 24 | Hours offered in the time window dropdown |
| `time_window` | `0` | Time window selected at start in hours (`0` = any time). A choice made in the dropdown overrides it on that device |
| `hide_private` | `true` | Hide private, charter and general-aviation flights (flights without an airline IATA code) |
| `flip_cycle` | `true` | Split-flap style only: letters and numbers scroll through the drum before settling, like a real board |
| `flip_on_load` | `true` | Spin every tile in from blank on first load |
| `flip_step_ms` | `55` | Milliseconds per character step (higher = slower) |
| `flip_max_steps` | `24` | Most characters a tile scrolls through before settling (lower = faster) |
| `airports` | built-in list | Favourite airports shown when the search field is empty (see below) |
| `title` | airport name | Your own title instead of the airport name |
| `departures_entity` | `sensor.flightradar24_airport_departures` | Departures sensor |
| `arrivals_entity` | `sensor.flightradar24_airport_arrivals` | Arrivals sensor |
| `airport_entity` | `text.flightradar24_airport_track` | Text entity that holds the tracked airport |

Tip: on a public or shared screen, set `show_airport_selector: false` so nobody changes the airport by mistake.

### Favourite airports

```yaml
type: custom:flight-board-card
airports:
  - icao: ESSA
    iata: ARN
    name: Stockholm Arlanda
    tz: Europe/Stockholm
  - icao: KLAX
    iata: LAX
    name: Los Angeles
    tz: America/Los_Angeles
```

Any airport can be found with the search. The favourites are just quick picks. Built-in favourites: Stockholm Arlanda, Stockholm Bromma, Göteborg Landvetter, Copenhagen, Oslo, Helsinki, London Heathrow, Amsterdam Schiphol, Frankfurt, Paris CDG, Milano Malpensa, Zurich, Singapore Changi, Dubai and New York JFK.

### Airline filter (fork)

```yaml
type: custom:flight-board-card
theme: splitflap
airlines:
  - AA
  - DL
  - UA
  - iata: WN
    name: Southwest
```

The time window hides flights scheduled later than the chosen number of hours from now. The `rows` limit still applies, so raise `rows` if a long window should list more flights.

American Eagle, Delta Connection and United Express report their mainline code, so they appear under AA, DL and UA. With a single airline selected you may see fewer rows than `rows`, because only that airline's flights are listed. The selection is stored per device (browser localStorage).

## Good to know

- **Fork notice.** This fork adds the airline dropdown, private-flight hiding and the scrolling split-flap animation. Install it in HACS as a custom repository (type Dashboard) in place of the original; the card type stays `custom:flight-board-card`.

- **One airport per Home Assistant installation.** The Flightradar24 integration follows one airport at a time. Changing the airport on the card changes it for every screen and every card using the integration.
- **Switching airport takes a moment.** The board shows *Loading* until Flightradar24 has fetched the new airport's flights, usually 20–60 seconds depending on the integration's scan interval.
- **About the data.** The Flightradar24 integration uses Flightradar24's public, unofficial data feed. If Flightradar24 changes something on their side, flight data can stop updating until the integration is updated. That is outside this card's control. Please report data problems to the [integration](https://github.com/AlexandrErohin/home-assistant-flightradar24/issues) and display problems [here](https://github.com/pmnilsson/flight-board-card/issues).
- **Upgrading from an early version.** The old style names `solari`, `frankfurt`, `schiphol` and `heathrow` still work and are mapped to `splitflap`, `digital`, `amsterdam` and `london`.

## Airport data

The airport search uses a compact copy of the [mwgg/Airports](https://github.com/mwgg/Airports) database (MIT License), limited to airports that have an IATA code. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Disclaimer

This project is not affiliated with or endorsed by Flightradar24, any airport or any airport operator. The styles are original designs inspired by well-known types of departure boards. Flight data comes from the Flightradar24 integration and may be delayed or incomplete, so don't use it for real travel decisions.

## License

[MIT](LICENSE) © 2026 P-M Nilsson
