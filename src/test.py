# ./src/test.py

import unittest
from lib import chat_api


class ChatAPITestCase(unittest.TestCase):
    def setUp(self):
        # Setup code, if necessary
        pass

    def tearDown(self):
        # Teardown code, if necessary
        pass

    def test_chat_modelate(self):
        # Test the function
        prompt = "example prompt"
        user_id = "user123"
        model = "gpt-3.5-turbo"
        response_language = "日本語"

        response = chat_api.chat_modelate(prompt, user_id, model, response_language)
        has_response = "response" in response

        self.assertTrue(
            has_response,
            "The response should be a non-empty string",
        )


if __name__ == "__main__":
    unittest.main()
