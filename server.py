from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate


# Configuration
Base = declarative_base()

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()


class Review(db.Model):
	__tablename__ = 'reviews'
	id = Column(Integer, Sequence('review_id_seq'), primary_key=True)
	review_date = db.Column(db.Date, nullable=False)

# # Set up the database engine and session
# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)  # `echo=True` will log SQL queries
# SessionLocal = sessionmaker(bind=engine)

generate_microservice_url = "http://127.0.0.1:8001/generate"

# Calling the random number generator microservice
def generate_review_date():
	response = requests.get(generate_microservice_url)
	data = response.json()
	increment = data.get("increment")
	if increment is None:
		raise ValueError("No 'increment' value in response")
	return increment

# Function to check if a review date exists and find the next available date
def get_available_review_date(start_date: datetime):
    review_date = start_date
    while True:
        # Check if the review date already exists in the database
        existing_review = db.session.query(Review).filter(Review.review_date == review_date).first()
        if not existing_review:
            # If no review exists on this date, return this date
            return review_date
        # If the review date exists, increment by 1 day and repeat the check
        review_date += timedelta(days=1)

@app.route("/schedule", methods=['GET'])
def schedule_review_date():
	start_time = datetime.now()
	message = generate_review_date()
	review_date_object = datetime.now() + timedelta(days=message)
	review_date_striped = review_date_object.date()
	scheduled_date = get_available_review_date(review_date_striped)
	
	# Add the new review date to the database
	review = Review(review_date=scheduled_date)
	db.session.add(review)
	db.session.commit()
	app.logger.info(f"Review scheduled for {scheduled_date}")
	
	# Logging time to complete 
	end_time = datetime.now()
	reload_time = end_time - start_time
	app.logger.info(f"Page reload time to schedule review date: {reload_time.total_seconds()} seconds")
	return jsonify({"result": scheduled_date})

if __name__ == "__main__":
	app.run(port=8002)
