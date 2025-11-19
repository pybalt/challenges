import unittest
from cloud_storage import CloudStorageImpl


class TestLevel1(unittest.TestCase):
    
    def setUp(self):
        self.storage = CloudStorageImpl()
    
    def test_example_from_description(self):
        self.assertTrue(self.storage.add_file("/dir1/dir2/file.txt", 10))
        self.assertFalse(self.storage.copy_file("/not-existing.file", "/dir1/file.txt"))
        self.assertTrue(self.storage.copy_file("/dir1/dir2/file.txt", "/dir1/file.txt"))
        self.assertFalse(self.storage.add_file("/dir1/file.txt", 15))
        self.assertFalse(self.storage.copy_file("/dir1/file.txt", "/dir1/dir2/file.txt"))
        self.assertEqual(self.storage.get_file_size("/dir1/file.txt"), 10)
        self.assertIsNone(self.storage.get_file_size("/not-existing.file"))
    
    def test_add_file_basic(self):
        self.assertTrue(self.storage.add_file("/file.txt", 100))
        self.assertEqual(self.storage.get_file_size("/file.txt"), 100)
    
    def test_add_file_duplicate(self):
        self.assertTrue(self.storage.add_file("/file.txt", 100))
        self.assertFalse(self.storage.add_file("/file.txt", 200))
        self.assertEqual(self.storage.get_file_size("/file.txt"), 100)
    
    def test_copy_file_basic(self):
        self.storage.add_file("/file1.txt", 50)
        self.assertTrue(self.storage.copy_file("/file1.txt", "/file2.txt"))
        self.assertEqual(self.storage.get_file_size("/file2.txt"), 50)
    
    def test_copy_nonexistent_file(self):
        self.assertFalse(self.storage.copy_file("/nonexistent.txt", "/new.txt"))
    
    def test_copy_to_existing_file(self):
        self.storage.add_file("/file1.txt", 50)
        self.storage.add_file("/file2.txt", 75)
        self.assertFalse(self.storage.copy_file("/file1.txt", "/file2.txt"))
    
    def test_get_file_size_nonexistent(self):
        self.assertIsNone(self.storage.get_file_size("/nonexistent.txt"))


if __name__ == '__main__':
    unittest.main()

