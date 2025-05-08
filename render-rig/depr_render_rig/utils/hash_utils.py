import hashlib

def hash_bytes_sha256(data: bytes) -> str:
    """
    Compute SHA-256 hash of a bytes-like object.

    :param data: Input data in bytes.
    :return: Hexadecimal SHA-256 hash string.
    """
    return hashlib.sha256(data).hexdigest()