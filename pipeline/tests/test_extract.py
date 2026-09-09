from pathlib import Path

from sillon.extract import extract

FIXTURE = Path(__file__).parent / "fixtures" / "sample_istdaten.csv"

PAIRS = [
    {
        "id": "delemont-porrentruy",
        "from": {"bpuic": 8500109, "name": "Delémont"},
        "to": {"bpuic": 8500126, "name": "Porrentruy"},
        "via": None,
    },
    {
        "id": "porrentruy-delemont",
        "from": {"bpuic": 8500126, "name": "Porrentruy"},
        "to": {"bpuic": 8500109, "name": "Delémont"},
        "via": None,
    },
    {
        "id": "berne-bale",
        "from": {"bpuic": 8507000, "name": "Berne"},
        "to": {"bpuic": 8500010, "name": "Bâle"},
        "via": None,
    },
    {
        "id": "lausanne-geneve",
        "from": {"bpuic": 8501120, "name": "Lausanne"},
        "to": {"bpuic": 8501008, "name": "Genève"},
        "via": None,
    },
]


def test_train_counts_per_pair():
    # counted by hand in sample_istdaten.csv: 42 Delémont->Porrentruy legs,
    # 41 the other way, 9 Bern->Basel SBB legs (8 running + 1 cancelled)
    result = extract(FIXTURE, PAIRS)
    assert len(result["delemont-porrentruy"]) == 42
    assert len(result["porrentruy-delemont"]) == 41
    assert len(result["berne-bale"]) == 9


def test_pair_with_no_trains_in_file_is_empty():
    result = extract(FIXTURE, PAIRS)
    assert result["lausanne-geneve"] == []


def test_cancelled_train_is_flagged():
    result = extract(FIXTURE, PAIRS)
    train = next(t for t in result["berne-bale"] if t["planned_dep"] == "08:04")
    assert train["cancelled"] is True
    assert train["line"] == "IC6"
    assert train["planned_arr"] == "09:00"


def test_unbekannt_status_is_kept_raw():
    result = extract(FIXTURE, PAIRS)
    train = next(t for t in result["berne-bale"] if t["planned_dep"] == "08:04")
    assert train["dep_status"] == "UNBEKANNT"
    assert train["arr_status"] == "UNBEKANNT"
    assert train["dep_delay"] is None
    assert train["arr_delay"] is None


def test_delay_matches_hand_computed_value():
    # raw fixture row: Bern AB 06:04 / prognose 06:04:52 (+52s -> 0 min)
    #                  Basel SBB AN 07:00 / prognose 07:01:18 (+78s -> 1 min)
    result = extract(FIXTURE, PAIRS)
    train = next(t for t in result["berne-bale"] if t["planned_dep"] == "06:04")
    assert train["dep_delay"] == 0
    assert train["arr_delay"] == 1
    assert train["dep_status"] == "REAL"
    assert train["arr_status"] == "REAL"
