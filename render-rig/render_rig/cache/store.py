import boto3
import json

s3 = boto3.client("s3")
BUCKET = "flight-px4-logs"

def chart_exists(log_id, chart_name):
    try:
        s3.head_object(Bucket=BUCKET, Key=f"{log_id}/{chart_name}.json")
        return True
    except s3.exceptions.ClientError:
        return False

def save_chart_json(fig, log_id, chart_name):
    json_bytes = fig.to_json().encode("utf-8")
    s3.put_object(Bucket=BUCKET, Key=f"{log_id}/{chart_name}.json", Body=json_bytes)

def get_chart_json(log_id, chart_name):
    obj = s3.get_object(Bucket=BUCKET, Key=f"{log_id}/{chart_name}.json")
    return json.loads(obj['Body'].read())
