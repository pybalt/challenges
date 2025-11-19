#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def test_level_3():
    print("=" * 70)
    print("Testing Level 3: User Management with Capacity Limits")
    print("=" * 70)
    
    storage = CloudStorageImpl()
    
    print("\n### Test 1: Add Users ###")
    result = storage.add_user('user1', 1000)
    print(f"  add_user('user1', 1000): {result}")
    assert result == True, "Failed to add user1"
    
    result = storage.add_user('user2', 500)
    print(f"  add_user('user2', 500): {result}")
    assert result == True, "Failed to add user2"
    
    result = storage.add_user('user1', 2000)
    print(f"  add_user('user1', 2000) - duplicate: {result}")
    assert result == False, "Should fail for duplicate user"
    
    print("\n### Test 2: Add Files by User ###")
    result = storage.add_file_by('user1', '/docs/file1.txt', 300)
    print(f"  add_file_by('user1', '/docs/file1.txt', 300): {result}")
    assert result == 700, f"Expected 700, got {result}"
    
    result = storage.add_file_by('user1', '/docs/file2.txt', 400)
    print(f"  add_file_by('user1', '/docs/file2.txt', 400): {result}")
    assert result == 300, f"Expected 300, got {result}"
    
    result = storage.add_file_by('user1', '/docs/file3.txt', 400)
    print(f"  add_file_by('user1', '/docs/file3.txt', 400) - exceeds capacity: {result}")
    assert result is None, "Should fail when exceeding capacity"
    
    print("\n### Test 3: Admin has unlimited capacity ###")
    result = storage.add_file('/admin/file1.txt', 10000000)
    print(f"  add_file('/admin/file1.txt', 10000000) by admin: {result}")
    assert result == True, "Admin should have unlimited capacity"
    
    print("\n### Test 4: Copy preserves ownership ###")
    result = storage.copy_file('/docs/file1.txt', '/backup/file1.txt')
    print(f"  copy_file('/docs/file1.txt', '/backup/file1.txt'): {result}")
    assert result == False, "Should fail - exceeds user1's capacity"
    
    print("\n### Test 5: Update Capacity - No Files Removed ###")
    result = storage.update_capacity('user1', 1500)
    print(f"  update_capacity('user1', 1500) - increase: {result}")
    assert result == 0, f"Expected 0 files removed, got {result}"
    
    print("\n### Test 6: Update Capacity - Files Removed ###")
    result = storage.add_file_by('user2', '/user2/file1.txt', 200)
    print(f"  add_file_by('user2', '/user2/file1.txt', 200): {result}")
    assert result == 300, f"Expected 300, got {result}"
    
    result = storage.add_file_by('user2', '/user2/file2.txt', 150)
    print(f"  add_file_by('user2', '/user2/file2.txt', 150): {result}")
    assert result == 150, f"Expected 150, got {result}"
    
    result = storage.add_file_by('user2', '/user2/file3.txt', 100)
    print(f"  add_file_by('user2', '/user2/file3.txt', 100): {result}")
    assert result == 50, f"Expected 50, got {result}"
    
    result = storage.update_capacity('user2', 200)
    print(f"  update_capacity('user2', 200) - reduce capacity: {result}")
    assert result == 2, f"Expected 2 files removed, got {result}"
    
    print(f"  Remaining file should be the smallest (100 bytes)")
    size = storage.get_file_size('/user2/file3.txt')
    print(f"  get_file_size('/user2/file3.txt'): {size}")
    assert size == 100, "file3.txt should remain"
    
    size = storage.get_file_size('/user2/file1.txt')
    print(f"  get_file_size('/user2/file1.txt'): {size}")
    assert size is None, "file1.txt should be removed (largest)"
    
    print("\n### Test 7: Non-existent User ###")
    result = storage.add_file_by('nonexistent', '/file.txt', 100)
    print(f"  add_file_by('nonexistent', '/file.txt', 100): {result}")
    assert result is None, "Should fail for non-existent user"
    
    result = storage.update_capacity('nonexistent', 1000)
    print(f"  update_capacity('nonexistent', 1000): {result}")
    assert result is None, "Should fail for non-existent user"
    
    print("\n" + "=" * 70)
    print("✓ All Level 3 tests passed!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        test_level_3()
        print("\nSUCCESS: Level 3 user management is working!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

