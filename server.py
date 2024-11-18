from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

random_microservice_url = "http://127.0.0.1:8001/generate"

# Calling the random number generator microservice
def generate_review_date():
	response = requests.get(random_microservice_url)
	return response.json().get("increment")

@app.route("/schedule", methods=['GET'])
def schedule_review_date():
	message = generate_review_date()
	reviewDate = datetime.now() + timedelta(days=message)
	return jsonify({"result": reviewDate})

if __name__ == "__main__":
	app.run(port=8002)
