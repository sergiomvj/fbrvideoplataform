import os
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from application.events.domain_events import (
    DomainEvent,
    EventBus,
    PRODUCTION_CREATED,
    PRODUCTION_STRUCTURED,
    PRODUCTION_VISUAL_PLANNED,
    PRODUCTION_MEDIA_SOURCED,
    PRODUCTION_CONTEXT_VERIFIED,
    PRODUCTION_HUMAN_REVIEW_REQUIRED,
    PRODUCTION_HUMAN_REVIEW_COMPLETED,
    PRODUCTION_COMPOSED,
    PRODUCTION_RENDER_SUBMITTED,
    PRODUCTION_RENDER_COMPLETED,
    PRODUCTION_RENDER_FAILED,
    PRODUCTION_FAILED,
)
from integrations.openclaw.hooks import (
    OpenClawWebhookPayload,
    create_webhook_payload,
    _webhook_log,
)
from integrations.fbr_click.notifier import (
    FBRClickNotification,
    NotificationMapper,
    _notifications_store,
)
from api.routes.productions import _event_bus


@pytest.fixture(autouse=True)
def _clear_stores():
    _webhook_log.clear()
    _notifications_store.clear()


class TestDomainEvent:
    def test_domain_event_creation(self) -> None:
        pid = uuid4()
        event = DomainEvent(
            event_type=PRODUCTION_CREATED,
            production_id=pid,
            payload={"title": "Test"},
            source="test",
        )
        assert event.event_type == PRODUCTION_CREATED
        assert event.production_id == pid
        assert event.payload == {"title": "Test"}
        assert event.source == "test"
        assert isinstance(event.timestamp, datetime)

    def test_domain_event_defaults(self) -> None:
        event = DomainEvent(event_type=PRODUCTION_FAILED)
        assert event.production_id is None
        assert event.payload == {}
        assert event.source == "synkra-backend"
        assert event.timestamp.tzinfo == timezone.utc

    def test_domain_event_is_frozen(self) -> None:
        event = DomainEvent(event_type=PRODUCTION_CREATED)
        with pytest.raises(AttributeError):
            event.event_type = "other"


class TestEventBus:
    @pytest.mark.asyncio
    async def test_subscribe_and_emit(self) -> None:
        bus = EventBus()
        received: list[DomainEvent] = []

        async def handler(event: DomainEvent) -> None:
            received.append(event)

        bus.subscribe(PRODUCTION_CREATED, handler)
        event = DomainEvent(event_type=PRODUCTION_CREATED, production_id=uuid4())
        await bus.emit(event)
        assert len(received) == 1
        assert received[0] == event

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self) -> None:
        bus = EventBus()
        results_a: list[DomainEvent] = []
        results_b: list[DomainEvent] = []

        async def handler_a(event: DomainEvent) -> None:
            results_a.append(event)

        async def handler_b(event: DomainEvent) -> None:
            results_b.append(event)

        bus.subscribe(PRODUCTION_CREATED, handler_a)
        bus.subscribe(PRODUCTION_CREATED, handler_b)
        event = DomainEvent(event_type=PRODUCTION_CREATED)
        await bus.emit(event)
        assert len(results_a) == 1
        assert len(results_b) == 1

    @pytest.mark.asyncio
    async def test_emit_with_no_subscribers(self) -> None:
        bus = EventBus()
        event = DomainEvent(event_type=PRODUCTION_RENDER_FAILED)
        await bus.emit(event)

    @pytest.mark.asyncio
    async def test_subscribers_only_receive_matching_events(self) -> None:
        bus = EventBus()
        received: list[DomainEvent] = []

        async def handler(event: DomainEvent) -> None:
            received.append(event)

        bus.subscribe(PRODUCTION_CREATED, handler)
        await bus.emit(DomainEvent(event_type=PRODUCTION_FAILED))
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_known_event_type_constants(self) -> None:
        expected = [
            PRODUCTION_CREATED,
            PRODUCTION_STRUCTURED,
            PRODUCTION_VISUAL_PLANNED,
            PRODUCTION_MEDIA_SOURCED,
            PRODUCTION_CONTEXT_VERIFIED,
            PRODUCTION_HUMAN_REVIEW_REQUIRED,
            PRODUCTION_HUMAN_REVIEW_COMPLETED,
            PRODUCTION_COMPOSED,
            PRODUCTION_RENDER_SUBMITTED,
            PRODUCTION_RENDER_COMPLETED,
            PRODUCTION_RENDER_FAILED,
            PRODUCTION_FAILED,
        ]
        assert len(expected) == 12
        assert len(set(expected)) == 12


class TestNotificationMapper:
    def test_map_human_review_required(self) -> None:
        mapper = NotificationMapper()
        pid = uuid4()
        event = DomainEvent(
            event_type=PRODUCTION_HUMAN_REVIEW_REQUIRED,
            production_id=pid,
        )
        result = mapper.map_event(event)
        assert result is not None
        assert isinstance(result, FBRClickNotification)
        assert result.title == "Review Required"
        assert result.severity == "warning"
        assert result.channel == "fbr_click"
        assert result.production_id == str(pid)

    def test_map_render_completed(self) -> None:
        mapper = NotificationMapper()
        event = DomainEvent(
            event_type=PRODUCTION_RENDER_COMPLETED,
            production_id=uuid4(),
        )
        result = mapper.map_event(event)
        assert result is not None
        assert result.title == "Render Completed"
        assert result.severity == "info"

    def test_map_render_failed(self) -> None:
        mapper = NotificationMapper()
        event = DomainEvent(
            event_type=PRODUCTION_RENDER_FAILED,
            production_id=uuid4(),
        )
        result = mapper.map_event(event)
        assert result is not None
        assert result.title == "Render Failed"
        assert result.severity == "critical"

    def test_map_production_failed(self) -> None:
        mapper = NotificationMapper()
        event = DomainEvent(
            event_type=PRODUCTION_FAILED,
            production_id=uuid4(),
        )
        result = mapper.map_event(event)
        assert result is not None
        assert result.title == "Production Failed"
        assert result.severity == "critical"

    def test_map_human_review_completed(self) -> None:
        mapper = NotificationMapper()
        event = DomainEvent(
            event_type=PRODUCTION_HUMAN_REVIEW_COMPLETED,
            production_id=uuid4(),
        )
        result = mapper.map_event(event)
        assert result is not None
        assert result.title == "Review Completed"
        assert result.severity == "info"

    def test_returns_none_for_non_relevant_events(self) -> None:
        mapper = NotificationMapper()
        non_relevant = [
            PRODUCTION_CREATED,
            PRODUCTION_STRUCTURED,
            PRODUCTION_VISUAL_PLANNED,
            PRODUCTION_MEDIA_SOURCED,
            PRODUCTION_CONTEXT_VERIFIED,
            PRODUCTION_COMPOSED,
            PRODUCTION_RENDER_SUBMITTED,
        ]
        for event_type in non_relevant:
            event = DomainEvent(event_type=event_type, production_id=uuid4())
            assert mapper.map_event(event) is None, f"{event_type} should not map"

    def test_notification_stored(self) -> None:
        mapper = NotificationMapper()
        event = DomainEvent(
            event_type=PRODUCTION_RENDER_FAILED,
            production_id=uuid4(),
        )
        mapper.map_event(event)
        assert len(_notifications_store) == 1
        assert _notifications_store[0]["severity"] == "critical"


class TestOpenClawWebhookPayload:
    def test_create_webhook_payload(self) -> None:
        pid = uuid4()
        event = DomainEvent(
            event_type=PRODUCTION_CREATED,
            production_id=pid,
            payload={"title": "Test"},
        )
        payload = create_webhook_payload(event)
        assert isinstance(payload, OpenClawWebhookPayload)
        assert payload.event_type == PRODUCTION_CREATED
        assert payload.production_id == str(pid)
        assert payload.summary == "Production created"
        assert payload.suggested_action == "none"

    def test_webhook_payload_with_suggested_action(self) -> None:
        event = DomainEvent(
            event_type=PRODUCTION_HUMAN_REVIEW_REQUIRED,
            production_id=uuid4(),
        )
        payload = create_webhook_payload(event)
        assert payload.suggested_action == "assign_reviewer"

    def test_webhook_payload_render_failed_action(self) -> None:
        event = DomainEvent(
            event_type=PRODUCTION_RENDER_FAILED,
            production_id=uuid4(),
        )
        payload = create_webhook_payload(event)
        assert payload.suggested_action == "retry_or_investigate"

    def test_webhook_payload_failed_action(self) -> None:
        event = DomainEvent(
            event_type=PRODUCTION_FAILED,
            production_id=uuid4(),
        )
        payload = create_webhook_payload(event)
        assert payload.suggested_action == "investigate_failure"

    def test_webhook_payload_render_completed_action(self) -> None:
        event = DomainEvent(
            event_type=PRODUCTION_RENDER_COMPLETED,
            production_id=uuid4(),
        )
        payload = create_webhook_payload(event)
        assert payload.suggested_action == "notify_stakeholders"

    def test_webhook_payload_none_production_id(self) -> None:
        event = DomainEvent(event_type=PRODUCTION_FAILED)
        payload = create_webhook_payload(event)
        assert payload.production_id is None

    def test_webhook_log_appended(self) -> None:
        event = DomainEvent(
            event_type=PRODUCTION_CREATED,
            production_id=uuid4(),
        )
        create_webhook_payload(event)
        assert len(_webhook_log) == 1
        assert _webhook_log[0]["event_type"] == PRODUCTION_CREATED

    def test_all_event_types_have_summaries(self) -> None:
        all_types = [
            PRODUCTION_CREATED,
            PRODUCTION_STRUCTURED,
            PRODUCTION_VISUAL_PLANNED,
            PRODUCTION_MEDIA_SOURCED,
            PRODUCTION_CONTEXT_VERIFIED,
            PRODUCTION_HUMAN_REVIEW_REQUIRED,
            PRODUCTION_HUMAN_REVIEW_COMPLETED,
            PRODUCTION_COMPOSED,
            PRODUCTION_RENDER_SUBMITTED,
            PRODUCTION_RENDER_COMPLETED,
            PRODUCTION_RENDER_FAILED,
            PRODUCTION_FAILED,
        ]
        for et in all_types:
            event = DomainEvent(event_type=et, production_id=uuid4())
            payload = create_webhook_payload(event)
            assert payload.summary != et


AUTH_HEADERS = {
    "X-User-Id": "test-user-001",
    "X-Organization-Id": "default",
    "X-Internal-Token": "test-internal-token-12345",
}


class TestEventEmissionOnProductionCreation:
    def test_emit_production_created_event(self, client) -> None:
        collected: list[DomainEvent] = []

        async def collector(event: DomainEvent) -> None:
            collected.append(event)

        _event_bus.subscribe(PRODUCTION_CREATED, collector)

        response = client.post(
            "/productions/",
            json={
                "title": "Event Test Production",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 201

        assert len(collected) >= 1
        created_events = [e for e in collected if e.event_type == PRODUCTION_CREATED]
        assert len(created_events) >= 1
        assert created_events[0].payload["title"] == "Event Test Production"

    def test_manual_event_emit_endpoint(self, client) -> None:
        create_resp = client.post(
            "/productions/",
            json={
                "title": "Manual Emit Test",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=AUTH_HEADERS,
        )
        production_id = create_resp.json()["id"]

        emit_resp = client.post(
            f"/productions/{production_id}/events",
            json={
                "event_type": "production.human_review_required",
                "payload": {"reason": "manual test"},
            },
            headers=AUTH_HEADERS,
        )
        assert emit_resp.status_code == 200
        data = emit_resp.json()
        assert data["emitted_event"]["event_type"] == "production.human_review_required"
        assert data["emitted_event"]["production_id"] == production_id
        assert data["notification"] is not None
        assert data["notification"]["severity"] == "warning"

    def test_manual_event_emit_non_relevant_returns_none_notification(self, client) -> None:
        create_resp = client.post(
            "/productions/",
            json={
                "title": "Non Relevant Event",
                "template_type_id": "presenter_short",
                "variation_id": "1",
                "mode": "automatic",
            },
            headers=AUTH_HEADERS,
        )
        production_id = create_resp.json()["id"]

        emit_resp = client.post(
            f"/productions/{production_id}/events",
            json={
                "event_type": "production.media_sourced",
                "payload": {},
            },
            headers=AUTH_HEADERS,
        )
        assert emit_resp.status_code == 200
        data = emit_resp.json()
        assert data["notification"] is None

    def test_emit_event_nonexistent_production(self, client) -> None:
        emit_resp = client.post(
            "/productions/nonexistent-id/events",
            json={
                "event_type": "production.failed",
                "payload": {},
            },
            headers=AUTH_HEADERS,
        )
        assert emit_resp.status_code == 404
