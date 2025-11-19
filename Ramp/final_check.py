#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def check_implementation():
    print("=" * 80)
    print("Final Implementation Check")
    print("=" * 80)
    
    # Check 1: Admin has truly unlimited capacity
    print("\n[Check 1] Admin unlimited capacity")
    storage = CloudStorageImpl()
    result = storage.add_file('/huge1.dat', 999999999)
    print(f"  add_file 999999999 bytes: {result}")
    result = storage.add_file('/huge2.dat', 999999999)
    print(f"  add_file another 999999999 bytes: {result}")
    print(f"  Admin used: {storage.users['admin']['used']}")
    print(f"  Admin capacity: {storage.users['admin']['capacity']}")
    print(f"  Can still add more: {storage.users['admin']['used'] < storage.users['admin']['capacity']}")
    assert result == True, "Admin should have unlimited capacity"
    print("  ✓ Pass\n")
    
    # Check 2: Copy preserves ownership
    print("[Check 2] Copy preserves ownership")
    storage = CloudStorageImpl()
    storage.add_user('user1', 1000)
    storage.add_file_by('user1', '/user1/file.txt', 500)
    storage.add_file('/admin/file.txt', 500)
    
    # Copy user1's file (should use user1's capacity)
    print(f"  user1 used before copy: {storage.users['user1']['used']}")
    result = storage.copy_file('/user1/file.txt', '/user1/file2.txt')
    print(f"  copy_file('/user1/file.txt', '/user1/file2.txt'): {result}")
    print(f"  user1 used after copy: {storage.users['user1']['used']}")
    print(f"  /user1/file2.txt owner: {storage.files.get('/user1/file2.txt', {}).get('owner', 'N/A')}")
    assert result == False, "Should fail - user1 only has 500 bytes remaining, needs 500 more"
    print("  ✓ Pass - correctly failed due to capacity\n")
    
    # Copy admin's file (should use admin's capacity)
    print(f"  admin used before copy: {storage.users['admin']['used']}")
    result = storage.copy_file('/admin/file.txt', '/admin/file2.txt')
    print(f"  copy_file('/admin/file.txt', '/admin/file2.txt'): {result}")
    print(f"  admin used after copy: {storage.users['admin']['used']}")
    print(f"  /admin/file2.txt owner: {storage.files.get('/admin/file2.txt', {}).get('owner', 'N/A')}")
    assert result == True, "Admin should be able to copy"
    print("  ✓ Pass\n")
    
    # Check 3: Update capacity removes largest files first
    print("[Check 3] Update capacity removes largest files, lexicographic ties")
    storage = CloudStorageImpl()
    storage.add_user('user1', 10000)
    storage.add_file_by('user1', '/z_large.dat', 3000)
    storage.add_file_by('user1', '/a_large.dat', 3000)  # Same size, comes first lexicographically
    storage.add_file_by('user1', '/medium.dat', 2000)
    storage.add_file_by('user1', '/small.dat', 1000)
    print(f"  user1 total used: {storage.users['user1']['used']}")
    print(f"  Files: z_large(3000), a_large(3000), medium(2000), small(1000)")
    
    # Reduce capacity to 5000 (need to remove 4000 bytes)
    print(f"  Reducing capacity to 5000 (need to remove 4000 bytes)...")
    result = storage.update_capacity('user1', 5000)
    print(f"  Files removed: {result}")
    print(f"  user1 used after: {storage.users['user1']['used']}")
    print(f"  Remaining files:")
    for fname in ['/z_large.dat', '/a_large.dat', '/medium.dat', '/small.dat']:
        size = storage.get_file_size(fname)
        if size is not None:
            print(f"    {fname}: {size}")
        else:
            print(f"    {fname}: REMOVED")
    
    # Should remove: a_large (3000, lexicographically first), then z_large (3000)
    # Wait, that's only 6000 bytes removed, but we only need to remove 4000.
    # So it should remove: a_large (3000), then medium (2000) = 5000 total, leaving 4000
    # Actually: total = 9000, capacity = 5000, so need to remove 4000
    # Remove a_large (3000) first (lexicographically first among largest)
    # After removing a_large: used = 6000, still > 5000
    # Remove z_large (3000) next
    # After removing z_large: used = 3000, now <= 5000, stop
    # So should remove 2 files
    assert result == 2, f"Expected 2 files removed, got {result}"
    assert storage.get_file_size('/a_large.dat') is None, "a_large should be removed"
    assert storage.get_file_size('/z_large.dat') is None, "z_large should be removed"
    print("  ✓ Pass\n")
    
    # Check 4: Edge case - exact capacity
    print("[Check 4] Adding file with exact remaining capacity")
    storage = CloudStorageImpl()
    storage.add_user('user1', 1000)
    result = storage.add_file_by('user1', '/file1.dat', 1000)
    print(f"  add_file_by 1000 bytes (exact capacity): {result}")
    assert result == 0, f"Expected 0 remaining, got {result}"
    print("  ✓ Pass\n")
    
    print("=" * 80)
    print("✓ All checks passed!")
    print("=" * 80)

if __name__ == '__main__':
    try:
        check_implementation()
    except AssertionError as e:
        print(f"\n✗ Check failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

