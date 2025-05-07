from diskcache import Cache  # not FanoutCache or anything else
import os

DISKCACHE_DIR = os.getenv("DISKCACHE_DIR", "/tmp/diskcache_ulog")
DISKCACHE_SIZE = int(os.getenv("DISKCACHE_SIZE", str(1 * 1024**3)))

cache = Cache(directory=DISKCACHE_DIR, size_limit=DISKCACHE_SIZE)
