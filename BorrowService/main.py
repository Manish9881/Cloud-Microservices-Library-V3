from flask import Flask, jsonify, request
import pika
import os
import json
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from threading import Thread

# Flask and SQLAlchemy setup
app = Flask(__name__)

# Database configuration
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# RabbitMQ configuration
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = os.getenv('RABBITMQ_PORT')
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS')

# Model for borrow records
class Borrow(db.Model):
    __tablename__ = 'borrows'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), nullable=False)
    book_id = db.Column(db.String(20), nullable=False)
    date_borrowed = db.Column(db.Date, nullable=False)
    date_returned = db.Column(db.Date, nullable=True)

with app.app_context():
    db.create_all()

# Helper function to validate student_id and book_id
def validate_student_and_book(student_id, book_id):
    user_service_url = os.getenv('USER_SERVICE_URL', 'http://userservice:5002')
    book_service_url = os.getenv('BOOK_SERVICE_URL', 'http://bookservice:5006')

    student_response = requests.get(f"{user_service_url}/users/{student_id}")
    if student_response.status_code != 200:
        return False, "Invalid student ID"

    book_response = requests.get(f"{book_service_url}/books/{book_id}")
    if book_response.status_code != 200:
        return False, "Invalid book ID"

    return True, None

# Helper function to check if a student has borrowed more than 5 books
def can_borrow_more_books(student_id):
    borrowed_count = Borrow.query.filter_by(student_id=student_id, date_returned=None).count()
    return borrowed_count < 5

# RabbitMQ callback function to process borrow requests
def on_borrow_request(ch, method, properties, body):
    with app.app_context():
        try:
            print(f"Received message: {body}")
            data = json.loads(body)
            student_id = data.get('student_id')
            book_id = data.get('book_id')

            is_valid, error_message = validate_student_and_book(student_id, book_id)
            if not is_valid:
                print(f"Validation failed: {error_message}")
                ch.basic_nack(delivery_tag=method.delivery_tag)
                return

            if not can_borrow_more_books(student_id):
                print(f"Student {student_id} exceeded borrow limit.")
                ch.basic_nack(delivery_tag=method.delivery_tag)
                return

            borrow_record = Borrow(
                student_id=student_id,
                book_id=book_id,
                date_borrowed=datetime.now().date(),
                date_returned=None
            )
            db.session.add(borrow_record)
            db.session.commit()
            print(f"Borrow record saved: {borrow_record}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

# Background thread to run the consumer
def start_consumer():
    print("Starting RabbitMQ consumer...")
    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbitmq_host,
            port=int(rabbitmq_port),
            credentials=credentials,
            heartbeat=30
        ))
        channel = connection.channel()
        channel.queue_declare(queue='borrow_book', durable=True)
        print("Consumer is now waiting for messages...")
        channel.basic_consume(queue='borrow_book', on_message_callback=on_borrow_request, auto_ack=False)
        channel.start_consuming()
    except Exception as e:
        print(f"Error in RabbitMQ consumer: {e}")

consumer_thread = Thread(target=start_consumer)
consumer_thread.start()

# Endpoint to get all books borrowed by a specific student
@app.route('/borrows/<student_id>', methods=['GET'])
def get_borrows_by_student(student_id):
    borrows = Borrow.query.filter_by(student_id=student_id).all()
    return jsonify([{
        "student_id": borrow.student_id,
        "book_id": borrow.book_id,
        "date_borrowed": borrow.date_borrowed.strftime('%Y-%m-%d'),
        "date_returned": borrow.date_returned.strftime('%Y-%m-%d') if borrow.date_returned else None
    } for borrow in borrows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
