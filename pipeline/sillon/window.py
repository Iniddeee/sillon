import json
from datetime import date
from pathlib import Path


def day_record(train: dict) -> dict:
    if train["cancelled"]:
        return {"status": "cancelled"}
    if train["dep_status"] == "REAL" and train["arr_status"] == "REAL":
        return {"status": "real", "dep": train["dep_delay"], "arr": train["arr_delay"]}
    return {"status": "nodata"}


def merge(
    pair: dict, day: date, trains: list[dict], existing: dict | None, max_days: int = 90
) -> dict:
    by_key: dict[str, dict] = {}
    if existing:
        for t in existing["trains"]:
            by_key[t["key"]] = {**t, "days": dict(t["days"])}

    day_str = day.isoformat()
    seen_today: set[str] = set()
    for train in trains:
        key = f"{train['line']}|{train['planned_dep']}"
        if key in seen_today:
            continue  # two trains with the same line and time on one day: keep the first
        seen_today.add(key)

        entry = by_key.setdefault(
            key,
            {
                "key": key,
                "line": train["line"],
                "planned_dep": train["planned_dep"],
                "planned_arr": train["planned_arr"],
                "days": {},
            },
        )
        entry["planned_arr"] = train["planned_arr"]
        entry["days"][day_str] = day_record(train)

    # window is per pair, not per train: a train quiet for a while still ages
    # out with the rest once its last day falls off the back
    all_days = sorted({d for entry in by_key.values() for d in entry["days"]}, reverse=True)
    keep = set(all_days[:max_days])

    final_trains = []
    for entry in by_key.values():
        entry["days"] = {d: v for d, v in entry["days"].items() if d in keep}
        if entry["days"]:
            final_trains.append(entry)
    final_trains.sort(key=lambda t: (t["planned_dep"], t["line"]))

    via = pair.get("via")
    return {
        "id": pair["id"],
        "from": pair["from"],
        "to": pair["to"],
        "via": via,
        "transfer_min": (via or {}).get("min_transfer_min", 2),
        "trains": final_trains,
    }


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def write_index(data_dir: Path, pairs: list[dict], generated: date) -> list[str]:
    days: set[str] = set()
    summaries = []
    for pair in pairs:
        pair_path = data_dir / "pairs" / f"{pair['id']}.json"
        if pair_path.exists():
            data = json.loads(pair_path.read_text(encoding="utf-8"))
            for train in data["trains"]:
                days.update(train["days"])
        summaries.append(
            {"id": pair["id"], "from": pair["from"], "to": pair["to"], "via": pair.get("via")}
        )

    sorted_days = sorted(days)
    write_json(
        data_dir / "index.json",
        {"generated": generated.isoformat(), "days": sorted_days, "pairs": summaries},
    )
    return sorted_days
