import argparse
import json
import tempfile
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import requests

from .download import download
from .extract import extract
from .stations import search_stations
from .window import merge, write_index, write_json


def main() -> None:
    parser = argparse.ArgumentParser(prog="sillon")
    sub = parser.add_subparsers(dest="command", required=True)

    yesterday = datetime.now(UTC).date() - timedelta(days=1)
    dl = sub.add_parser("download", help="download the istdaten CSV for one day")
    dl.add_argument("--date", type=date.fromisoformat, default=yesterday)
    dl.add_argument("--out", type=Path, default=Path("./tmp"))

    st = sub.add_parser("stations", help="search BPUIC/name for train stops in a CSV")
    st.add_argument("--csv", type=Path, required=True)
    st.add_argument("--search", required=True)

    ex = sub.add_parser("extract", help="extract tracked pairs from a CSV")
    ex.add_argument("--csv", type=Path, required=True)
    ex.add_argument("--pairs", type=Path, required=True)
    ex.add_argument("--out", type=Path)

    rn = sub.add_parser("run", help="download, extract, and merge one day into the rolling window")
    rn.add_argument("--date", type=date.fromisoformat, default=yesterday)
    rn.add_argument("--pairs", type=Path, required=True)
    rn.add_argument("--data", type=Path, required=True)
    rn.add_argument("--csv", type=Path, help="use this CSV instead of downloading")

    args = parser.parse_args()

    if args.command == "download":
        with requests.Session() as session:
            path = download(args.date, args.out, session)
        print(f"{path} ({path.stat().st_size} bytes)")

    elif args.command == "stations":
        for bpuic, name in search_stations(args.csv, args.search):
            print(f"{bpuic}\t{name}")

    elif args.command == "extract":
        pairs = json.loads(args.pairs.read_text(encoding="utf-8"))
        t0 = time.monotonic()
        result = extract(args.csv, pairs)
        elapsed = time.monotonic() - t0

        for pair_id in sorted(result):
            print(f"{pair_id}: {len(result[pair_id])} trains")
        print(f"extracted in {elapsed:.1f}s")

        if args.out:
            args.out.write_text(
                json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    elif args.command == "run":
        pairs = json.loads(args.pairs.read_text(encoding="utf-8"))
        t0 = time.monotonic()

        downloaded_csv = None
        if args.csv:
            csv_path = args.csv
        else:
            # never inside --data: a failed run must not leave 666 MB in the data branch
            with requests.Session() as session:
                csv_path = download(args.date, Path(tempfile.gettempdir()) / "sillon", session)
            downloaded_csv = csv_path

        extracted = extract(csv_path, pairs)

        for pair in pairs:
            pair_path = args.data / "pairs" / f"{pair['id']}.json"
            existing = None
            if pair_path.exists():
                existing = json.loads(pair_path.read_text(encoding="utf-8"))
            merged = merge(pair, args.date, extracted[pair["id"]], existing)
            write_json(pair_path, merged)

        days = write_index(args.data, pairs, datetime.now(UTC).date())

        if downloaded_csv:
            downloaded_csv.unlink()

        elapsed = time.monotonic() - t0
        print(f"{len(days)} days in window, done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
