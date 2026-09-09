import json
import re
from datetime import date
from pathlib import Path

DATASET_URL = "https://data.opentransportdata.swiss/dataset/ist-daten-v2"
CHUNK_SIZE = 1024 * 1024

# CKAN's package_show API returns 403 from here; the dataset page embeds the
# same resource list as schema.org JSON-LD, so we parse that instead.
_LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


def resource_url(day: date, session) -> str:
    resp = session.get(DATASET_URL)
    resp.raise_for_status()
    match = _LD_JSON.search(resp.text)
    if match is None:
        raise ValueError(f"no ld+json block on {DATASET_URL}")

    graph = json.loads(match.group(1))["@graph"]
    ident = f"{day.isoformat()}_IstDaten.csv"
    for node in graph:
        types = node.get("@type", [])
        if "schema:Distribution" in types and node.get("dcterms:identifier") == ident:
            return node["schema:url"]

    raise ValueError(f"no istdaten resource for {day.isoformat()} (dataset window is ~50 days)")


def download(day: date, dest: Path, session) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{day.isoformat()}_istdaten.csv"

    # resolved right before the GET: this link 302s to a Cloudflare-signed
    # URL valid ~60s; requests follows it inline, so there's nothing to cache
    url = resource_url(day, session)

    with session.get(url, stream=True) as resp:
        resp.raise_for_status()
        expected = int(resp.headers["Content-Length"])
        written = 0
        with open(out, "wb") as f:
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
                written += len(chunk)

    if written != expected:
        raise ValueError(f"{out.name}: got {written} bytes, expected {expected}")
    return out
