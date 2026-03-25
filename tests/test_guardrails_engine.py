import unittest

from gmail_crew_ai.guardrails.engine import validate_action
from gmail_crew_ai.guardrails.models import PolicyValidationInput


class GuardrailsEngineTests(unittest.TestCase):
    def test_delete_allowed_for_low_priority_old_promotion(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="1",
                category="PROMOTIONS",
                priority="LOW",
                requested_action="delete",
                age_days=45,
                sender="promo@example.com",
                subject="Big sale",
                classification_confidence=0.95,
            )
        )
        self.assertTrue(result.allowed)

    def test_delete_blocked_for_high_priority(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="2",
                category="PROMOTIONS",
                priority="HIGH",
                requested_action="delete",
                age_days=45,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("LOW priority" in reason for reason in result.reasons))

    def test_delete_blocked_for_invoice_category(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="3",
                category="INVOICE",
                priority="LOW",
                requested_action="delete",
                age_days=45,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("protected" in reason for reason in result.reasons))

    def test_delete_blocked_for_personal_category(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="4",
                category="PERSONAL",
                priority="LOW",
                requested_action="delete",
                age_days=45,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("protected" in reason for reason in result.reasons))

    def test_delete_blocked_when_age_missing(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="5",
                category="PROMOTIONS",
                priority="LOW",
                requested_action="delete",
                age_days=None,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("age_days missing" in reason for reason in result.reasons))

    def test_archive_allowed_for_medium_priority_and_allowed_category(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="6",
                category="NEWSLETTERS",
                priority="MEDIUM",
                requested_action="archive",
                age_days=10,
            )
        )
        self.assertTrue(result.allowed)

    def test_unknown_action_blocked(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="7",
                category="PROMOTIONS",
                priority="LOW",
                requested_action="explode",
                age_days=10,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("disallowed action" in reason for reason in result.reasons))

    def test_unknown_category_blocked(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="8",
                category="MYSTERY_CATEGORY",
                priority="LOW",
                requested_action="archive",
                age_days=10,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("Unknown category" in reason for reason in result.reasons))

    def test_unknown_priority_blocked(self):
        result = validate_action(
            PolicyValidationInput(
                email_id="9",
                category="PROMOTIONS",
                priority="CRITICAL",
                requested_action="archive",
                age_days=10,
            )
        )
        self.assertFalse(result.allowed)
        self.assertTrue(any("Unknown priority" in reason for reason in result.reasons))


if __name__ == "__main__":
    unittest.main()
