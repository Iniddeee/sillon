import argparse
import json
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import requests

from .download import download
from .extract import extract
from .stations import search_stations


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


if __name__ == "__main__":
    main()
