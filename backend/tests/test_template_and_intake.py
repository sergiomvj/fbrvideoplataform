import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    from api.routes.productions import _productions_store
    _productions_store.clear()
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-User-Id": "test-user-001"}


class TestTemplateRegistry:
    def test_list_templates(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/templates/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) == 2

    def test_template_has_expected_fields(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/templates/", headers=auth_headers)
        data = response.json()
        presenter = next(t for t in data["templates"] if t["type_id"] == "presenter_short")
        assert presenter["name"] == "Presenter Short"
        assert presenter["aspect_ratio"] == "9:16"
        assert presenter["resolution"] == "hd"
        assert presenter["max_duration_seconds"] == 60
        assert presenter["supports_broll"] is False
        assert len(presenter["variations"]) == 3

    def test_get_presenter_short(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/templates/presenter_short", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["type_id"] == "presenter_short"
        assert data["max_duration_seconds"] == 60

    def test_get_videodoc_narrated(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/templates/videodoc_narrated", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["type_id"] == "videodoc_narrated"
        assert data["max_duration_seconds"] == 180
        assert data["supports_broll"] is True
        assert "video" in data["supported_asset_types"]

    def test_get_nonexistent_template(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/templates/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_templates_require_auth(self, client: TestClient) -> None:
        response = client.get("/templates/")
        assert response.status_code == 401


class TestProductionIntake:
    def test_create_automatic_production(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "Test News Video",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
                "base_content": "Breaking news content here",
                "editorial_context": "Urgent news",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test News Video"
        assert data["mode"] == "automatic"
        assert data["current_state"] == "intake"
        assert data["template_type_id"] == "presenter_short"
        assert data["variation_id"] == "1"
        assert data["operator_user_id"] == "test-user-001"
        assert len(data["state_history"]) == 1

    def test_create_manual_production(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "Manual Video",
                "template_type_id": "videodoc_narrated",
                "variation_id": "2",
                "mode": "manual",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "manual"
        assert data["template_type_id"] == "videodoc_narrated"

    def test_create_production_invalid_template(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "Bad Template",
                "template_type_id": "nonexistent",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_create_production_invalid_variation(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "Bad Variation",
                "template_type_id": "presenter_short",
                "variation_id": "99",
                "mode": "automatic",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_create_production_invalid_mode(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "Bad Mode",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "hybrid",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_production_requires_auth(self, client: TestClient) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "No Auth",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
        )
        assert response.status_code == 401

    def test_list_productions_filters_by_user(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        client.post(
            "/productions/",
            json={
                "title": "User 1 Production",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=auth_headers,
        )
        other_headers = {"X-User-Id": "other-user"}
        client.post(
            "/productions/",
            json={
                "title": "User 2 Production",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=other_headers,
        )

        response = client.get("/productions/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["productions"][0]["operator_user_id"] == "test-user-001"

    def test_get_production_by_id(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        create_response = client.post(
            "/productions/",
            json={
                "title": "Fetchable Production",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=auth_headers,
        )
        production_id = create_response.json()["id"]

        response = client.get(f"/productions/{production_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Fetchable Production"

    def test_get_nonexistent_production(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.get("/productions/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_cannot_access_other_users_production(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        create_response = client.post(
            "/productions/",
            json={
                "title": "Private Production",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=auth_headers,
        )
        production_id = create_response.json()["id"]

        other_headers = {"X-User-Id": "other-user"}
        response = client.get(f"/productions/{production_id}", headers=other_headers)
        assert response.status_code == 404

    def test_create_with_restrictions(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/productions/",
            json={
                "title": "Restricted",
                "template_type_id": "videodoc_narrated",
                "variation_id": "3",
                "mode": "manual",
                "restrictions": ["no violence", "no political imagery"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["restrictions"]) == 2
