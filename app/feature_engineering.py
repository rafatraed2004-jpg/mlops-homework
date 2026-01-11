import hashlib


def hashed_feature(value: str, num_buckets: int) -> int:
    if num_buckets <= 0:
        raise ValueError("num_buckets must be > 0")
    if value is None:
        raise ValueError("value must not be None")

    digest = hashlib.md5(value.encode("utf-8")).hexdigest()
    as_int = int(digest, 16)
    return as_int % num_buckets
