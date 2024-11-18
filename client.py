from flask import Flask, jsonify



app = Flask(__name__)

@app.route("/generate", methods=['GET'])
def generate_review_date(id=1, increment=60):
	return jsonify({"increment": increment})

if __name__ == "__main__":
	app.run(port=8001)

