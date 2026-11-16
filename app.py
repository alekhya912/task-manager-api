from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Task database model
class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    completed = db.Column(db.Boolean, default=False)

@app.route("/")
def home():
    return "Welcome to Task Manager API!"

# GET API - View all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    all_tasks=Task.query.all()
    task_list=[]
    for task in all_tasks:
        task_list.append({
            "id":task.id,
            "title":task.title,
            "completed":task.completed
        })
    return jsonify(task_list),200

# POST API - Add a new task
@app.route("/tasks", methods=["POST"])
def add_task():

    new_data=request.get_json()
    new_task=Task(
        title=new_data["title"],
        completed=new_data["completed"]
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        "id":new_task.id,
        "title":new_task.title,
        "completed":new_task.completed
    }),200

# PUT API - Update an existing task
@app.route("/tasks/<int:task_id>", methods=["PUT"])  
def update_task(task_id):
    new_data=request.get_json()
    t=Task.query.filter_by(id=task_id).first()

    if t is None:
        return jsonify({"message":"Task not found"}),404
    
    t.title=new_data["title"]
    t.completed=new_data["completed"]
    db.session.commit()
    return jsonify({
        "id":t.id,
        "title":t.title,
        "completed":t.completed
    }),200


# DELETE API - Delete an existing task
@app.route("/tasks/<int:task_id>",methods=["DELETE"])
def delete_task(task_id):

    t=Task.query.filter_by(id=task_id).first()

    if t is None:
        return jsonify({"message": "Task not found"}),404
    
    db.session.delete(t)
    db.session.commit()
    return jsonify({
        "message":"Task deleted successfully!"
    }),200


@app.route("/db-test")
def db_test():
    try:
        db.session.execute(text("SELECT 1"))
        return "Database connected successfully!"

    except Exception as e:
        return f"Database connection failed: {e}", 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)