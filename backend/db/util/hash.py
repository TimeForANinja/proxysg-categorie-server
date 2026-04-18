import hashlib


def sha256_hash(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()
