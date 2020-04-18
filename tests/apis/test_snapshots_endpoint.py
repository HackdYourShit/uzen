import json

import pytest

from tests.utils import first_snapshot_id, make_snapshot_result
from uzen.models.snapshots import Snapshot
from uzen.services.browser import Browser


@pytest.mark.asyncio
async def test_snapshot_list(client):
    response = await client.get("/api/snapshots/")
    assert response.status_code == 200

    snapshots = response.json()
    assert isinstance(snapshots, list)


@pytest.mark.asyncio
async def test_snapshot_count(client):
    response = await client.get("/api/snapshots/count")
    assert response.status_code == 200

    data = response.json()
    count = data.get("count")
    assert isinstance(count, int)


@pytest.mark.asyncio
@pytest.mark.usefixtures("snapshots_setup")
async def test_snapshot_search(client):
    count = await Snapshot.all().count()
    response = await client.get("/api/snapshots/search")
    assert response.status_code == 200

    snapshots = response.json()
    assert len(snapshots) == count

    response = await client.get("/api/snapshots/search", params={"hostname": "example"})
    snapshots = response.json()
    assert len(snapshots) == count

    response = await client.get("/api/snapshots/search", params={"server": "ECS"})
    snapshots = response.json()
    assert len(snapshots) == count

    # it doesn't match any snapshot
    response = await client.get("/api/snapshots/search", params={"server": "Tomcat"})
    snapshots = response.json()
    assert len(snapshots) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("snapshots_setup")
async def test_snapshot_list_with_size(client):
    payload = {"size": 1}
    response = await client.get("/api/snapshots/", params=payload)
    assert response.status_code == 200

    snapshots = response.json()
    assert len(snapshots) == 1
    first = snapshots[0]
    assert first.get("url") == "http://example10.com/"


@pytest.mark.asyncio
@pytest.mark.usefixtures("snapshots_setup")
async def test_snapshot_list_with_offset_and_size(client):
    payload = {"offset": 0, "size": 1}
    response = await client.get("/api/snapshots/", params=payload)
    assert response.status_code == 200

    snapshots = response.json()
    assert len(snapshots) == 1

    offset = 0
    size = 10
    payload = {"offset": offset, "size": size}
    response = await client.get("/api/snapshots/", params=payload)
    snapshots = response.json()
    assert len(snapshots) == size - offset
    first = snapshots[0]
    assert first.get("url") == f"http://example{size - offset}.com/"

    offset = 5
    size = 100000
    payload = {"offset": offset, "size": size}
    response = await client.get("/api/snapshots/", params=payload)
    snapshots = response.json()
    assert len(snapshots) == await Snapshot.all().count() - offset
    first = snapshots[0]
    assert first.get("url") == f"http://example{offset}.com/"


@pytest.mark.asyncio
async def test_snapshot_post_without_url(client):
    payload = {}
    response = await client.post("/api/snapshots/", data=json.dumps(payload))
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_snapshot_post_with_invalid_url(client):
    payload = {"url": "foo"}
    response = await client.post("/api/snapshots/", data=json.dumps(payload))
    assert response.status_code == 422


def mock_take_snapshot(*args, **kwargs):
    return make_snapshot_result()


@pytest.mark.asyncio
@pytest.mark.usefixtures("snapshots_setup")
async def test_snapshot_post(client, monkeypatch):
    monkeypatch.setattr(Browser, "take_snapshot", mock_take_snapshot)

    payload = {"url": "http://example.com"}
    response = await client.post("/api/snapshots/", data=json.dumps(payload))

    assert response.status_code == 201

    snapshot = response.json()
    assert snapshot.get("url") == "http://example.com/"
    assert snapshot.get("body") == "foo bar"

    snapshot = await Snapshot.get(id=snapshot.get("id"))
    await snapshot.fetch_related("_scripts")
    assert len(snapshot.scripts) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("dns_records_setup")
async def test_snapshot_get_with_dns_records(client):
    id_ = await first_snapshot_id()
    response = await client.get(f"/api/snapshots/{id_}")
    assert response.status_code == 200

    snapshot = response.json()
    assert len(snapshot.get("dns_records")) == 1
    assert len(snapshot.get("scripts")) == 0
    assert len(snapshot.get("classifications")) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("classifications_setup")
async def test_snapshot_get_with_classifications(client):
    id_ = await first_snapshot_id()
    response = await client.get(f"/api/snapshots/{id_}")
    assert response.status_code == 200

    snapshot = response.json()
    assert len(snapshot.get("classifications")) == 1
    assert len(snapshot.get("dns_records")) == 0
    assert len(snapshot.get("scripts")) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("scripts_setup")
async def test_snapshot_get_with_scripts(client):
    id_ = await first_snapshot_id()
    response = await client.get(f"/api/snapshots/{id_}")
    assert response.status_code == 200

    snapshot = response.json()
    assert len(snapshot.get("scripts")) == 1
    assert len(snapshot.get("classifications")) == 0
    assert len(snapshot.get("dns_records")) == 0
