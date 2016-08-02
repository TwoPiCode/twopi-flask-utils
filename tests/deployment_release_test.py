import unittest, os
from twopi_flask_utils.deployment_release import get_release 

class TestGetRelease(unittest.TestCase):

    def tearDown(self):
        if os.path.exists('version.txt'):
            os.remove('version.txt')

    def test_get_release(self):
        f = open('version.txt', 'w')
        f.write('fakeversion')
        f.close()
        
        self.assertEqual(get_release(), 'fakeversion')

    def test_no_release_file(self):
        self.assertEqual(get_release(), '__UNKNOWN__')

if __name__ == '__main__':
    unittest.main()