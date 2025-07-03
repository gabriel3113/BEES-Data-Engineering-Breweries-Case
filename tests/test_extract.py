import responses, json, os
from src.extract import fetch_breweries, API_URL

@responses.activate
def test_fetch_breweries(tmp_path, monkeypatch):
    # mock 2 páginas
    page1 = [{"id": 1, "name": "Foo"}]
    page2 = []  # página vazia encerra
    responses.add(responses.GET, API_URL, json=page1, status=200)
    responses.add(responses.GET, API_URL, json=page2, status=200)

    monkeypatch.setenv("DATA_DIR", tmp_path.as_posix())
    fetch_breweries()

    files = list(tmp_path.glob("**/*.json"))
    assert len(files) == 1
    with open(files[0]) as f:
        assert json.load(f) == page1