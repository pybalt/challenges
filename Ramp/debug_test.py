#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def debug_test_case_10():
    storage = CloudStorageImpl()
    
    print("=== Test Case 10 Debug ===\n")
    
    print("1. add_file('/path/to/file.txt', 1234)")
    result = storage.add_file('/path/to/file.txt', 1234)
    print(f"   Result: {result}")
    
    print("\n2. add_file('/path/to/video.mp4', 12345)")
    result = storage.add_file('/path/to/video.mp4', 12345)
    print(f"   Result: {result}")
    
    print("\n3. add_user('mom', 5000)")
    result = storage.add_user('mom', 5000)
    print(f"   Result: {result}")
    print(f"   Mom's capacity: {storage.users['mom']['capacity']}, used: {storage.users['mom']['used']}")
    
    print("\n4. copy_file('/path/to/video.mp4', '/mom/video.mp4')")
    print(f"   Source file owner: {storage.files.get('/path/to/video.mp4', {}).get('owner', 'admin')}")
    result = storage.copy_file('/path/to/video.mp4', '/mom/video.mp4')
    print(f"   Result: {result} (Expected: True)")
    if '/mom/video.mp4' in storage.files:
        print(f"   Copied file owner: {storage.files['/mom/video.mp4'].get('owner', 'admin')}")
        print(f"   Copied file size: {storage.files['/mom/video.mp4']['size']}")
    print(f"   Admin used: {storage.users['admin']['used']}")
    print(f"   Mom used: {storage.users['mom']['used']}")
    
    print("\n5. add_user('dad', 100000)")
    result = storage.add_user('dad', 100000)
    print(f"   Result: {result}")
    
    print("\n6. add_file_by('mom', '/mom/videos/video.mp4', 3500)")
    result = storage.add_file_by('mom', '/mom/videos/video.mp4', 3500)
    print(f"   Result: {result} (Expected: 1500)")
    print(f"   Mom used: {storage.users['mom']['used']}")
    
    print("\n7. copy_file('/mom/videos/video.mp4', '/dad/video.mp4')")
    print(f"   Source file owner: {storage.files['/mom/videos/video.mp4'].get('owner', 'admin')}")
    print(f"   Mom's remaining capacity: {storage.users['mom']['capacity'] - storage.users['mom']['used']}")
    result = storage.copy_file('/mom/videos/video.mp4', '/dad/video.mp4')
    print(f"   Result: {result} (Expected: False)")
    
    print("\n8. find_file('/', 'video.mp4')")
    result = storage.find_file('/', 'video.mp4')
    print(f"   Result: {result}")
    expected = ['/mom/video.mp4(12345)', '/path/to/video.mp4(12345)', '/mom/videos/video.mp4(3500)']
    print(f"   Expected: {expected}")
    
    print("\n9. update_capacity('mom', 10000)")
    print(f"   Mom's files before update:")
    for fname, fdata in storage.files.items():
        if fdata.get('owner', 'admin') == 'mom':
            print(f"     {fname}: {fdata['size']} bytes")
    print(f"   Mom used: {storage.users['mom']['used']}, capacity: {storage.users['mom']['capacity']}")
    result = storage.update_capacity('mom', 10000)
    print(f"   Result: {result} (Expected: 0)")
    
    print("\n10. update_capacity('mom', 2000)")
    print(f"   Mom's files before update:")
    for fname, fdata in storage.files.items():
        if fdata.get('owner', 'admin') == 'mom':
            print(f"     {fname}: {fdata['size']} bytes")
    print(f"   Mom used: {storage.users['mom']['used']}, capacity: {storage.users['mom']['capacity']}")
    result = storage.update_capacity('mom', 2000)
    print(f"   Result: {result} (Expected: 1)")
    print(f"   Mom used after: {storage.users['mom']['used']}")
    
    print("\n11. find_file('/', 'video.mp4') after capacity reduction")
    result = storage.find_file('/', 'video.mp4')
    print(f"   Result: {result}")
    expected = ['/mom/video.mp4(12345)', '/path/to/video.mp4(12345)']
    print(f"   Expected: {expected}")
    
    print("\n12. get_file_size('/mom/video.mp4')")
    result = storage.get_file_size('/mom/video.mp4')
    print(f"   Result: {result} (Expected: 12345)")
    
    print("\n13. add_file_by('mom', '/mom/videos/video.mp4', 2500)")
    result = storage.add_file_by('mom', '/mom/videos/video.mp4', 2500)
    print(f"   Result: {result} (Expected: None)")
    
    print("\n14. add_file_by('mom', '/mom/videos/video.mp4', 2000)")
    result = storage.add_file_by('mom', '/mom/videos/video.mp4', 2000)
    print(f"   Result: {result} (Expected: 0)")

if __name__ == '__main__':
    debug_test_case_10()

