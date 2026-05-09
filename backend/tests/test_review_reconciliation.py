import pytest
from uuid import uuid4

from httpx import AsyncClient, ASGITransport

from domain.human_review.models import ReviewQueueItem
from main import app


AUTH_HEADERS = {
    "X-Internal-Token": "test-token",
    "X-User-Id": "user-001",
    "X-Organization-Id": "org-001",
}


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    monkeypatch.setenv("BACKEND_INTERNAL_TOKEN", "test-token")


@pytest.fixture
def production_id():
    return uuid4()


@pytest.fixture
def scene_id():
    return uuid4()


@pytest.fixture
def asset_id():
    return uuid4()


async def _add_item(session_factory, production_id, scene_id=None, asset_id=None):
    from infrastructure.db.review_repository import ReviewRepository

    scene_id = scene_id or uuid4()
    asset_id = asset_id or uuid4()
    async with session_factory() as session:
        repo = ReviewRepository(session)
        item = ReviewQueueItem(
            production_id=production_id,
            scene_id=scene_id,
            asset_id=asset_id,
        )
        result = await repo.save_item(item)
        await session.commit()
    return result


@pytest.mark.asyncio
async def test_get_review_returns_canonical_payload(production_id, scene_id, asset_id, db_session_factory):
    await _add_item(db_session_factory, production_id, scene_id, asset_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/review/{production_id}",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] == 1

    returned = data["items"][0]
    assert returned["production_id"] == str(production_id)
    assert returned["scene_id"] == str(scene_id)
    assert returned["asset_id"] == str(asset_id)
    assert "scene_index" in returned
    assert "scene_label" in returned
    assert "score" in returned
    assert "justification" in returned
    assert "decision" in returned
    assert "status" in returned
    assert "preview_url" in returned
    assert "asset_url" in returned
    assert "asset_type" in returned
    assert "source" in returned
    assert returned["status"] == "pending"


@pytest.mark.asyncio
async def test_get_review_empty_queue(production_id, db_session_factory):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/review/{production_id}",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total_count"] == 0


@pytest.mark.asyncio
async def test_approve_action(production_id, scene_id, asset_id, db_session_factory):
    item = await _add_item(db_session_factory, production_id, scene_id, asset_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{production_id}/{item.id}/approve",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_reject_action(production_id, scene_id, asset_id, db_session_factory):
    item = await _add_item(db_session_factory, production_id, scene_id, asset_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{production_id}/{item.id}/reject",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_requery_action(production_id, scene_id, asset_id, db_session_factory):
    item = await _add_item(db_session_factory, production_id, scene_id, asset_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{production_id}/{item.id}/requery",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "requeried"


@pytest.mark.asyncio
async def test_approve_nonexistent_returns_404(production_id, db_session_factory):
    fake_id = uuid4()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{production_id}/{fake_id}/approve",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reject_nonexistent_returns_404(production_id, db_session_factory):
    fake_id = uuid4()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{production_id}/{fake_id}/reject",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_requery_nonexistent_returns_404(production_id, db_session_factory):
    fake_id = uuid4()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{production_id}/{fake_id}/requery",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_review_requires_auth(production_id, db_session_factory):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/review/{production_id}")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_multiple_items_for_same_production(production_id, db_session_factory):
    await _add_item(db_session_factory, production_id)
    await _add_item(db_session_factory, production_id)
    await _add_item(db_session_factory, production_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/review/{production_id}",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_items_isolated_across_productions(db_session_factory):
    prod_a = uuid4()
    prod_b = uuid4()
    await _add_item(db_session_factory, prod_a)
    await _add_item(db_session_factory, prod_a)
    await _add_item(db_session_factory, prod_b)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp_a = await client.get(f"/review/{prod_a}", headers=AUTH_HEADERS)
        resp_b = await client.get(f"/review/{prod_b}", headers=AUTH_HEADERS)

    assert resp_a.json()["total_count"] == 2
    assert resp_b.json()["total_count"] == 1


@pytest.mark.asyncio
async def test_approved_item_not_in_pending_list(production_id, scene_id, asset_id, db_session_factory):
    item = await _add_item(db_session_factory, production_id, scene_id, asset_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            f"/review/{production_id}/{item.id}/approve",
            headers=AUTH_HEADERS,
        )
        resp = await client.get(f"/review/{production_id}", headers=AUTH_HEADERS)

    assert resp.json()["total_count"] == 0
