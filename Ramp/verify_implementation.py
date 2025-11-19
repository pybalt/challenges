#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def verify_basic_functionality():
    storage = CloudStorageImpl()
    
    print("=" * 60)
    print("Testing Basic Functionality")
    print("=" * 60)
    
    print("\n1. Testing add_file('/dir1/dir2/file.txt', 10)")
    result = storage.add_file("/dir1/dir2/file.txt", 10)
    print(f"   Result: {result} (Expected: True)")
    assert result == True, "Failed to add file"
    
    print("\n2. Testing copy_file('/not-existing.file', '/dir1/file.txt')")
    result = storage.copy_file("/not-existing.file", "/dir1/file.txt")
    print(f"   Result: {result} (Expected: False)")
    assert result == False, "Should fail for non-existing source"
    
    print("\n3. Testing copy_file('/dir1/dir2/file.txt', '/dir1/file.txt')")
    result = storage.copy_file("/dir1/dir2/file.txt", "/dir1/file.txt")
    print(f"   Result: {result} (Expected: True)")
    assert result == True, "Failed to copy file"
    
    print("\n4. Testing add_file('/dir1/file.txt', 15) - duplicate")
    result = storage.add_file("/dir1/file.txt", 15)
    print(f"   Result: {result} (Expected: False)")
    assert result == False, "Should fail for duplicate file"
    
    print("\n5. Testing copy_file('/dir1/file.txt', '/dir1/dir2/file.txt') - duplicate")
    result = storage.copy_file("/dir1/file.txt", "/dir1/dir2/file.txt")
    print(f"   Result: {result} (Expected: False)")
    assert result == False, "Should fail for duplicate destination"
    
    print("\n6. Testing get_file_size('/dir1/file.txt')")
    result = storage.get_file_size("/dir1/file.txt")
    print(f"   Result: {result} (Expected: 10)")
    assert result == 10, "Wrong file size"
    
    print("\n7. Testing get_file_size('/not-existing.file')")
    result = storage.get_file_size("/not-existing.file")
    print(f"   Result: {result} (Expected: None)")
    assert result is None, "Should return None for non-existing file"
    
    print("\n" + "=" * 60)
    print("✓ All basic tests passed!")
    print("=" * 60)

def verify_complex_scenario():
    storage = CloudStorageImpl()
    
    print("\n" + "=" * 60)
    print("Testing Complex Scenario (test_level_1_case_08)")
    print("=" * 60)
    
    print("\nAdding /file/file.txt with size 50")
    assert storage.add_file('/file/file.txt', 50) == True
    
    print("Adding /file.png with size 880")
    assert storage.add_file('/file.png', 880) == True
    
    print("Getting non-existing files")
    assert storage.get_file_size('/file/file.txt50') is None
    assert storage.get_file_size('/file/file') is None
    assert storage.get_file_size('/fil') is None
    
    print("Getting /file/file.txt")
    assert storage.get_file_size('/file/file.txt') == 50
    
    print("Copying /file.png to /file.png880")
    assert storage.copy_file('/file.png', '/file.png880') == True
    
    print("Adding /file.png8 with size 80")
    assert storage.add_file('/file.png8', 80) == True
    
    print("Copying /file/file.txt to /file.pn")
    assert storage.copy_file('/file/file.txt', '/file.pn') == True
    
    print("Verifying sizes")
    assert storage.get_file_size('/file.pn') == 50
    assert storage.get_file_size('/file.png') == 880
    assert storage.get_file_size('/file.png8') == 80
    assert storage.get_file_size('/file.png880') == 880
    
    print("\n✓ Complex scenario test passed!")

if __name__ == '__main__':
    try:
        verify_basic_functionality()
        verify_complex_scenario()
        print("\n" + "=" * 60)
        print("SUCCESS: All verification tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

