from render_rig2.utils.cache import cache

print("📦 Cached keys:")
for key in cache.iterkeys():
    print("-", key)
cache.clear()
print("flight-px4-logs/raw-logs/2025/4/8/file_64c166b0dd104e44bd81adb9bddfb5bb.ulg" in cache)