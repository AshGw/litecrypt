import unittest

from litecrypt.core.helpers.funcs import parse_encrypted_message, parse_message


class TestMessageParsing(unittest.TestCase):
    def test_parse_message_string_input(self):
        input_message = "xyz"
        self.assertIs(bytes, type(parse_message(input_message)))

    def test_parse_message_bytes_input(self):
        input_message = b"xyz"
        self.assertIs(bytes, type(parse_message(input_message)))

    def test_parse_encrypted_message_string_input(self):
        message = "SGVsbG8sIFdvcmxkIQ=="
        self.assertIs(bytes, type(parse_encrypted_message(message)))

    def test_parse_encrypted_message_bytes_input(self):
        message = b"SGVsbG8sIFdvcmxkIQ=="
        self.assertIs(bytes, type(parse_encrypted_message(message)))

    def test_parse_encrypted_message_invalid_input(self):
        ret = parse_encrypted_message(123)
        assert ret is None


if __name__ == "__main__":
    unittest.main()
