__all__ = [
    "MetricOverTimePatch",
    "MetricOverTimeUpdate",
    "MetricOverTimeCreate",
    "MetricOverTime",
    "MetricsOverTime",
]
import datetime
import uuid

from pydantic import constr

from .base import Base, BaseRoot


class MetricOverTimePatch(Base):
    timestamp: datetime.datetime | None = None
    name: constr(strip_whitespace=True, max_length=128) | None = None
    values: dict[str, float | None] | None = None


class MetricOverTimeUpdate(MetricOverTimePatch):
    timestamp: datetime.datetime
    name: constr(strip_whitespace=True, max_length=128)
    values: dict[str, float | None]


class MetricOverTimeCreate(MetricOverTimeUpdate):
    id: uuid.UUID | None = None
    test_run_id: uuid.UUID
    test_id: uuid.UUID | None = None


class MetricOverTime(MetricOverTimeCreate):
    id: uuid.UUID


class MetricsOverTime(BaseRoot):
    root: list[MetricOverTime]
