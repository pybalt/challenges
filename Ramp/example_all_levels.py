#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def main():
    storage = CloudStorageImpl()
    
    print("=" * 80)
    print("Cloud Storage System - Complete Feature Demo (Levels 1-3)")
    print("=" * 80)
    
    print("\n" + "="*80)
    print("LEVEL 1: Basic File Operations")
    print("="*80)
    
    print("\n→ Adding files (as admin with unlimited capacity):")
    storage.add_file("/projects/report.pdf", 500)
    storage.add_file("/projects/notes.txt", 150)
    storage.add_file("/documents/invoice.pdf", 300)
    print("  ✓ Added 3 files")
    
    print("\n→ Copying files:")
    storage.copy_file("/projects/report.pdf", "/backup/report.pdf")
    print("  ✓ Copied report.pdf to backup")
    
    print("\n→ Getting file sizes:")
    print(f"  /projects/report.pdf: {storage.get_file_size('/projects/report.pdf')} bytes")
    print(f"  /backup/report.pdf: {storage.get_file_size('/backup/report.pdf')} bytes")
    print(f"  /nonexistent.txt: {storage.get_file_size('/nonexistent.txt')}")
    
    print("\n" + "="*80)
    print("LEVEL 2: Finding Files")
    print("="*80)
    
    storage.add_file("/media/video.mp4", 2000)
    storage.add_file("/media/audio.mp3", 800)
    storage.add_file("/temp/log.txt", 50)
    
    print("\n→ Find all PDF files:")
    results = storage.find_file("/", ".pdf")
    for result in results:
        print(f"  • {result}")
    
    print("\n→ Find all files in /projects/:")
    results = storage.find_file("/projects/", "")
    for result in results:
        print(f"  • {result}")
    
    print("\n→ Find all .txt files:")
    results = storage.find_file("/", ".txt")
    for result in results:
        print(f"  • {result}")
    
    print("\n" + "="*80)
    print("LEVEL 3: User Management with Capacity Limits")
    print("="*80)
    
    print("\n→ Creating users with capacity limits:")
    storage.add_user("alice", 1000)
    storage.add_user("bob", 500)
    print("  ✓ Created user 'alice' with 1000 bytes capacity")
    print("  ✓ Created user 'bob' with 500 bytes capacity")
    
    print("\n→ Alice adds files:")
    remaining = storage.add_file_by("alice", "/alice/project.zip", 400)
    print(f"  • Added project.zip (400 bytes), remaining: {remaining} bytes")
    
    remaining = storage.add_file_by("alice", "/alice/notes.txt", 300)
    print(f"  • Added notes.txt (300 bytes), remaining: {remaining} bytes")
    
    remaining = storage.add_file_by("alice", "/alice/large.dat", 500)
    if remaining is None:
        print(f"  ✗ Cannot add large.dat (500 bytes) - exceeds capacity!")
    
    print("\n→ Bob adds files:")
    remaining = storage.add_file_by("bob", "/bob/file1.txt", 200)
    print(f"  • Added file1.txt (200 bytes), remaining: {remaining} bytes")
    
    remaining = storage.add_file_by("bob", "/bob/file2.txt", 250)
    print(f"  • Added file2.txt (250 bytes), remaining: {remaining} bytes")
    
    print("\n→ Updating Bob's capacity (reducing from 500 to 300 bytes):")
    files_removed = storage.update_capacity("bob", 300)
    print(f"  • Removed {files_removed} file(s) to fit new capacity")
    print(f"  • Largest file (file2.txt) was removed")
    print(f"  • Remaining file: /bob/file1.txt = {storage.get_file_size('/bob/file1.txt')} bytes")
    print(f"  • Removed file: /bob/file2.txt = {storage.get_file_size('/bob/file2.txt')}")
    
    print("\n→ Searching Alice's files:")
    results = storage.find_file("/alice/", "")
    for result in results:
        print(f"  • {result}")
    
    print("\n→ Admin still has unlimited capacity:")
    storage.add_file("/admin/huge_database.db", 999999999)
    print(f"  ✓ Admin added huge file: {storage.get_file_size('/admin/huge_database.db')} bytes")
    
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    print("\n→ All files in system:")
    all_files = storage.find_file("/", "")
    print(f"  Total files: {len(all_files)}")
    for result in all_files[:10]:
        print(f"  • {result}")
    if len(all_files) > 10:
        print(f"  ... and {len(all_files) - 10} more")
    
    print("\n" + "="*80)
    print("✓ Demo completed successfully!")
    print("="*80)

if __name__ == '__main__':
    main()

