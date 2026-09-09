import argparse
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import requests

from .download import download


def main() -> None:
    parser = argparse.ArgumentParser(prog="sillon")
    sub = parser.add_subparsers(dest="command", required=True)

    yesterday = datetime.now(UTC).date() - timedelta(days=1)
    dl = sub.add_parser("download", help="download the istdaten CSV for one day")
    dl.add_argument("--date", type=date.fromisoformat, default=yesterday)
    dl.add_argument("--out", type=Path, default=Path("./tmp"))

    args = parser.parse_args()

    if args.command == "download":
        with requests.Session() as session:
            path = download(args.date, args.out, session)
        print(f"{path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
