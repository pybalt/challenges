#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def test_level_4_basic():
    print("=" * 70)
    print("Testing Level 4: Compression and Decompression")
    print("=" * 70)
    
    storage = CloudStorageImpl()
    
    print("\n### Test 1: Basic Compression ###")
    storage.add_user('user1', 1000)
    storage.add_file_by('user1', '/file.txt', 100)
    print(f"  Added file: 100 bytes, remaining: {storage.users['user1']['used']}")
    
    result = storage.compress_file('user1', '/file.txt')
    print(f"  compress_file result: {result} (Expected: 950)")
    assert result == 950, f"Expected 950, got {result}"
    
    assert storage.get_file_size('/file.txt') is None, "Original file should be deleted"
    assert storage.get_file_size('/file.txt.COMPRESSED') == 50, "Compressed file should be 50 bytes"
    print(f"  ✓ Compression successful")
    
    print("\n### Test 2: Basic Decompression ###")
    result = storage.decompress_file('user1', '/file.txt.COMPRESSED')
    print(f"  decompress_file result: {result} (Expected: 900)")
    assert result == 900, f"Expected 900, got {result}"
    
    assert storage.get_file_size('/file.txt') == 100, "Decompressed file should be 100 bytes"
    assert storage.get_file_size('/file.txt.COMPRESSED') is None, "Compressed file should be deleted"
    print(f"  ✓ Decompression successful")
    
    print("\n### Test 3: Compression with Capacity Check ###")
    storage.add_user('user2', 5000)
    storage.add_file_by('user2', '/large.dat', 4000)
    storage.compress_file('user2', '/large.dat')
    print(f"  After compression: used={storage.users['user2']['used']}, remaining={5000 - storage.users['user2']['used']}")
    
    storage.add_file_by('user2', '/medium.dat', 2000)
    print(f"  Added medium file: used={storage.users['user2']['used']}, remaining={5000 - storage.users['user2']['used']}")
    
    result = storage.decompress_file('user2', '/large.dat.COMPRESSED')
    print(f"  Trying to decompress (would need 4000, have {5000 - storage.users['user2']['used']}): {result}")
    assert result is None, "Should fail - not enough capacity"
    print(f"  ✓ Correctly failed decompression due to capacity")
    
    print("\n### Test 4: Ownership Check ###")
    storage.add_user('owner', 5000)
    storage.add_file_by('owner', '/secret.txt', 1000)
    
    storage.add_user('hacker', 9999)
    result = storage.compress_file('hacker', '/secret.txt')
    assert result is None, "Should fail - file doesn't belong to hacker"
    print(f"  ✓ Correctly failed compression - wrong owner")
    
    result = storage.compress_file('owner', '/secret.txt')
    assert result is not None, "Should succeed - correct owner"
    print(f"  ✓ Compression succeeded with correct owner")
    
    result = storage.decompress_file('hacker', '/secret.txt.COMPRESSED')
    assert result is None, "Should fail - file doesn't belong to hacker"
    print(f"  ✓ Correctly failed decompression - wrong owner")
    
    print("\n### Test 5: Collision Check ###")
    storage.add_user('user3', 10000)
    storage.add_file_by('user3', '/music.mp3', 300)
    storage.compress_file('user3', '/music.mp3')
    
    storage.add_file_by('user3', '/music.mp3', 400)
    result = storage.decompress_file('user3', '/music.mp3.COMPRESSED')
    assert result is None, "Should fail - decompressed file already exists"
    print(f"  ✓ Correctly failed decompression - collision")
    
    print("\n### Test 6: Copy Preserves .COMPRESSED ###")
    storage.add_user('user4', 5000)
    storage.add_file_by('user4', '/deep/file.dat', 300)
    storage.compress_file('user4', '/deep/file.dat')
    
    result = storage.copy_file('/deep/file.dat.COMPRESSED', '/copy.dat.COMPRESSED')
    assert result == True, "Should succeed"
    assert storage.get_file_size('/copy.dat.COMPRESSED') == 150, "Copied compressed file should be 150 bytes"
    print(f"  ✓ Copy preserved .COMPRESSED suffix")
    
    print("\n" + "=" * 70)
    print("✓ All Level 4 basic tests passed!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        test_level_4_basic()
        print("\nSUCCESS: Level 4 implementation is working!")
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

