import asyncio
import httpx
import pandas as pd
import random
import time

from render_rig2.database_access.sessions.log_registry_session_local import LogRegistrySessionLocal
from render_rig2.database_access.models.log_registry_model import LogsDlReg

# Step 1: Get all log_ids from DB
def get_all_log_ids(session):
    try:
        return [row[0] for row in session.query(LogsDlReg.log_id).all()]
    except Exception as e:
        print(f"Error: {e}")
        return []

# Step 2: Sample subset
def sample_log_ids(log_ids, sample_size=100):
    return random.sample(log_ids, sample_size) if len(log_ids) > sample_size else log_ids

# Step 3: Construct chart generator URLs
def construct_urls(log_ids, chart_name="chart_accel_raw_xyz"):
    base_url = "http://render-rig2-alb-830325047.us-east-1.elb.amazonaws.com/chart_generator"
    return [f"{base_url}/{log_id}/{chart_name}" for log_id in log_ids]

# Step 4: Async fetch basic metrics
async def fetch(client, url):
    start = time.time()
    try:
        response = await client.get(url, timeout=3600)
        duration = time.time() - start
        return {
            "url": url,
            "status_code": response.status_code,
            "response_time_sec": duration,
            "response_size_mb": len(response.content) / (1024 * 1024),
        }
    except Exception:
        return {
            "url": url,
            "status_code": None,
            "response_time_sec": None,
            "response_size_mb": None,
        }

# Step 5: Run all requests
async def run_all(urls):
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, url) for url in urls]
        return await asyncio.gather(*tasks)

# Step 6: Main function with sample_size param
def main(sample_size=100):
    db = LogRegistrySessionLocal()
    log_ids = sample_log_ids(get_all_log_ids(db), sample_size)
    db.close()
    urls = construct_urls(log_ids)

    import nest_asyncio
    nest_asyncio.apply()

    results = asyncio.run(run_all(urls))
    df = pd.DataFrame(results)
    # print(df)
    # Save to CSV
    df.to_csv("async_api_call_results.csv", index=False)
    return df

# Entry point
if __name__ == "__main__":
    main(sample_size=100)
