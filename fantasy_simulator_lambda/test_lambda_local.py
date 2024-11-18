import json
import os
import sys

from lambda_function import lambda_handler

with open("data/sample_input.json") as f:
    event_data = json.load(f)

event = {"body": json.dumps(event_data)}

response = lambda_handler(event, None)

print("Response:")
body = json.loads(response["body"])

print(json.dumps(body, indent=2))
