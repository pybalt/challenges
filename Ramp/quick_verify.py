#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

# Quick verification of the two failing scenarios
storage = CloudStorageImpl()

print("=== Quick Verification ===\n")

# Test case 3 scenario
print("Test case 3 scenario:")
storage.add_user('new_user', 100)
storage.add_file_by('new_user', '/tmp/file.txt', 60)
print(f"new_user used: {storage.users['new_user']['used']}, capacity: {storage.users['new_user']['capacity']}")
print(f"Trying to copy 60-byte file when only 40 bytes remaining...")
result = storage.copy_file('/tmp/file.txt', '/file.txt')
print(f"Result: {result} (Expected: False)\n")

# Test case 10 scenario
print("Test case 10 scenario:")
storage2 = CloudStorageImpl()
storage2.add_file('/admin/video.mp4', 12345)
print(f"Admin file owner: {storage2.files['/admin/video.mp4'].get('owner', 'admin')}")
storage2.add_user('mom', 5000)
print(f"Copying admin's file...")
result = storage2.copy_file('/admin/video.mp4', '/mom/video.mp4')
print(f"Result: {result} (Expected: True)")
if '/mom/video.mp4' in storage2.files:
    print(f"/mom/video.mp4 owner: {storage2.files['/mom/video.mp4'].get('owner', 'admin')}")
print(f"Admin used: {storage2.users['admin']['used']}")
print(f"Mom used: {storage2.users['mom']['used']}")

storage2.add_file_by('mom', '/mom/video2.mp4', 3500)
print(f"\nAfter mom adds 3500-byte file:")
print(f"Mom used: {storage2.users['mom']['used']}, remaining: {5000 - storage2.users['mom']['used']}")

print(f"\nTrying to copy mom's 3500-byte file (mom has only 1500 bytes remaining)...")
result = storage2.copy_file('/mom/video2.mp4', '/dad/video.mp4')
print(f"Result: {result} (Expected: False)")

print(f"\nUpdating mom's capacity to 2000 (used: {storage2.users['mom']['used']})...")
result = storage2.update_capacity('mom', 2000)
print(f"Files removed: {result} (Expected: 1)")
print(f"Mom's files after update:")
for fname, fdata in storage2.files.items():
    if fdata.get('owner', 'admin') == 'mom':
        print(f"  {fname}: {fdata['size']} bytes")
print(f"Mom used after: {storage2.users['mom']['used']}")

print(f"\nChecking if /mom/video.mp4 still exists (should be Yes, owned by admin):")
size = storage2.get_file_size('/mom/video.mp4')
print(f"  /mom/video.mp4 size: {size}, owner: {storage2.files['/mom/video.mp4'].get('owner', 'admin') if '/mom/video.mp4' in storage2.files else 'N/A'}")

