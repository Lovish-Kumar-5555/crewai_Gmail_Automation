from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EmailPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RequestedAction(str, Enum):
    NOTIFY = "notify"
    DRAFT_REPLY = "draft_reply"
    ARCHIVE = "archive"
    DELETE = "delete"
    LABEL = "label"
    SKIP = "skip"
    EMPTY_TRASH = "empty_trash"


class DeleteConditions(BaseModel):
    age_days: int | None = None
    min_age_days: int | None = None
    has_required_age: bool = False
    age_threshold_met: bool = False
    priority_is_low: bool = False
    category_not_protected: bool = False
    sensitive_signal_present: bool = False
    classification_uncertain: bool = False


class PolicyValidationInput(BaseModel):
    email_id: str | None = None
    message_ref: str | None = None
    sender: str | None = None
    subject: str | None = None
    category: str | None = None
    priority: str | None = None
    requested_action: str
    age_days: int | None = None
    classification_confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    allowed: bool
    action: str
    email_id: str | None = None
    message_ref: str | None = None
    category: str | None = None
    priority: str | None = None
    reasons: list[str] = Field(default_factory=list)
    evaluated_conditions: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_log_payload(self, tool_name: str, executed: bool) -> dict[str, Any]:
        return {
            "tool": tool_name,
            "email_id": self.email_id,
            "message_ref": self.message_ref,
            "requested_action": self.action,
            "category": self.category,
            "priority": self.priority,
            "allowed": self.allowed,
            "executed": executed,
            "reasons": self.reasons,
            "evaluated_conditions": self.evaluated_conditions,
            "timestamp": self.timestamp,
        }
