from abc import ABC

class CloudStorage(ABC):
    """
    `CloudStorage` interface.
    """

    def add_file(self, name: str, size: int) -> bool:
        """
        Should add a new file `name` to the storage.
        `size` is the amount of memory required in bytes.
        The current operation fails if a file with the same `name`
        already exists.
        Returns `True` if the file was added successfully or `False`
        otherwise.
        """
        # default implementation
        return False

    def copy_file(self, name_from: str, name_to: str) -> bool:
        """
        Should copy the file at `name_from` to `name_to`.
        The operation fails if `name_from` points to a file that
        does not exist or points to a directory.
        The operation fails if the specified file already exists at
        `name_to`.
        Returns `True` if the file was copied successfully or
        `False` otherwise.
        """
        # default implementation
        return False

    def get_file_size(self, name: str) -> int | None:
        """
        Should return the size of the file `name` if it exists, or
        `None` otherwise.
        """
        # default implementation
        return None

    def find_file(self, prefix: str, suffix: str) -> list[str]:
        """
        Should search for files with names starting with `prefix`
        and ending with `suffix`.
        Returns a list of strings representing all matching files in
        this format:
        `["<name_1>(<size_1>)", "<name_2>(<size_2>)", ...]`.
        The output should be sorted in descending order of file
        sizes or, in the case of ties,
        [lexicographically](keyword://lexicographical-order-for-
        strings).
        If no files match the required properties, should return an
        empty list.
        """
        # default implementation
        return []


    def add_user(self, user_id: str, capacity: int) -> bool:
        """
        Should add a new user to the system, with `capacity` as
        their storage limit in bytes.
        The total size of all files owned by `user_id` cannot exceed
        `capacity`.
        The operation fails if a user with `user_id` already exists.
        Returns `True` if a user with `user_id` is successfully
        created, or `False` otherwise.
        """
        # default implementation
        return False

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        """
        Should behave in the same way as the `add_file` from Level
        1, but the added file should be owned by the user with
        `user_id`.
        A new file cannot be added to the storage if doing so will
        exceed the user's `capacity` limit.
        Returns the remaining storage capacity for `user_id` if the
        file is successfully added or `None` otherwise.
        
        *Note that* all queries calling the `add_file` operation
        implemented during Level 1 are run by the user with
        `user_id = "admin"`, who has unlimited storage capacity.
        Also, assume that the `copy_file` operation preserves the
        ownership of the original file.
        """
        # default implementation
        return None

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        """
        Should change the maximum storage capacity for the user with
        `user_id`.
        If the total size of all user's files exceeds the new
        `capacity`, the largest files (sorted
        [lexicographically](keyword://lexicographical-order-for-
        strings) in case of a tie) should be removed from the
        storage until the total size of all remaining files will no
        longer exceed the new `capacity`.
        Returns the number of removed files, or `None` if a user
        with `user_id` does not exist.
        """
        # default implementation
        return None

    def compress_file(self, user_id: str, name: str) -> int | None:
        """
        Should compress the file `name` if it belongs to `user_id`.
        The compressed file should be replaced with a new file named
        `<name>.COMPRESSED`.
        The size of the newly created file should be equal to the
        half of the original file.
        The size of all files is guaranteed to be even, so there
        should be no fractional calculations.
        It is also guaranteed that `name` for this operation never
        points to a compressed file - i.e., it never ends with
        `.COMPRESSED`.
        Compressed files should be owned by `user_id` — the owner of
        the original file.
        Returns the remaining storage capacity for `user_id` if the
        file was compressed successfully or `None` otherwise.
        
        *Note that* because file names can only contain lowercase
        letters, compressed files cannot be added via `add_file`.
        *It is guaranteed* that all `copy_file` operations will
        preserve the suffix `.COMPRESSED`.
        """
        # default implementation
        return None

    def decompress_file(self, user_id: str, name: str) -> int | None:
        """
        Should revert the compression of the file `name` if it
        belongs to `user_id`.
        It is guaranteed that `name` for this operation always ends
        with `.COMPRESSED`.
        If decompression results in the `user_id` exceeding their
        storage capacity limit or a decompressed version of the file
        with the given name already exists, the operation fails.
        Returns the remaining capacity of `user_id` if the file was
        decompressed successfully or `None` otherwise.
        """
        # default implementation
        return None
