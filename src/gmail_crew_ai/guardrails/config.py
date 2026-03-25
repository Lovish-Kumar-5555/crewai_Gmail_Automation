from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PolicyConfig:
    """Centralized policy configuration for tool execution guardrails."""

    allowed_categories: set[str] = field(
        default_factory=lambda: {
            "WORK",
            "PROMOTION",
            "PROMOTIONS",
            "INVOICE",
            "RECEIPTS_INVOICES",
            "PERSONAL",
            "SPAM",
            "NOTIFICATION",
            "NEWSLETTERS",
            "GITHUB",
            "YOUTUBE",
            "SOCIALS",
            "RECRUITMENT",
            "EVENT_INVITATIONS",
            "COLD_EMAIL",
            "SPONSORSHIPS",
            "OTHER",
            "UNCATEGORIZED",
        }
    )
    allowed_priorities: set[str] = field(
        default_factory=lambda: {"HIGH", "MEDIUM", "LOW"}
    )
    allowed_actions: set[str] = field(
        default_factory=lambda: {
            "notify",
            "draft_reply",
            "archive",
            "delete",
            "label",
            "skip",
            "empty_trash",
        }
    )
    destructive_actions: set[str] = field(
        default_factory=lambda: {"delete", "empty_trash"}
    )
    delete_min_age_days: int = 30
    non_deletable_categories: set[str] = field(
        default_factory=lambda: {"PERSONAL", "INVOICE", "RECEIPTS_INVOICES"}
    )
    delete_allowed_priorities: set[str] = field(default_factory=lambda: {"LOW"})
    archive_allowed_priorities: set[str] = field(default_factory=lambda: {"MEDIUM", "LOW"})
    archive_allowed_categories: set[str] = field(
        default_factory=lambda: {
            "PROMOTION",
            "PROMOTIONS",
            "NEWSLETTERS",
            "SPAM",
            "NOTIFICATION",
            "SOCIALS",
            "GITHUB",
            "WORK",
            "RECRUITMENT",
            "EVENT_INVITATIONS",
            "COLD_EMAIL",
            "SPONSORSHIPS",
            "OTHER",
        }
    )
    high_priority_action_categories: set[str] = field(
        default_factory=lambda: {
            "WORK",
            "PERSONAL",
            "GITHUB",
            "YOUTUBE",
            "RECRUITMENT",
            "EVENT_INVITATIONS",
            "NOTIFICATION",
        }
    )
    uncategorized_default_allowed_actions: set[str] = field(
        default_factory=lambda: {"skip", "empty_trash"}
    )
    classification_confidence_threshold: float = 0.75

    # Aliases make policy resilient to variations from different classifiers/prompts.
    category_aliases: dict[str, str] = field(
        default_factory=lambda: {
            "PROMOTIONAL": "PROMOTIONS",
            "INVOICES": "INVOICE",
            "RECEIPT": "RECEIPTS_INVOICES",
            "RECEIPTS": "RECEIPTS_INVOICES",
            "NEWSLETTER": "NEWSLETTERS",
        }
    )
    action_aliases: dict[str, str] = field(
        default_factory=lambda: {
            "send_notification": "notify",
            "notification": "notify",
            "create_draft": "draft_reply",
            "draft": "draft_reply",
            "draft_email": "draft_reply",
            "delete_email": "delete",
            "organize": "label",
            "label_email": "label",
            "no_action": "skip",
        }
    )
    invoice_sensitivity_keywords: tuple[str, ...] = (
        "invoice",
        "receipt",
        "billing",
        "payment",
        "tax",
    )
    personal_sensitivity_keywords: tuple[str, ...] = (
        "family",
        "friend",
        "mom",
        "dad",
        "spouse",
        "private",
        "personal",
    )


DEFAULT_POLICY_CONFIG = PolicyConfig()
