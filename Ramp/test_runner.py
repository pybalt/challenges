#!/usr/bin/env python3
import sys
sys.path.insert(0, 'C:\\Users\\leobr\\Workspace\\challenges\\Ramp')

from cloud_storage import CloudStorageImpl

def test_level_1():
    storage = CloudStorageImpl()
    
    print("Test 1: add_file('/dir1/dir2/file.txt', 10)")
    result = storage.add_file("/dir1/dir2/file.txt", 10)
    print(f"  Expected: True, Got: {result}")
    assert result == True
    
    print("\nTest 2: copy_file('/not-existing.file', '/dir1/file.txt')")
    result = storage.copy_file("/not-existing.file", "/dir1/file.txt")
    print(f"  Expected: False, Got: {result}")
    assert result == False
    
    print("\nTest 3: copy_file('/dir1/dir2/file.txt', '/dir1/file.txt')")
    result = storage.copy_file("/dir1/dir2/file.txt", "/dir1/file.txt")
    print(f"  Expected: True, Got: {result}")
    assert result == True
    
    print("\nTest 4: add_file('/dir1/file.txt', 15)")
    result = storage.add_file("/dir1/file.txt", 15)
    print(f"  Expected: False, Got: {result}")
    assert result == False
    
    print("\nTest 5: copy_file('/dir1/file.txt', '/dir1/dir2/file.txt')")
    result = storage.copy_file("/dir1/file.txt", "/dir1/dir2/file.txt")
    print(f"  Expected: False, Got: {result}")
    assert result == False
    
    print("\nTest 6: get_file_size('/dir1/file.txt')")
    result = storage.get_file_size("/dir1/file.txt")
    print(f"  Expected: 10, Got: {result}")
    assert result == 10
    
    print("\nTest 7: get_file_size('/not-existing.file')")
    result = storage.get_file_size("/not-existing.file")
    print(f"  Expected: None, Got: {result}")
    assert result is None
    
    print("\n✓ All Level 1 tests passed!")

if __name__ == '__main__':
    test_level_1()

