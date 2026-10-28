import unittest
from core.json_parser import extract_json_object

class JsonParserTests(unittest.TestCase):
    def test_direct_json(self):
        self.assertEqual(extract_json_object('{"action":"chat"}'), {"action": "chat"})
    def test_json_in_prose(self):
        self.assertEqual(extract_json_object('Respuesta: {"action":"list_files","parameters":{}} fin'), {"action": "list_files", "parameters": {}})
    def test_invalid(self):
        self.assertIsNone(extract_json_object('no es json'))

if __name__ == "__main__":
    unittest.main()
