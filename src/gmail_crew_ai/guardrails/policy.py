from __future__ import annotations

from typing import Any

from gmail_crew_ai.guardrails.config import PolicyConfig
from gmail_crew_ai.guardrails.models import DeleteConditions


def normalize_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized


def normalize_category(category: str | None, config: PolicyConfig) -> str | None:
    raw = normalize_value(category)
    if raw is None:
        return None
    upper = raw.upper()
    return config.category_aliases.get(upper, upper)


def normalize_priority(priority: str | None) -> str | None:
    raw = normalize_value(priority)
    if raw is None:
        return None
    return raw.upper()


def normalize_action(action: str | None, config: PolicyConfig) -> str | None:
    raw = normalize_value(action)
    if raw is None:
        return None
    lowered = raw.lower()
    return config.action_aliases.get(lowered, lowered)


def contains_sensitive_signal(
    sender: str | None,
    subject: str | None,
    keywords: tuple[str, ...],
) -> bool:
    text = f"{sender or ''} {subject or ''}".lower()
    return any(keyword in text for keyword in keywords)


def build_delete_conditions(
    *,
    age_days: int | None,
    min_age_days: int,
    priority: str | None,
    category: str | None,
    non_deletable_categories: set[str],
    sender: str | None,
    subject: str | None,
    confidence: float | None,
    confidence_threshold: float,
    invoice_keywords: tuple[str, ...],
    personal_keywords: tuple[str, ...],
) -> DeleteConditions:
    has_required_age = isinstance(age_days, int)
    age_threshold_met = has_required_age and age_days >= min_age_days
    priority_is_low = priority == "LOW"
    category_not_protected = bool(category) and category not in non_deletable_categories
    sensitive_signal_present = contains_sensitive_signal(
        sender, subject, invoice_keywords
    ) or contains_sensitive_signal(sender, subject, personal_keywords)
    classification_uncertain = (
        confidence is None or confidence < confidence_threshold or category in {"OTHER", "UNCATEGORIZED"}
    )

    return DeleteConditions(
        age_days=age_days if isinstance(age_days, int) else None,
        min_age_days=min_age_days,
        has_required_age=has_required_age,
        age_threshold_met=age_threshold_met,
        priority_is_low=priority_is_low,
        category_not_protected=category_not_protected,
        sensitive_signal_present=sensitive_signal_present,
        classification_uncertain=classification_uncertain,
    )


def merge_conditions(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    merged.update(extra)
    return merged
