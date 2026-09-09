from datetime import datetime, timedelta
from pathlib import Path

import duckdb

_PLANNED_FMT = "%d.%m.%Y %H:%M"
_PROGNOSE_FMT = "%d.%m.%Y %H:%M:%S"

_QUERY = """
    SELECT FAHRT_BEZEICHNER, LINIEN_TEXT, BPUIC,
           ANKUNFTSZEIT, AN_PROGNOSE, AN_PROGNOSE_STATUS,
           ABFAHRTSZEIT, AB_PROGNOSE, AB_PROGNOSE_STATUS,
           FAELLT_AUS_TF
    FROM read_csv(?, delim=';', header=true, all_varchar=true)
    WHERE PRODUKT_ID = 'Zug' AND BPUIC = ANY(?)
"""


def _planned(raw: str | None) -> datetime | None:
    return datetime.strptime(raw, _PLANNED_FMT) if raw else None


def _prognose(raw: str | None) -> datetime | None:
    return datetime.strptime(raw, _PROGNOSE_FMT) if raw else None


def _delay(planned: datetime | None, prognose: datetime | None) -> int | None:
    if planned is None or prognose is None:
        return None
    # whole minutes, truncated: a train 2:59 late is still "under 3 minutes"
    return int((prognose - planned).total_seconds() / 60)


def _load_trips(csv: Path, stops: set[str]) -> dict[str, list[dict]]:
    # all_varchar: 22-column file, keep everything as text so a bad status
    # value can't crash the read; times are parsed to datetime below
    con = duckdb.connect()
    rows = con.execute(_QUERY, [str(csv), list(stops)]).fetchall()

    trips: dict[str, list[dict]] = {}
    for trip_id, line, bpuic, arr_raw, arr_prog, arr_status, dep_raw, dep_prog, dep_status, ausfall in rows:
        trips.setdefault(trip_id, []).append(
            {
                "line": line,
                "bpuic": bpuic,
                "planned_arr": _planned(arr_raw),
                "arr_prognose": _prognose(arr_prog),
                "arr_status": arr_status or "",
                "planned_dep": _planned(dep_raw),
                "dep_prognose": _prognose(dep_prog),
                "dep_status": dep_status or "",
                "cancelled": ausfall == "true",
            }
        )
    return trips


def _first_leg(legs: list[dict], bpuic: str, key: str, after: datetime | None = None) -> dict | None:
    matches = sorted(
        (leg for leg in legs if leg["bpuic"] == bpuic and leg[key] and (after is None or leg[key] > after)),
        key=lambda leg: leg[key],
    )
    return matches[0] if matches else None


def _segments(trips: dict[str, list[dict]], from_bpuic: str, to_bpuic: str) -> list[dict]:
    segments = []
    for legs in trips.values():
        dep = _first_leg(legs, from_bpuic, "planned_dep")
        if dep is None:
            continue

        # a route can pass "to" more than once; keep the first pass after departure
        arr = _first_leg(legs, to_bpuic, "planned_arr", after=dep["planned_dep"])
        if arr is None:
            continue

        segments.append(
            {
                "line": dep["line"],
                "dep_dt": dep["planned_dep"],
                "arr_dt": arr["planned_arr"],
                "planned_dep": dep["planned_dep"].strftime("%H:%M"),
                "planned_arr": arr["planned_arr"].strftime("%H:%M"),
                "dep_delay": _delay(dep["planned_dep"], dep["dep_prognose"]),
                "arr_delay": _delay(arr["planned_arr"], arr["arr_prognose"]),
                "dep_status": dep["dep_status"],
                "arr_status": arr["arr_status"],
                "cancelled": dep["cancelled"] or arr["cancelled"],
            }
        )
    segments.sort(key=lambda t: (t["planned_dep"], t["line"]))
    return segments


def _direct_trains(trips: dict[str, list[dict]], from_bpuic: str, to_bpuic: str) -> list[dict]:
    return [
        {k: v for k, v in seg.items() if k not in ("dep_dt", "arr_dt")}
        for seg in _segments(trips, from_bpuic, to_bpuic)
    ]


def _connecting_trains(
    trips: dict[str, list[dict]], from_bpuic: str, via_bpuic: str, to_bpuic: str, transfer_min: int
) -> list[dict]:
    first_legs = _segments(trips, from_bpuic, via_bpuic)
    second_legs = _segments(trips, via_bpuic, to_bpuic)

    trains = []
    for s1 in first_legs:
        earliest = s1["arr_dt"] + timedelta(minutes=transfer_min)
        # second_legs is sorted by planned_dep as a string, not by dep_dt, so a
        # next-day departure ("00:18") can sort before a same-day one ("23:18");
        # pick the true chronological minimum among valid candidates instead
        candidates = (s for s in second_legs if s["dep_dt"] >= earliest)
        s2 = min(candidates, key=lambda s: s["dep_dt"], default=None)
        if s2 is None:
            continue

        trains.append(
            {
                "line": s1["line"],
                "line2": s2["line"],
                "planned_dep": s1["planned_dep"],
                "planned_arr": s2["planned_arr"],
                "dep_delay": s1["dep_delay"],
                "dep_status": s1["dep_status"],
                "arr_delay": s2["arr_delay"],
                "arr_status": s2["arr_status"],
                "cancelled": s1["cancelled"] or s2["cancelled"],
                "via_arr": s1["planned_arr"],
                "via_dep": s2["planned_dep"],
                "via_arr_delay": s1["arr_delay"],
                "via_arr_status": s1["arr_status"],
                "via_dep_delay": s2["dep_delay"],
                "via_dep_status": s2["dep_status"],
            }
        )
    trains.sort(key=lambda t: (t["planned_dep"], t["line"]))
    return trains


def extract(csv: Path, pairs: list[dict]) -> dict[str, list[dict]]:
    stops: set[str] = set()
    for pair in pairs:
        stops.add(str(pair["from"]["bpuic"]))
        stops.add(str(pair["to"]["bpuic"]))
        via = pair.get("via")
        if via:
            stops.add(str(via["bpuic"]))

    trips = _load_trips(csv, stops)

    result: dict[str, list[dict]] = {}
    for pair in pairs:
        from_bpuic = str(pair["from"]["bpuic"])
        to_bpuic = str(pair["to"]["bpuic"])
        via = pair.get("via")

        if via:
            via_bpuic = str(via["bpuic"])
            transfer_min = via.get("min_transfer_min", 2)
            result[pair["id"]] = _connecting_trains(trips, from_bpuic, via_bpuic, to_bpuic, transfer_min)
        else:
            result[pair["id"]] = _direct_trains(trips, from_bpuic, to_bpuic)

    return result
