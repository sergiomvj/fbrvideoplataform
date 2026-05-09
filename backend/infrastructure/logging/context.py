from contextvars import ContextVar
from typing import Optional
from dataclasses import dataclass, field

_logging_context: ContextVar[dict] = ContextVar("logging_context", default={})


@dataclass
class LoggingContext:
    production_id: Optional[str] = None
    scene_id: Optional[str] = None
    asset_id: Optional[str] = None
    render_job_id: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    request_id: Optional[str] = None

    def to_dict(self) -> dict:
        result = {}
        if self.production_id:
            result["production_id"] = self.production_id
        if self.scene_id:
            result["scene_id"] = self.scene_id
        if self.asset_id:
            result["asset_id"] = self.asset_id
        if self.render_job_id:
            result["render_job_id"] = self.render_job_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.organization_id:
            result["organization_id"] = self.organization_id
        if self.request_id:
            result["request_id"] = self.request_id
        return result

    def update_context(self) -> None:
        current = _logging_context.get()
        _logging_context.set({**current, **self.to_dict()})

    def clear(self) -> None:
        _logging_context.set({})

    def __enter__(self):
        self.update_context()
        return self

    def __exit__(self, *args):
        self.clear()


def get_context() -> dict:
    return _logging_context.get().copy()


def merge_context(extra: dict) -> dict:
    current = get_context()
    return {**current, **extra}