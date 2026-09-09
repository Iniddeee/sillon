from datetime import datetime
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


def extract(csv: Path, pairs: list[dict]) -> dict[str, list[dict]]:
    stops = {str(p["from"]["bpuic"]) for p in pairs} | {str(p["to"]["bpuic"]) for p in pairs}

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

    result: dict[str, list[dict]] = {}
    for pair in pairs:
        from_bpuic = str(pair["from"]["bpuic"])
        to_bpuic = str(pair["to"]["bpuic"])
        trains = []

        for legs in trips.values():
            departures = sorted(
                (leg for leg in legs if leg["bpuic"] == from_bpuic and leg["planned_dep"]),
                key=lambda leg: leg["planned_dep"],
            )
            if not departures:
                continue
            dep = departures[0]

            # a route can pass "to" more than once; keep the first pass after departure
            arrivals = sorted(
                (
                    leg
                    for leg in legs
                    if leg["bpuic"] == to_bpuic
                    and leg["planned_arr"]
                    and leg["planned_arr"] > dep["planned_dep"]
                ),
                key=lambda leg: leg["planned_arr"],
            )
            if not arrivals:
                continue
            arr = arrivals[0]

            trains.append(
                {
                    "line": dep["line"],
                    "planned_dep": dep["planned_dep"].strftime("%H:%M"),
                    "planned_arr": arr["planned_arr"].strftime("%H:%M"),
                    "dep_delay": _delay(dep["planned_dep"], dep["dep_prognose"]),
                    "arr_delay": _delay(arr["planned_arr"], arr["arr_prognose"]),
                    "dep_status": dep["dep_status"],
                    "arr_status": arr["arr_status"],
                    "cancelled": dep["cancelled"] or arr["cancelled"],
                }
            )

        trains.sort(key=lambda t: (t["planned_dep"], t["line"]))
        result[pair["id"]] = trains

    return result
