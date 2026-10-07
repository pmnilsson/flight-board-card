# Changelog

## 1.7.0 (fork)
- Track flight dropdown in the header: pick any flight on the board (filterable by flight, city or airline) to pin it; tap again to untrack.

## 1.6.0 (fork)
- Flight tracker: enter a flight number to pin its status in a Tracking panel above the board, and highlight it in the lists. Works with flight numbers and callsigns, ignores the other filters, and is remembered per device.
- New options `show_flight_tracker` and `tracked_flights`.

## 1.5.0 (fork)
- Add airlines to the dropdown from the card: pick from the airlines currently on the board or type a 2-letter code. Saved per device, removable with the x.
- Time window dropdown (Any time, Next 1/2/4/8/12/24 hours), configurable with `time_windows` and `time_window`, remembered per device.
- New options `allow_add_airlines`, `show_window_selector`, `time_windows`, `time_window`.

## 1.4.0 (fork)
- Airline filter dropdown (default AA, DL, UA, configurable with `airlines`), remembered per device.
- `hide_private` hides flights without an airline IATA code (on by default).
- Split-flap style: tiles scroll through the character drum before settling on the right letter or number. Options `flip_cycle`, `flip_on_load`, `flip_step_ms`, `flip_max_steps`.
- Only tiles whose text changed animate on updates.

## 1.3.1
- More room for the Status column (taken from Time and Flight, Destination unchanged).
- Status words switch to short forms (EXP, DELAY, DEP, CANCEL) only when the full word does not fit.

## 1.3.0
- First public release.
- Six board styles, selectable on the card: Classic, Split-flap, Digital flaps, Amsterdam style, London style, LED dot-matrix.
- Airport search with about 8,000 airports, plus a favourites list.
- Visual editor for all settings.
- 24-hour or 12-hour time format.
- Show departures, arrivals or both; side by side or stacked.
- Expected, delayed and landed times aligned in their own column.
- Board scales to fit any screen width.
- Clear message when the Flightradar24 integration is missing.
- Full width in Sections dashboards.
