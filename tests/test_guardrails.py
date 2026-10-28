import unittest
from core.guardrails import validate_action

class GuardrailTests(unittest.TestCase):
    def test_read_action_allowed(self):
        self.assertTrue(validate_action("list_files", {}).allowed)
    def test_sensitive_action_denied(self):
        self.assertFalse(validate_action("delete_files", {}).allowed)
    def test_unknown_action_denied(self):
        self.assertFalse(validate_action("powershell", {}).allowed)

if __name__ == "__main__":
    unittest.main()
