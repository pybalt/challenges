#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

# Debug test case 3
storage = CloudStorageImpl()

print("=== Debug Test Case 3 ===\n")

storage.add_user('new_user', 100)
print(f"new_user capacity: {storage.users['new_user']['capacity']}, used: {storage.users['new_user']['used']}")

result = storage.add_file_by('new_user', '/tmp/file.txt', 60)
print(f"add_file_by('new_user', '/tmp/file.txt', 60): {result}")
print(f"new_user capacity: {storage.users['new_user']['capacity']}, used: {storage.users['new_user']['used']}, remaining: {storage.users['new_user']['capacity'] - storage.users['new_user']['used']}")

print(f"\nFile details:")
print(f"  /tmp/file.txt owner: {storage.files['/tmp/file.txt'].get('owner')}, size: {storage.files['/tmp/file.txt']['size']}")

print(f"\nTrying to copy /tmp/file.txt (60 bytes) to /file.txt")
print(f"  Owner: new_user")
print(f"  Current used: {storage.users['new_user']['used']}")
print(f"  Capacity: {storage.users['new_user']['capacity']}")
print(f"  New used would be: {storage.users['new_user']['used'] + 60}")
print(f"  Check: {storage.users['new_user']['used'] + 60} > {storage.users['new_user']['capacity']} = {storage.users['new_user']['used'] + 60 > storage.users['new_user']['capacity']}")

result = storage.copy_file('/tmp/file.txt', '/file.txt')
print(f"\ncopy_file('/tmp/file.txt', '/file.txt'): {result}")
print(f"new_user used after: {storage.users['new_user']['used']}")
if '/file.txt' in storage.files:
    print(f"  /file.txt was created! owner: {storage.files['/file.txt'].get('owner')}, size: {storage.files['/file.txt']['size']}")
else:
    print(f"  /file.txt was NOT created")

