import unittest
from emulator import VirtualFileSystem

class TestLS(unittest.TestCase):
    def setUp(self):
        self.fs = VirtualFileSystem('fs_image.zip')

    def test_list_directory(self):
        files = self.fs.list_directory('/')
        self.assertIn('file1.txt', files)
        self.assertIn('dir1', files)

    def test_list_empty_directory(self):
        files = self.fs.list_directory('/empty_dir')
        self.assertEqual(files, [])

if __name__ == '__main__':
    unittest.main()