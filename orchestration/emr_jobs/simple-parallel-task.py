from pyspark.sql import SparkSession
import os
from random import randint
import json
import boto3
from uuid import uuid4

def generate_random_worker_ids(num=10, lower_limit=1000, upper_limit=9999):
    return [randint(lower_limit, upper_limit) for _ in range(num)]

def log_ids_on_worker(worker_id):
    import random
    import socket
    from datetime import datetime
    hostname = socket.gethostname()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_dict = dict()
    output_dict["worker_id"] = worker_id
    output_dict["hostname"] = hostname
    output_dict["time"] = current_time
    output_dict["random_number"] = random.randint(1, 100)
    return output_dict


# 1. Start Spark session
spark = SparkSession.builder.appName("LogIDTest").getOrCreate()
sc = spark.sparkContext

# 2. log_ids on driver
log_ids = generate_random_worker_ids()

# 3. Dummy RDD to parallelize logging
rdd = sc.parallelize(range(300), numSlices=6)  # creates 300

# 5. Trigger action to run tasks
results = rdd.map(log_ids_on_worker).collect()

output_string = json.dumps(results, indent=4, sort_keys=True)
s3 = boto3.client("s3")
s3_key = f"ec2-info/log-{uuid4()}.json"
s3.put_object(Bucket="flight-px4-logs", Key=s3_key, Body=output_string, ContentType="application/json")

# 6. Stop session
spark.stop()
