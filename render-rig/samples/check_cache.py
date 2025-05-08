from render_rig2.utils.cache import cache

print("📦 Cached keys:")
for key in cache.iterkeys():
    print("-", key)
cache.clear()