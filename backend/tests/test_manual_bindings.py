import pytest
from fastapi.testclient import TestClient

TEST_INTERNAL_TOKEN = "test-internal-token-12345"


def _create_production(client: TestClient, auth_headers: dict, **overrides) -> str:
    payload = {
        "title": "Binding Test Production",
        "template_type_id": "videodoc_narrated",
        "variation_id": "1",
        "mode": "manual",
    }
    payload.update(overrides)
    response = client.post("/productions/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json()["id"]


class TestCreateBinding:
    def test_create_binding_returns_201(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 0,
                "asset_reference": "https://example.com/asset.jpg",
                "asset_type": "image",
                "restrictions": ["no text overlay"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["production_id"] == production_id
        assert data["scene_index"] == 0
        assert data["asset_reference"] == "https://example.com/asset.jpg"
        assert data["asset_type"] == "image"
        assert data["bound_by"] == "test-user-001"
        assert "id" in data
        assert "created_at" in data

    def test_create_binding_with_video_type(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 1,
                "asset_reference": "https://example.com/clip.mp4",
                "asset_type": "video",
                "restrictions": [],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["asset_type"] == "video"

    def test_create_binding_invalid_asset_type(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 0,
                "asset_reference": "https://example.com/asset.jpg",
                "asset_type": "audio",
                "restrictions": [],
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_binding_requires_auth(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 0,
                "asset_reference": "https://example.com/asset.jpg",
                "asset_type": "image",
                "restrictions": [],
            },
        )
        assert response.status_code == 401

    def test_create_binding_nonexistent_production(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/00000000-0000-0000-0000-000000000000/bindings",
            json={
                "production_id": "00000000-0000-0000-0000-000000000000",
                "scene_index": 0,
                "asset_reference": "https://example.com/asset.jpg",
                "asset_type": "image",
                "restrictions": [],
            },
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestListBindings:
    def test_list_bindings_empty(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.get(
            f"/productions/{production_id}/bindings",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["bindings"] == []

    def test_list_bindings_returns_created(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 0,
                "asset_reference": "https://example.com/a.jpg",
                "asset_type": "image",
                "restrictions": [],
            },
            headers=auth_headers,
        )
        client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 1,
                "asset_reference": "https://example.com/b.mp4",
                "asset_type": "video",
                "restrictions": ["landscape only"],
            },
            headers=auth_headers,
        )
        response = client.get(
            f"/productions/{production_id}/bindings",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    def test_list_bindings_requires_auth(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.get(
            f"/productions/{production_id}/bindings",
        )
        assert response.status_code == 401


class TestDeleteBinding:
    def test_delete_binding_returns_200(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        create_response = client.post(
            f"/productions/{production_id}/bindings",
            json={
                "production_id": production_id,
                "scene_index": 0,
                "asset_reference": "https://example.com/asset.jpg",
                "asset_type": "image",
                "restrictions": [],
            },
            headers=auth_headers,
        )
        binding_id = create_response.json()["id"]

        response = client.delete(
            f"/productions/{production_id}/bindings/{binding_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["deleted"] == binding_id

    def test_delete_nonexistent_binding_returns_404(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.delete(
            f"/productions/{production_id}/bindings/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_delete_binding_requires_auth(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_id = _create_production(client, auth_headers)
        response = client.delete(
            f"/productions/{production_id}/bindings/00000000-0000-0000-0000-000000000000",
        )
        assert response.status_code == 401


class TestBindingsIsolatedByProduction:
    def test_bindings_are_scoped_to_production(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        production_a = _create_production(client, auth_headers, title="Production A")
        production_b = _create_production(client, auth_headers, title="Production B")

        client.post(
            f"/productions/{production_a}/bindings",
            json={
                "production_id": production_a,
                "scene_index": 0,
                "asset_reference": "https://example.com/a.jpg",
                "asset_type": "image",
                "restrictions": [],
            },
            headers=auth_headers,
        )

        response_b = client.get(
            f"/productions/{production_b}/bindings",
            headers=auth_headers,
        )
        assert response_b.status_code == 200
        assert response_b.json()["count"] == 0

        response_a = client.get(
            f"/productions/{production_a}/bindings",
            headers=auth_headers,
        )
        assert response_a.status_code == 200
        assert response_a.json()["count"] == 1
