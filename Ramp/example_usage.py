#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_storage_impl import CloudStorageImpl

def main():
    storage = CloudStorageImpl()
    
    print("=" * 70)
    print("Cloud Storage System - Example Usage")
    print("=" * 70)
    
    print("\n### Level 1: Basic Operations ###\n")
    
    print("Adding files:")
    storage.add_file("/projects/report.pdf", 500)
    storage.add_file("/projects/notes.txt", 150)
    storage.add_file("/documents/invoice.pdf", 300)
    storage.add_file("/documents/contract.pdf", 450)
    storage.add_file("/temp/log.txt", 50)
    storage.add_file("/temp/cache.txt", 75)
    print("  ✓ Added 6 files")
    
    print("\nCopying a file:")
    storage.copy_file("/projects/report.pdf", "/backup/report.pdf")
    print("  ✓ Copied /projects/report.pdf to /backup/report.pdf")
    
    print("\nGetting file sizes:")
    print(f"  /projects/report.pdf: {storage.get_file_size('/projects/report.pdf')} bytes")
    print(f"  /temp/log.txt: {storage.get_file_size('/temp/log.txt')} bytes")
    print(f"  /nonexistent.txt: {storage.get_file_size('/nonexistent.txt')}")
    
    print("\n### Level 2: Finding Files ###\n")
    
    print("Find all PDF files:")
    results = storage.find_file("/", ".pdf")
    for result in results:
        print(f"  - {result}")
    
    print("\nFind all files in /projects/:")
    results = storage.find_file("/projects/", "")
    for result in results:
        print(f"  - {result}")
    
    print("\nFind all .txt files in /temp/:")
    results = storage.find_file("/temp/", ".txt")
    for result in results:
        print(f"  - {result}")
    
    print("\nFind files starting with /documents/ and ending with .pdf:")
    results = storage.find_file("/documents/", ".pdf")
    for result in results:
        print(f"  - {result}")
    
    print("\n### Demonstrating Sorting ###\n")
    
    storage2 = CloudStorageImpl()
    storage2.add_file("/file_large.dat", 1000)
    storage2.add_file("/file_small.dat", 100)
    storage2.add_file("/file_medium.dat", 500)
    storage2.add_file("/file_another.dat", 500)  # Same size as medium
    
    print("Files sorted by size (descending), then alphabetically:")
    results = storage2.find_file("/", ".dat")
    for result in results:
        print(f"  - {result}")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)

if __name__ == '__main__':
    main()

