# automation_flight_board_schedule.py
#
# PURPOSE
#   Gives the Flight Board Card the SCHEDULE of flights that are being tracked but
#   are not airborne yet (route, scheduled departure and arrival times).
#
#   The Flightradar24 integration only knows the flight number of a flight that has
#   not taken off, so the card could only show "Not airborne yet". This script asks
#   the same Flightradar24 data source that the flightradar24.com flight page uses
#   (https://www.flightradar24.com/data/flights/aa4415) for the schedule and
#   publishes it as one sensor that the card reads.
#
# HOW IT WORKS
#   - Reads the flights in sensor.flightradar24_additional_tracked (the card adds
#     flights there when you track them) plus the optional EXTRA_FLIGHTS list below.
#   - Only flights that are NOT live (not airborne) are looked up. Once a flight is
#     airborne the integration provides the live data itself.
#   - For each flight it picks the most relevant leg (live, else the next one, else
#     the most recent) and publishes it in sensor.flight_board_schedule.
#   - Results are cached, so each flight is looked up at most once per
#     CACHE_SECONDS.
#
# CARD SETTINGS
#   The card reads sensor.flight_board_schedule by default (schedule_entity option).
#
# NOTES
#   - This uses an unofficial Flightradar24 web endpoint. Flightradar24 can block or
#     change it at any time. When that happens the script logs a warning, keeps the
#     last good data and sends ONE notification per NOTIFY_COOLDOWN_SECONDS.
#   - PyScript sensors are not saved across a full HA restart; the startup trigger
#     rebuilds the sensor every time PyScript loads.
#   - Only the Python standard library is used (urllib, json), no extra install.

import json
import time
import urllib.request

# =============================================================================
# VARIABLES (all settings live here)
# =============================================================================

# Sensor created by the Flightradar24 integration that lists the tracked flights
TRACKED_SENSOR = "sensor.flightradar24_additional_tracked"

# Sensor created by this script (the card reads it)
OUT_SENSOR = "sensor.flight_board_schedule"
OUT_NAME = "Flight board schedule"
OUT_ICON = "mdi:airplane-clock"

# Extra flight numbers to always look up, even if the card did not add them.
# Example: ["AA4415", "DL1234"]
EXTRA_FLIGHTS = []

# Flightradar24 flight list endpoint (same data as the flight page)
FR24_URL = "https://api.flightradar24.com/common/v1/flight/list.json?query={query}&fetchBy=flight&page=1&limit=25"
FR24_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
FETCH_TIMEOUT_SECONDS = 15

# A flight is looked up at most once per this many seconds
CACHE_SECONDS = 900

# How often the sensor is rebuilt (also rebuilt when the tracked sensor changes)
REFRESH_PERIOD_SECONDS = 300

# A leg that landed more than this many seconds ago is treated as finished
FINISHED_AFTER_SECONDS = 3 * 3600

# Error notifications
NOTIFY_SERVICE_NAME = "mobile_app_iphone_rg"
NOTIFY_TITLE = "Flight board schedule"
PERSISTENT_NOTIFICATION_ID = "flight_board_schedule_error"
# Minimum seconds between repeated error notifications (avoids spam)
NOTIFY_COOLDOWN_SECONDS = 3600

# Log prefix
LOG_PREFIX = "flight_board_schedule"

# Mutable module state (a dict avoids needing "global")
SCHEDULE_STATE = {"last_notify": 0, "cache": {}}


# =============================================================================
# HELPERS
# =============================================================================

def fb_sched_notify_error(message):
    # Send an error to the iPhone AND to the Home Assistant notification panel,
    # at most once per NOTIFY_COOLDOWN_SECONDS. Never raises.
    try:
        now = time.time()
        if now - SCHEDULE_STATE["last_notify"] < NOTIFY_COOLDOWN_SECONDS:
            return
        SCHEDULE_STATE["last_notify"] = now

        # Phone notification
        try:
            service.call("notify", NOTIFY_SERVICE_NAME, title=NOTIFY_TITLE, message=message)
        except Exception as e:
            log.error(f"{LOG_PREFIX}: phone notify failed: {e}")

        # Home Assistant notification
        try:
            service.call(
                "persistent_notification",
                "create",
                title=NOTIFY_TITLE,
                message=message,
                notification_id=PERSISTENT_NOTIFICATION_ID,
            )
        except Exception as e:
            log.error(f"{LOG_PREFIX}: persistent notification failed: {e}")
    except Exception as e:
        log.error(f"{LOG_PREFIX}: notify helper failed: {e}")


def fb_sched_get(data, path):
    # Safe nested lookup: path is a list of keys. Returns None if anything is missing.
    cur = data
    for key in path:
        if cur is None:
            return None
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def fb_sched_norm(value):
    # Upper case, letters and digits only ("aa 4415" -> "AA4415")
    out = ""
    for ch in str(value or "").upper():
        if ch.isalnum():
            out = out + ch
    return out


def fb_sched_leg(item):
    # Turn one Flightradar24 flight list entry into the attribute layout the card uses.
    return {
        "flight_number": fb_sched_get(item, ["identification", "number", "default"]),
        "callsign": fb_sched_get(item, ["identification", "callsign"]),
        "aircraft_registration": fb_sched_get(item, ["aircraft", "registration"]),
        "aircraft_model": fb_sched_get(item, ["aircraft", "model", "text"]),
        "aircraft_code": fb_sched_get(item, ["aircraft", "model", "code"]),
        "airline": fb_sched_get(item, ["airline", "name"]),
        "airline_short": fb_sched_get(item, ["airline", "short"]),
        "airline_iata": fb_sched_get(item, ["airline", "code", "iata"]),
        "airline_icao": fb_sched_get(item, ["airline", "code", "icao"]),
        "airport_origin_name": fb_sched_get(item, ["airport", "origin", "name"]),
        "airport_origin_code_iata": fb_sched_get(item, ["airport", "origin", "code", "iata"]),
        "airport_origin_code_icao": fb_sched_get(item, ["airport", "origin", "code", "icao"]),
        "airport_origin_city": fb_sched_get(item, ["airport", "origin", "position", "region", "city"]),
        "airport_destination_name": fb_sched_get(item, ["airport", "destination", "name"]),
        "airport_destination_code_iata": fb_sched_get(item, ["airport", "destination", "code", "iata"]),
        "airport_destination_code_icao": fb_sched_get(item, ["airport", "destination", "code", "icao"]),
        "airport_destination_city": fb_sched_get(item, ["airport", "destination", "position", "region", "city"]),
        "time_scheduled_departure": fb_sched_get(item, ["time", "scheduled", "departure"]),
        "time_scheduled_arrival": fb_sched_get(item, ["time", "scheduled", "arrival"]),
        "time_estimated_departure": fb_sched_get(item, ["time", "estimated", "departure"]),
        "time_estimated_arrival": fb_sched_get(item, ["time", "estimated", "arrival"]),
        "time_real_departure": fb_sched_get(item, ["time", "real", "departure"]),
        "time_real_arrival": fb_sched_get(item, ["time", "real", "arrival"]),
        "status_text": fb_sched_get(item, ["status", "text"]),
        "is_live": bool(fb_sched_get(item, ["status", "live"])),
    }


def fb_sched_pick(legs, now):
    # Choose the most relevant leg: a live one first, then the nearest one that has not
    # finished, then the nearest of any. "Nearest" = scheduled departure closest to now.
    best = None
    best_rank = 9
    best_dist = 0
    for leg in legs:
        dep = leg.get("time_scheduled_departure")
        if dep is None:
            dep = leg.get("time_estimated_departure")
        if dep is None:
            continue
        arr = leg.get("time_real_arrival")
        if leg.get("is_live"):
            rank = 0
        elif arr is None and dep >= now - FINISHED_AFTER_SECONDS:
            rank = 1
        elif arr is not None and arr >= now - FINISHED_AFTER_SECONDS:
            rank = 1
        else:
            rank = 2
        dist = abs(dep - now)
        if best is None or rank < best_rank or (rank == best_rank and dist < best_dist):
            best = leg
            best_rank = rank
            best_dist = dist
    return best


def fb_sched_fetch(code):
    # Download the flight list for one flight number and return the best leg (dict) or None.
    # Raises on network or parse errors so the caller can log and keep the old data.
    url = FR24_URL.replace("{query}", code.lower())
    req = urllib.request.Request(
        url,
        headers={"User-Agent": FR24_USER_AGENT, "Accept": "application/json"},
    )
    # Blocking calls run in a worker thread so Home Assistant is not held up
    resp = task.executor(urllib.request.urlopen, req, timeout=FETCH_TIMEOUT_SECONDS)
    raw = task.executor(resp.read)
    try:
        task.executor(resp.close)
    except Exception:
        pass
    payload = json.loads(raw.decode("utf-8"))
    items = fb_sched_get(payload, ["result", "response", "data"])
    if not items:
        return None
    legs = []
    for item in items:
        try:
            legs.append(fb_sched_leg(item))
        except Exception as e:
            log.warning(f"{LOG_PREFIX}: skipped a malformed leg for {code}: {e}")
    return fb_sched_pick(legs, time.time())


def fb_sched_codes():
    # Flights to look up: tracked-but-not-live flights from the integration plus EXTRA_FLIGHTS.
    codes = []
    try:
        attrs = state.getattr(TRACKED_SENSOR)
        flights = []
        if attrs:
            flights = attrs.get("flights") or []
        for flight in flights:
            if flight.get("tracked_type") == "live":
                continue
            code = fb_sched_norm(flight.get("flight_number") or flight.get("callsign"))
            if code and code not in codes:
                codes.append(code)
    except Exception as e:
        log.warning(f"{LOG_PREFIX}: could not read {TRACKED_SENSOR}: {e}")
    for extra in EXTRA_FLIGHTS:
        code = fb_sched_norm(extra)
        if code and code not in codes:
            codes.append(code)
    return codes


# =============================================================================
# TRIGGERS
# =============================================================================

@state_trigger(TRACKED_SENSOR)
@time_trigger("startup", f"period(00:00:00, {REFRESH_PERIOD_SECONDS}sec)")
def flight_board_schedule_refresh():
    # This is a rebuild (not a one-shot action), so the idempotency guard is
    # intentionally not used; re-running is always safe.
    cache = SCHEDULE_STATE["cache"]
    now = time.time()
    codes = fb_sched_codes()
    failures = []

    # Each flight is handled on its own so one failure never blocks the others.
    for code in codes:
        entry = None
        try:
            entry = cache.get(code)
            if entry is not None and now - entry["at"] < CACHE_SECONDS:
                continue
            leg = fb_sched_fetch(code)
            cache[code] = {"at": now, "leg": leg}
            if leg is None:
                log.info(f"{LOG_PREFIX}: Flightradar24 has no schedule for {code}")
        except Exception as e:
            # Keep the previous data (if any) and retry on the next refresh
            log.warning(f"{LOG_PREFIX}: lookup for {code} failed: {e}")
            failures.append(code)
            if entry is not None:
                cache[code] = {"at": now - CACHE_SECONDS + 60, "leg": entry["leg"]}

    try:
        # Only publish flights that are still wanted
        out = []
        for code in codes:
            entry = cache.get(code)
            if entry is None or entry["leg"] is None:
                continue
            leg = dict(entry["leg"])
            leg["query"] = code
            leg["schedule_fetched_at"] = entry["at"]
            out.append(leg)
        # Forget flights that are no longer tracked
        for key in list(cache.keys()):
            if key not in codes:
                cache.pop(key, None)

        state.set(
            OUT_SENSOR,
            value=len(out),
            new_attributes={
                "state_class": "total",
                "flights": out,
                "icon": OUT_ICON,
                "friendly_name": OUT_NAME,
                "source": "flightradar24 flight list",
            },
        )
    except Exception as e:
        log.error(f"{LOG_PREFIX}: failed publishing {OUT_SENSOR}: {e}")
        fb_sched_notify_error(f"Failed publishing {OUT_SENSOR}: {e}")
        return

    if failures:
        fb_sched_notify_error(
            "Could not get the schedule from Flightradar24 for: " + ", ".join(failures)
            + ". Flightradar24 may be blocking or have changed the endpoint. Check the log."
        )
