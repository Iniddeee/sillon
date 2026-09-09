import json
from datetime import date, timedelta
from pathlib import Path

from sillon import cli
from sillon.extract import extract
from sillon.window import day_record, merge, write_json

FIXTURE = Path(__file__).parent / "fixtures" / "sample_istdaten.csv"
PAIRS_PATH = Path(__file__).parents[2] / "config" / "pairs.json"

PAIR = {
    "id": "berne-bale",
    "from": {"bpuic": 8507000, "name": "Berne"},
    "to": {"bpuic": 8500010, "name": "Bâle"},
    "via": None,
}


def _train(dep_delay=0, arr_delay=0, status="REAL", cancelled=False, **overrides):
    train = {
        "line": "IC6",
        "planned_dep": "07:04",
        "planned_arr": "08:00",
        "dep_delay": dep_delay,
        "arr_delay": arr_delay,
        "dep_status": status,
        "arr_status": status,
        "cancelled": cancelled,
    }
    train.update(overrides)
    return train


def _itinerary(via_arr_status="REAL", via_dep_status="REAL", **overrides):
    train = _train(
        line2="IC5",
        via_arr="07:51",
        via_dep="08:02",
        via_arr_delay=1,
        via_arr_status=via_arr_status,
        via_dep_delay=0,
        via_dep_status=via_dep_status,
    )
    train.update(overrides)
    return train


def test_day_record_real():
    assert day_record(_train(dep_delay=1, arr_delay=2)) == {"status": "real", "dep": 1, "arr": 2}


def test_day_record_cancelled():
    assert day_record(_train(cancelled=True)) == {"status": "cancelled"}


def test_day_record_nodata_when_one_status_not_real():
    train = _train(status="REAL", arr_status="PROGNOSE")
    assert day_record(train) == {"status": "nodata"}


def test_day_record_legs_present_when_both_via_statuses_real():
    record = day_record(_itinerary())
    assert record["legs"] == [{"arr": 1}, {"dep": 0}]


def test_day_record_legs_absent_when_a_via_status_is_not_real():
    record = day_record(_itinerary(via_dep_status="PROGNOSE"))
    assert "legs" not in record


def test_day_record_legs_absent_for_a_direct_train():
    assert "legs" not in day_record(_train())


def test_window_slides_past_max_days():
    start = date(2026, 1, 1)
    state = None
    for i in range(91):
        state = merge(PAIR, start + timedelta(days=i), [_train()], state, max_days=90)

    train = state["trains"][0]
    assert len(train["days"]) == 90
    assert start.isoformat() not in train["days"]
    assert (start + timedelta(days=1)).isoformat() in train["days"]


def test_merge_same_day_twice_is_idempotent():
    day = date(2026, 9, 7)
    once = merge(PAIR, day, [_train()], None)
    twice = merge(PAIR, day, [_train()], once)
    assert once == twice


def test_train_with_no_remaining_days_is_dropped():
    start = date(2026, 1, 1)
    train_a = _train()
    train_b = _train(line="IC8", planned_dep="09:04", planned_arr="10:00")

    state = merge(PAIR, start, [train_a], None, max_days=90)
    for i in range(1, 91):
        state = merge(PAIR, start + timedelta(days=i), [train_b], state, max_days=90)

    keys = {t["key"] for t in state["trains"]}
    assert "IC6|07:04" not in keys
    assert "IC8|09:04" in keys


def test_planned_arr_is_updated_by_latest_day():
    day1, day2 = date(2026, 9, 1), date(2026, 9, 2)
    state = merge(PAIR, day1, [_train(planned_arr="08:00")], None)
    state = merge(PAIR, day2, [_train(planned_arr="08:05")], state)
    assert state["trains"][0]["planned_arr"] == "08:05"


def test_write_json_is_byte_identical_across_writes(tmp_path):
    obj = {"b": 1, "a": [3, 2, 1]}
    path = tmp_path / "out.json"

    write_json(path, obj)
    first = path.read_bytes()
    write_json(path, obj)
    second = path.read_bytes()

    assert first == second
    assert first.endswith(b"\n")


def test_merge_carries_itinerary_fields_and_legs_for_a_day():
    via_pair = {
        "id": "delemont-bienne-lausanne",
        "from": {"bpuic": 8500109, "name": "Delémont"},
        "to": {"bpuic": 8501120, "name": "Lausanne"},
        "via": {"bpuic": 8504300, "name": "Bienne"},
    }
    trains = extract(FIXTURE, [via_pair])["delemont-bienne-lausanne"]
    state = merge(via_pair, date(2026, 9, 7), trains, None)

    train = next(t for t in state["trains"] if t["key"] == "RE56|09:41")
    assert train["line2"] == "IC51"
    assert train["via_arr"] == "10:11"
    assert train["via_dep"] == "10:48"
    assert train["days"]["2026-09-07"]["legs"] == [{"arr": 2}, {"dep": 0}]


def test_run_end_to_end(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    argv = [
        "sillon",
        "run",
        "--date",
        "2026-09-07",
        "--csv",
        str(FIXTURE),
        "--pairs",
        str(PAIRS_PATH),
        "--data",
        str(data_dir),
    ]
    monkeypatch.setattr("sys.argv", argv)
    cli.main()

    assert FIXTURE.exists()  # --csv input is never deleted, only a downloaded copy is

    index = json.loads((data_dir / "index.json").read_text(encoding="utf-8"))
    assert index["days"] == ["2026-09-07"]
    assert {p["id"] for p in index["pairs"]} >= {"berne-bale", "delemont-porrentruy"}

    pair_data = json.loads((data_dir / "pairs" / "berne-bale.json").read_text(encoding="utf-8"))
    assert pair_data["id"] == "berne-bale"
    train = next(t for t in pair_data["trains"] if t["planned_dep"] == "08:04")
    assert train["days"]["2026-09-07"] == {"status": "cancelled"}
