import json
from datetime import date
from pathlib import Path

import pytest

from sillon.download import DATASET_URL, download, resource_url

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, text="", content=b"", headers=None):
        self.text = text
        self._content = content
        self.headers = headers or {}

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size):
        for i in range(0, len(self._content), chunk_size):
            yield self._content[i : i + chunk_size]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeSession:
    def __init__(self, responses):
        self.responses = responses

    def get(self, url, **kwargs):
        return self.responses[url]


def dataset_page_text() -> str:
    graph = json.loads((FIXTURES / "dataset_page.json").read_text(encoding="utf-8"))
    return f'<html><script type="application/ld+json">{json.dumps(graph)}</script></html>'


def test_resource_url_finds_known_day():
    session = FakeSession({DATASET_URL: FakeResponse(text=dataset_page_text())})
    url = resource_url(date(2026, 7, 22), session)
    assert url.endswith("/download/2026-07-22_istdaten.csv")


def test_resource_url_missing_day_raises():
    session = FakeSession({DATASET_URL: FakeResponse(text=dataset_page_text())})
    with pytest.raises(ValueError, match="no istdaten resource"):
        resource_url(date(2026, 1, 1), session)


def test_download_writes_file_and_checks_size(tmp_path):
    session = FakeSession({DATASET_URL: FakeResponse(text=dataset_page_text())})
    url = resource_url(date(2026, 7, 22), session)

    body = b"a" * 5000
    session.responses[url] = FakeResponse(content=body, headers={"Content-Length": str(len(body))})

    out = download(date(2026, 7, 22), tmp_path, session)
    assert out.name == "2026-07-22_istdaten.csv"
    assert out.read_bytes() == body


def test_download_size_mismatch_raises(tmp_path):
    session = FakeSession({DATASET_URL: FakeResponse(text=dataset_page_text())})
    url = resource_url(date(2026, 7, 22), session)

    body = b"a" * 5000
    session.responses[url] = FakeResponse(content=body, headers={"Content-Length": "9999"})

    with pytest.raises(ValueError, match="got 5000 bytes"):
        download(date(2026, 7, 22), tmp_path, session)
