import unittest
from twopi_flask_utils.config import build_url 

class TestBuildUrl(unittest.TestCase):
    def test_basic_dsn(self):
        cases = [
            (build_url('redis://localhost:6379/0'), 'redis://localhost:6379/0'),
            (build_url('foo://localhost/0', port=6379, scheme='redis'), 'redis://localhost:6379/0'),
        ]

        for result, expected in cases:
            self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()