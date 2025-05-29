import requests
from pprint import pprint
from pymongo import MongoClient

# Connect to MongoDB running on localhost
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["render-rig2-tasks"]
collection = db["group1"]

# Poll Celery Flower for tasks
poll_url = "http://localhost:5555/api/tasks"
response = requests.get(poll_url)

if response.status_code == 200:
    tasks = response.json()
    print(len(tasks), "tasks found.")

    for k, v in tasks.items():
        doc = {
            "_id": k,      # Use the task ID as the unique identifier
            "value": v     # Store the task metadata under 'value'
        }

        result = collection.update_one(
            {"_id": k},
            {"$set": doc},
            upsert=True
        )

        action = "Upserted" if result.upserted_id else "Updated"
        print(f"{action} task {k}")
else:
    print("No tasks found.")
