# Cloud Storage System

A simple in-memory cloud storage system that manages files and their metadata.

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

Run all Level 1 tests:
```bash
python -m unittest test_level_1.Level1Tests -v
```

Run a single test:
```bash
bash run_single_test.sh "test_level_1.Level1Tests.test_level_1_case_01_add_and_get_file_in_directory"
```

## Features

### Level 1
- `add_file(name, size)` - Add a new file to storage
- `copy_file(name_from, name_to)` - Copy a file from one location to another
- `get_file_size(name)` - Get the size of a file

### Level 2
- `find_file(prefix, suffix)` - Find files matching prefix and suffix patterns
  - Returns list in format: `["<name>(<size>)", ...]`
  - Sorted by size (descending), then lexicographically by name

### Level 3
- `add_user(user_id, capacity)` - Add a user with storage capacity limit (in bytes)
  - Returns `True` if successful, `False` if user already exists
- `add_file_by(user_id, name, size)` - Add a file owned by a specific user
  - Checks if adding the file would exceed user's capacity
  - Returns remaining capacity if successful, `None` otherwise
  - Note: `add_file()` from Level 1 uses 'admin' user with unlimited capacity
- `update_capacity(user_id, capacity)` - Update user's storage capacity
  - If new capacity is exceeded, removes largest files (lexicographically on ties)
  - Returns number of files removed, or `None` if user doesn't exist
  - Note: `copy_file()` preserves ownership of the original file

### Level 4
- `compress_file(user_id, name)` - Compress a file owned by the user
  - Replaces original file with `<name>.COMPRESSED`
  - Compressed size = original size / 2 (original size guaranteed to be even)
  - Returns remaining capacity if successful, `None` otherwise
  - Fails if user/file doesn't exist, file doesn't belong to user, or compressed file already exists
- `decompress_file(user_id, name)` - Decompress a `.COMPRESSED` file owned by the user
  - Replaces compressed file with original name (without `.COMPRESSED` suffix)
  - Decompressed size = compressed size * 2
  - Returns remaining capacity if successful, `None` otherwise
  - Fails if user/file doesn't exist, file doesn't belong to user, decompressed file already exists, or would exceed capacity
  - Note: `copy_file()` preserves the `.COMPRESSED` suffix

## Implementation

The implementation is in `cloud_storage_impl.py` which extends the `CloudStorage` interface from `cloud_storage.py`.

