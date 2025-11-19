#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def test_case_3():
    print("=" * 70)
    print("Test Case 3: should_copy_files_of_specific_user_only")
    print("=" * 70)
    
    storage = CloudStorageImpl()
    
    print("\n1. Add users")
    result = storage.add_user('new_user', 100)
    print(f"   add_user('new_user', 100): {result}")
    assert result == True
    
    result = storage.add_user('super_user', 100)
    print(f"   add_user('super_user', 100): {result}")
    assert result == True
    
    print("\n2. Add files by users")
    result = storage.add_file_by('new_user', '/tmp/file.txt', 60)
    print(f"   add_file_by('new_user', '/tmp/file.txt', 60): {result}")
    print(f"   new_user used: {storage.users['new_user']['used']}, remaining: {100 - storage.users['new_user']['used']}")
    assert result == 40
    
    result = storage.add_file_by('super_user', '/tmp/super/file.txt', 40)
    print(f"   add_file_by('super_user', '/tmp/super/file.txt', 40): {result}")
    print(f"   super_user used: {storage.users['super_user']['used']}, remaining: {100 - storage.users['super_user']['used']}")
    assert result == 60
    
    result = storage.add_file('/tmp/root/file.txt', 150)
    print(f"   add_file('/tmp/root/file.txt', 150): {result}")
    print(f"   admin used: {storage.users['admin']['used']}")
    assert result == True
    
    print("\n3. Copy files")
    print(f"   Trying to copy /tmp/file.txt (owner: {storage.files['/tmp/file.txt'].get('owner')}, size: 60) to /file.txt")
    print(f"   new_user capacity: {storage.users['new_user']['capacity']}, used: {storage.users['new_user']['used']}")
    result = storage.copy_file('/tmp/file.txt', '/file.txt')
    print(f"   copy_file('/tmp/file.txt', '/file.txt'): {result} (Expected: False)")
    assert result == False, f"Expected False, got {result}"
    
    print(f"\n   Trying to copy /tmp/super/file.txt (owner: {storage.files['/tmp/super/file.txt'].get('owner')}, size: 40) to /super/file.txt")
    print(f"   super_user capacity: {storage.users['super_user']['capacity']}, used: {storage.users['super_user']['used']}")
    result = storage.copy_file('/tmp/super/file.txt', '/super/file.txt')
    print(f"   copy_file('/tmp/super/file.txt', '/super/file.txt'): {result} (Expected: True)")
    assert result == True, f"Expected True, got {result}"
    
    print(f"\n   Trying to copy /tmp/root/file.txt (owner: {storage.files['/tmp/root/file.txt'].get('owner')}, size: 150) to /root/file.txt")
    print(f"   admin capacity: {storage.users['admin']['capacity']}, used: {storage.users['admin']['used']}")
    result = storage.copy_file('/tmp/root/file.txt', '/root/file.txt')
    print(f"   copy_file('/tmp/root/file.txt', '/root/file.txt'): {result} (Expected: True)")
    assert result == True, f"Expected True, got {result}"
    
    print("\n✓ Test case 3 passed!")

def test_case_10():
    print("\n" + "=" * 70)
    print("Test Case 10: mixed")
    print("=" * 70)
    
    storage = CloudStorageImpl()
    
    print("\n1. Add admin files")
    result = storage.add_file('/path/to/file.txt', 1234)
    print(f"   add_file('/path/to/file.txt', 1234): {result}")
    assert result == True
    
    result = storage.add_file('/path/to/video.mp4', 12345)
    print(f"   add_file('/path/to/video.mp4', 12345): {result}")
    assert result == True
    print(f"   /path/to/video.mp4 owner: {storage.files['/path/to/video.mp4'].get('owner', 'admin')}")
    
    print("\n2. Add mom user")
    result = storage.add_user('mom', 5000)
    print(f"   add_user('mom', 5000): {result}")
    assert result == True
    
    print("\n3. Copy admin's video to /mom/video.mp4")
    print(f"   Source: /path/to/video.mp4, owner: {storage.files['/path/to/video.mp4'].get('owner', 'admin')}, size: 12345")
    print(f"   Admin capacity: {storage.users['admin']['capacity']}, used: {storage.users['admin']['used']}")
    result = storage.copy_file('/path/to/video.mp4', '/mom/video.mp4')
    print(f"   copy_file('/path/to/video.mp4', '/mom/video.mp4'): {result} (Expected: True)")
    if '/mom/video.mp4' in storage.files:
        print(f"   /mom/video.mp4 owner: {storage.files['/mom/video.mp4'].get('owner', 'admin')}")
    assert result == True, f"Expected True, got {result}"
    
    print("\n4. Add dad user")
    result = storage.add_user('dad', 100000)
    print(f"   add_user('dad', 100000): {result}")
    assert result == True
    
    print("\n5. Mom adds her own video")
    result = storage.add_file_by('mom', '/mom/videos/video.mp4', 3500)
    print(f"   add_file_by('mom', '/mom/videos/video.mp4', 3500): {result} (Expected: 1500)")
    print(f"   mom capacity: {storage.users['mom']['capacity']}, used: {storage.users['mom']['used']}")
    assert result == 1500, f"Expected 1500, got {result}"
    
    print("\n6. Try to copy mom's video (should fail due to capacity)")
    print(f"   Source: /mom/videos/video.mp4, owner: {storage.files['/mom/videos/video.mp4'].get('owner')}, size: 3500")
    print(f"   mom remaining: {storage.users['mom']['capacity'] - storage.users['mom']['used']}")
    result = storage.copy_file('/mom/videos/video.mp4', '/dad/video.mp4')
    print(f"   copy_file('/mom/videos/video.mp4', '/dad/video.mp4'): {result} (Expected: False)")
    assert result == False, f"Expected False, got {result}"
    
    print("\n7. Verify file sizes")
    result = storage.get_file_size('/path/to/video.mp4')
    print(f"   get_file_size('/path/to/video.mp4'): {result}")
    assert result == 12345
    
    result = storage.get_file_size('/mom/video.mp4')
    print(f"   get_file_size('/mom/video.mp4'): {result}")
    assert result == 12345
    
    print("\n8. Find all video.mp4 files")
    result = storage.find_file('/', 'video.mp4')
    print(f"   find_file('/', 'video.mp4'): {result}")
    expected = ['/mom/video.mp4(12345)', '/path/to/video.mp4(12345)', '/mom/videos/video.mp4(3500)']
    print(f"   Expected: {expected}")
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("\n9. Update mom's capacity to 10000 (no removal needed)")
    print(f"   Mom's files before:")
    for fname, fdata in storage.files.items():
        if fdata.get('owner', 'admin') == 'mom':
            print(f"     {fname}: {fdata['size']} bytes")
    result = storage.update_capacity('mom', 10000)
    print(f"   update_capacity('mom', 10000): {result} (Expected: 0)")
    assert result == 0, f"Expected 0, got {result}"
    
    print("\n10. Update mom's capacity to 2000 (should remove largest file)")
    print(f"   Mom's used: {storage.users['mom']['used']}, new capacity: 2000")
    print(f"   Mom's files before:")
    for fname, fdata in storage.files.items():
        if fdata.get('owner', 'admin') == 'mom':
            print(f"     {fname}: {fdata['size']} bytes")
    result = storage.update_capacity('mom', 2000)
    print(f"   update_capacity('mom', 2000): {result} (Expected: 1)")
    print(f"   Mom's used after: {storage.users['mom']['used']}")
    print(f"   Mom's files after:")
    for fname, fdata in storage.files.items():
        if fdata.get('owner', 'admin') == 'mom':
            print(f"     {fname}: {fdata['size']} bytes")
    assert result == 1, f"Expected 1, got {result}"
    
    print("\n11. Verify files after capacity reduction")
    result = storage.find_file('/', 'video.mp4')
    print(f"   find_file('/', 'video.mp4'): {result}")
    expected = ['/mom/video.mp4(12345)', '/path/to/video.mp4(12345)']
    print(f"   Expected: {expected}")
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("\n✓ Test case 10 passed!")

if __name__ == '__main__':
    try:
        test_case_3()
        test_case_10()
        print("\n" + "=" * 70)
        print("✓ All failing test cases now pass!")
        print("=" * 70)
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

