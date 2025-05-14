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

# Step 4: Async fetch with rate limit
async def fetch(client, url, semaphore, delay_sec):
    async with semaphore:
        await asyncio.sleep(delay_sec)  # delay before sending
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

# Step 5: Run all requests with rate limiting
async def run_all(urls, rate_per_minute=60):
    semaphore = asyncio.Semaphore(1)  # Only 1 request at a time
    delay_sec = 60 / rate_per_minute  # Delay between each request

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch(client, url, semaphore, delay_sec * i)
            for i, url in enumerate(urls)
        ]
        return await asyncio.gather(*tasks)

# Step 6: Main function
db = LogRegistrySessionLocal()
log_ids = sample_log_ids(get_all_log_ids(db), 50)
db.close()
urls = construct_urls(log_ids)
import requests
from time import perf_counter


for i in urls:
    start = perf_counter()
    result = requests.get(i)
    end = perf_counter()
    print(f"URL: {i}, Status Code: {result.status_code}, Response Time: {end - start:.2f} seconds, Size: {len(result.content) / (1024 * 1024):.2f} MB")
    time.sleep(1)
