import threading
import uuid
from render_rig2.utils.redis_status import set_task_status, get_task_status
import time

NUM_TASKS = 100
TTL_SECONDS = 300
missing_keys = []

def simulate_task(i):
    task_id = f"task1_{uuid.uuid4().hex}"
    payload = {
        "task_status": "success",
        "chart": f"chart_{i}",
        "index": i
    }
    set_task_status(task_id, payload, ttl_seconds=TTL_SECONDS)
    # Verify write
    # time.sleep(1)
    result = get_task_status(task_id)
    if result is None:
        print(f"[FAIL] Task {i} not found in Redis")
        missing_keys.append(task_id)
    else:
        print(f"[OK] Task {i} written and read back")

def main():
    threads = []
    for i in range(NUM_TASKS):
        t = threading.Thread(target=simulate_task, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"\n🔍 {len(missing_keys)} / {NUM_TASKS} keys missing")
    if missing_keys:
        with open("missing_keys.log", "w") as f:
            for k in missing_keys:
                f.write(k + "\n")

if __name__ == "__main__":
    main()
