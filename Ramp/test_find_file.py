#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def test_find_file():
    storage = CloudStorageImpl()
    
    print("=" * 60)
    print("Testing find_file Method (Level 2)")
    print("=" * 60)
    
    print("\n1. Setup: Adding test files")
    storage.add_file("/docs/report.txt", 100)
    storage.add_file("/docs/data.txt", 50)
    storage.add_file("/files/report.pdf", 200)
    storage.add_file("/files/notes.txt", 75)
    storage.add_file("/temp/file.log", 30)
    print("   Added 5 files")
    
    print("\n2. Find files with prefix='/docs/' and suffix='.txt'")
    result = storage.find_file("/docs/", ".txt")
    print(f"   Result: {result}")
    print(f"   Expected: ['/docs/report.txt(100)', '/docs/data.txt(50)']")
    assert result == ['/docs/report.txt(100)', '/docs/data.txt(50)'], f"Unexpected result: {result}"
    
    print("\n3. Find files with prefix='/' and suffix='.txt'")
    result = storage.find_file("/", ".txt")
    print(f"   Result: {result}")
    expected = ['/docs/report.txt(100)', '/files/notes.txt(75)', '/docs/data.txt(50)']
    print(f"   Expected: {expected}")
    assert result == expected, f"Unexpected result: {result}"
    
    print("\n4. Find files with prefix='/files/' and suffix='.pdf'")
    result = storage.find_file("/files/", ".pdf")
    print(f"   Result: {result}")
    expected = ['/files/report.pdf(200)']
    print(f"   Expected: {expected}")
    assert result == expected, f"Unexpected result: {result}"
    
    print("\n5. Find files with non-matching pattern")
    result = storage.find_file("/nonexistent/", ".txt")
    print(f"   Result: {result}")
    print(f"   Expected: []")
    assert result == [], f"Expected empty list, got: {result}"
    
    print("\n6. Testing sorting with same size (lexicographic)")
    storage2 = CloudStorageImpl()
    storage2.add_file("/zoo.txt", 100)
    storage2.add_file("/apple.txt", 100)
    storage2.add_file("/banana.txt", 100)
    result = storage2.find_file("/", ".txt")
    print(f"   Result: {result}")
    expected = ['/apple.txt(100)', '/banana.txt(100)', '/zoo.txt(100)']
    print(f"   Expected: {expected}")
    assert result == expected, f"Lexicographic sorting failed: {result}"
    
    print("\n7. Testing with various sizes")
    storage3 = CloudStorageImpl()
    storage3.add_file("/file1.txt", 300)
    storage3.add_file("/file2.txt", 100)
    storage3.add_file("/file3.txt", 200)
    storage3.add_file("/file4.txt", 100)
    result = storage3.find_file("/", ".txt")
    print(f"   Result: {result}")
    expected = ['/file1.txt(300)', '/file3.txt(200)', '/file2.txt(100)', '/file4.txt(100)']
    print(f"   Expected: {expected}")
    assert result == expected, f"Size sorting failed: {result}"
    
    print("\n" + "=" * 60)
    print("✓ All find_file tests passed!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_find_file()
        print("\nSUCCESS: Level 2 find_file implementation is working!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

