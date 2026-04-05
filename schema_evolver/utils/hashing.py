import hashlib

def hash_string(data: str) -> str:
    """Computes a SHA-256 hash of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
