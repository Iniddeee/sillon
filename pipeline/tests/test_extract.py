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

VIA_PAIRS = [
    {
        "id": "delemont-bienne-lausanne",
        "from": {"bpuic": 8500109, "name": "Delémont"},
        "to": {"bpuic": 8501120, "name": "Lausanne"},
        "via": {"bpuic": 8504300, "name": "Bienne"},
    },
    {
        "id": "porrentruy-delemont-bale",
        "from": {"bpuic": 8500126, "name": "Porrentruy"},
        "to": {"bpuic": 8500010, "name": "Bâle"},
        "via": {"bpuic": 8500109, "name": "Delémont"},
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


def test_connecting_itinerary_waits_for_earliest_valid_second_leg():
    # hand-checked in tests/fixtures/sample_istdaten.csv: RE56 4560-002 leaves
    # Delemont 09:41, reaches Bienne 10:11 (+2min default transfer -> 10:13
    # threshold). IC51 1614-001 leaves Bienne at 09:48 (too early, already gone);
    # IC51 1616-001 leaves at 10:48, the first clearing the threshold.
    result = extract(FIXTURE, VIA_PAIRS)
    trip = next(t for t in result["delemont-bienne-lausanne"] if t["planned_dep"] == "09:41")
    assert trip["line"] == "RE56"
    assert trip["line2"] == "IC51"
    assert trip["via_arr"] == "10:11"
    assert trip["via_dep"] == "10:48"
    assert trip["planned_arr"] == "11:56"


def test_connecting_itinerary_same_physical_train_continuing():
    # IC51 1610-001 runs Delemont->Bienne->Lausanne without a change: it shows up
    # as its own segment 2, arriving Bienne 07:41 and leaving again at 07:48.
    result = extract(FIXTURE, VIA_PAIRS)
    trip = next(t for t in result["delemont-bienne-lausanne"] if t["planned_dep"] == "07:11")
    assert trip["line"] == trip["line2"] == "IC51"
    assert trip["via_arr"] == "07:41"
    assert trip["via_dep"] == "07:48"


def test_connecting_itinerary_carries_via_delay():
    # R1 5855-001 (Porrentruy->Delemont) arrives 06:09, prognose 06:10:05 -> +1min
    result = extract(FIXTURE, VIA_PAIRS)
    trip = next(t for t in result["porrentruy-delemont-bale"] if t["planned_dep"] == "05:40")
    assert trip["line"] == "R1"
    assert trip["line2"] == "IR56"
    assert trip["via_arr"] == "06:09"
    assert trip["via_dep"] == "06:21"
    assert trip["via_arr_delay"] == 1
    assert trip["via_arr_status"] == "REAL"
