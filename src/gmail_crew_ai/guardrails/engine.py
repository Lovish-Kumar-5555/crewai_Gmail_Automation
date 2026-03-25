from __future__ import annotations

import json
import logging
from typing import Any

from gmail_crew_ai.guardrails.config import DEFAULT_POLICY_CONFIG, PolicyConfig
from gmail_crew_ai.guardrails.models import PolicyValidationInput, ValidationResult
from gmail_crew_ai.guardrails.policy import (
    build_delete_conditions,
    merge_conditions,
    normalize_action,
    normalize_category,
    normalize_priority,
)

_LOGGER = logging.getLogger("gmail_crew_ai.guardrails")
if not _LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    _LOGGER.addHandler(handler)
_LOGGER.setLevel(logging.INFO)


def _json_log(payload: dict[str, Any], blocked: bool) -> None:
    line = json.dumps(payload, default=str)
    if blocked:
        _LOGGER.warning(line)
    else:
        _LOGGER.info(line)


def validate_action(
    request: PolicyValidationInput,
    policy_config: PolicyConfig | None = None,
) -> ValidationResult:
    """
    Central policy validator.

    Fail-closed behavior:
    - Missing required fields for an action => blocked
    - Unknown category/priority/action => blocked
    - Unevaluable delete conditions => blocked
    """
    config = policy_config or DEFAULT_POLICY_CONFIG
    reasons: list[str] = []
    raw_action = request.requested_action
    action = normalize_action(raw_action, config)
    category = normalize_category(request.category, config)
    priority = normalize_priority(request.priority)
    conditions: dict[str, Any] = {
        "raw_action": raw_action,
        "normalized_action": action,
        "raw_category": request.category,
        "normalized_category": category,
        "raw_priority": request.priority,
        "normalized_priority": priority,
        "is_destructive": action in config.destructive_actions if action else False,
    }

    if not action:
        reasons.append("Missing requested_action; fail-closed.")
    elif action not in config.allowed_actions:
        reasons.append(f"Unknown or disallowed action '{action}'.")

    # Unknown values are blocked even for non-destructive actions.
    if request.category is not None and category not in config.allowed_categories:
        reasons.append(f"Unknown category '{request.category}'.")
    if request.priority is not None and priority not in config.allowed_priorities:
        reasons.append(f"Unknown priority '{request.priority}'.")

    # Category/priority are required for all user-email actions unless action is explicitly
    # allowed for uncategorized/default handling.
    if action and action not in config.uncategorized_default_allowed_actions:
        if category is None or category == "UNCATEGORIZED":
            reasons.append(
                "Category missing or uncategorized for action that requires explicit classification."
            )
        if priority is None:
            reasons.append(
                "Priority missing for action that requires explicit classification."
            )
    elif action in config.uncategorized_default_allowed_actions:
        conditions["uncategorized_default_allowed"] = True

    if action == "delete":
        delete_conditions = build_delete_conditions(
            age_days=request.age_days,
            min_age_days=config.delete_min_age_days,
            priority=priority,
            category=category,
            non_deletable_categories=config.non_deletable_categories,
            sender=request.sender,
            subject=request.subject,
            confidence=request.classification_confidence,
            confidence_threshold=config.classification_confidence_threshold,
            invoice_keywords=config.invoice_sensitivity_keywords,
            personal_keywords=config.personal_sensitivity_keywords,
        )
        conditions = merge_conditions(conditions, delete_conditions.model_dump())

        if not delete_conditions.priority_is_low:
            reasons.append("Delete blocked: only LOW priority emails may be deleted.")
        if not delete_conditions.has_required_age:
            reasons.append("Delete blocked: age_days missing or invalid.")
        elif not delete_conditions.age_threshold_met:
            reasons.append(
                f"Delete blocked: age_days must be >= {config.delete_min_age_days}."
            )
        if not delete_conditions.category_not_protected:
            reasons.append(
                "Delete blocked: category is protected (personal/invoice)."
            )
        if (
            delete_conditions.sensitive_signal_present
            and delete_conditions.classification_uncertain
        ):
            reasons.append(
                "Delete blocked: sensitive personal/invoice signal detected while classification is uncertain."
            )

    if action == "archive":
        if priority not in config.archive_allowed_priorities:
            reasons.append("Archive blocked: only MEDIUM/LOW priorities are archivable.")
        if category not in config.archive_allowed_categories:
            reasons.append(
                "Archive blocked: category is not in allowed archive categories."
            )

    if action in {"notify", "draft_reply"}:
        if priority != "HIGH":
            reasons.append(f"{action} blocked: action allowed only for HIGH priority.")
        if category not in config.high_priority_action_categories:
            reasons.append(
                f"{action} blocked: category not allowed for high-priority action."
            )

    allowed = len(reasons) == 0
    return ValidationResult(
        allowed=allowed,
        action=action or (raw_action or "unknown"),
        email_id=request.email_id,
        message_ref=request.message_ref,
        category=category,
        priority=priority,
        reasons=reasons,
        evaluated_conditions=conditions,
    )


def log_validation(result: ValidationResult, tool_name: str, executed: bool) -> None:
    payload = result.as_log_payload(tool_name=tool_name, executed=executed)
    _json_log(payload, blocked=(not result.allowed or not executed))


def validation_response_payload(
    *,
    proposed_action: str,
    result: ValidationResult,
    executed: bool,
    execution_result: str | None = None,
) -> dict[str, Any]:
    return {
        "proposed_action": proposed_action,
        "validated_action": result.action,
        "executed": executed,
        "allowed": result.allowed,
        "email_id": result.email_id,
        "category": result.category,
        "priority": result.priority,
        "blocked_reasons": result.reasons if not result.allowed else [],
        "validation": result.model_dump(),
        "execution_result": execution_result,
    }
