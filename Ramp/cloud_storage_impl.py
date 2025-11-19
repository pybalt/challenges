from cloud_storage import CloudStorage


class CloudStorageImpl(CloudStorage):

    def __init__(self):
        self.files = {}
        self.directories = set()
        self.users = {}
        self.users['admin'] = {'capacity': float('inf'), 'used': 0}

    def _is_directory(self, path: str) -> bool:
        if path in self.directories:
            return True
        for filename in self.files:
            if filename.startswith(path + '/'):
                return True
        return False
    
    def _create_parent_directories(self, path: str):
        parts = path.split('/')
        for depth in range(1, len(parts)):
            parent_directory = '/'.join(parts[:depth])
            if parent_directory:
                self.directories.add(parent_directory)
    
    def add_file(self, name: str, size: int) -> bool:
        return self.add_file_by('admin', name, size) is not None
    
    def copy_file(self, name_from: str, name_to: str) -> bool:
        if name_from not in self.files:
            return False

        if self._is_directory(name_from):
            return False
        
        if name_to in self.files:
            return False
        
        if self._is_directory(name_to):
            return False
        
        source_file = self.files[name_from]
        owner_id = source_file.get('owner', 'admin')
        file_size = source_file['size']
        
        result = self.add_file_by(owner_id, name_to, file_size)
        return result is not None
    
    def get_file_size(self, name: str) -> int | None:
        if name in self.files:
            return self.files[name]['size']
        
        return None
    
    def find_file(self, prefix: str, suffix: str) -> list[str]:
        matching_files = []
        
        for filename, metadata in self.files.items():
            if filename.startswith(prefix) and filename.endswith(suffix):
                file_size = metadata['size']
                matching_files.append((filename, file_size))
        
        FILENAME_INDEX = 0
        FILESIZE_INDEX = 1
        
        # Sort first by size and then by name
        matching_files.sort(
            key=lambda file_tuple: (
                -file_tuple[FILESIZE_INDEX],
                file_tuple[FILENAME_INDEX]
            )
        )
        
        formatted_results = []
        for filename, file_size in matching_files:
            formatted_result = f"{filename}({file_size})"
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self.users:
            return False
        
        self.users[user_id] = {'capacity': capacity, 'used': 0}
        return True
    
    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        if user_id not in self.users:
            return None
        
        if name in self.files:
            return None
        
        if self._is_directory(name):
            return None
        
        user = self.users[user_id]
        
        if user['capacity'] == float('inf'):
            new_used = user['used'] + size
        else:
            remaining = user['capacity'] - user['used']
            if size > remaining:
                return None
            new_used = user['used'] + size
        
        self._create_parent_directories(name)
        self.files[name] = {'size': size, 'owner': user_id}
        user['used'] = new_used
        
        remaining_capacity = user['capacity'] - user['used']
        if remaining_capacity == float('inf'):
            return 10**18
        return int(remaining_capacity)
    
    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        user['capacity'] = capacity
        
        user_files = []
        for filename, metadata in self.files.items():
            if metadata.get('owner', 'admin') == user_id:
                user_files.append((filename, metadata['size']))
        
        if user['used'] <= capacity:
            return 0
        
        FILENAME_INDEX = 0
        FILESIZE_INDEX = 1
        
        user_files.sort(
            key=lambda file_tuple: (
                -file_tuple[FILESIZE_INDEX],
                file_tuple[FILENAME_INDEX]
            )
        )
        
        files_removed = 0
        for filename, file_size in user_files:
            if user['used'] <= capacity:
                break
            
            del self.files[filename]
            user['used'] -= file_size
            files_removed += 1
            
        return files_removed
    
    def compress_file(self, user_id: str, name: str) -> int | None:
        if user_id not in self.users:
            return None
        
        if name not in self.files:
            return None
        
        compressed_name = name + '.COMPRESSED'
        if compressed_name in self.files:
            return None
        
        file_metadata = self.files[name]
        file_owner = file_metadata.get('owner', 'admin')
        
        if file_owner != user_id:
            return None
        
        original_size = file_metadata['size']
        compressed_size = original_size // 2
        
        user = self.users[user_id]
        
        if user['capacity'] == float('inf'):
            new_used = user['used'] - original_size + compressed_size
        else:
            current_used = user['used']
            new_used = current_used - original_size + compressed_size
            
            if new_used > user['capacity']:
                return None
        
        del self.files[name]
        self._create_parent_directories(compressed_name)
        self.files[compressed_name] = {'size': compressed_size, 'owner': user_id}
        user['used'] = new_used
        
        remaining_capacity = user['capacity'] - user['used']
        if remaining_capacity == float('inf'):
            return 10**18
        return int(remaining_capacity)
    
    def decompress_file(self, user_id: str, name: str) -> int | None:
        if user_id not in self.users:
            return None
        
        if not name.endswith('.COMPRESSED'):
            return None
        
        if name not in self.files:
            return None
        
        file_metadata = self.files[name]
        file_owner = file_metadata.get('owner', 'admin')
        
        if file_owner != user_id:
            return None
        
        decompressed_name = name[:-11]
        if decompressed_name in self.files:
            return None
        
        compressed_size = file_metadata['size']
        decompressed_size = compressed_size * 2
        
        user = self.users[user_id]
        
        if user['capacity'] == float('inf'):
            new_used = user['used'] - compressed_size + decompressed_size
        else:
            current_used = user['used']
            new_used = current_used - compressed_size + decompressed_size
            
            if new_used > user['capacity']:
                return None
        
        del self.files[name]
        self._create_parent_directories(decompressed_name)
        self.files[decompressed_name] = {'size': decompressed_size, 'owner': user_id}
        user['used'] = new_used
        
        remaining_capacity = user['capacity'] - user['used']
        if remaining_capacity == float('inf'):
            return 10**18
        return int(remaining_capacity)