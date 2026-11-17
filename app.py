from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
import os,math
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

# GET API - Retrieve all the tasks by using query parameters
@app.route("/tasks", methods=["GET"])
def get_tasks():
    completed=request.args.get("completed")
    sort_order=request.args.get("sort")

    query=Task.query  # Start with all tasks

    # Filtering
    if completed=="true":
        query=query.filter_by(completed=True)
    elif completed=="false":
        query=query.filter_by(completed=False)
    elif completed is not None:
        return jsonify({"message":"Invalid completed query param value"})

    #Sorting
    if sort_order=="asc" or sort_order is None:
        query=query.order_by(Task.id.asc())
    elif sort_order=="desc":
        query=query.order_by(Task.id.desc())
    elif sort_order is not None:
        return jsonify({"message":"Invalid sort query param value"})

    # Applying PAGINATION 
    page = request.args.get("page", "1")   # Here 1 is default pages when nothing is mentioned in query param
    per_page = request.args.get("per_page", "3")  # Here 3 is default tasks per page when nothing is mentioned in query param
    
    if not page.isdigit() or not per_page.isdigit():
        return jsonify({"message":"Page and per page values must be integers"}),400

    page=int(page)
    per_page=int(per_page)

    if page < 1 or per_page < 1:
        return jsonify({"message": "Page and per_page must be positive integers"}), 400

    total_tasks = query.count()    # Retrieves total count of tasks

    total_pages= math.ceil((total_tasks/per_page))

    all_tasks = query.limit(per_page).offset((page - 1) * per_page).all()

    task_list=[]
    for task in all_tasks:
        task_list.append({
            "id":task.id,
            "title":task.title,
            "completed":task.completed
        })
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total_tasks": total_tasks,
        "total_pages": total_pages,
        "tasks": task_list
        }), 200
    

# POST API - Add a new task
@app.route("/tasks", methods=["POST"])
def add_task():

    new_data=request.get_json()

# Input validation in POST

    # To validate whether input is a dictionary and if it is a dict then it is not empty
    if not isinstance(new_data, dict) or not new_data:
            return jsonify({"message": "Request body must be a non-empty JSON object"}), 400

    # To validate whether input contains title
    if "title" not in new_data:
        return jsonify({"message":"Please provide a title for your task"}),400

    # To validate whether title is a string
    if not isinstance(new_data["title"],str):
        return jsonify({"message":"Title must be a string"}),400

    # To validate whether title is not empty
    if not new_data["title"].strip():
        return jsonify({"message":"Title can't be an empty string"}),400

    # To validate whether completed exists in input and if exists to validate whether it is a boolean 
    if "completed" in new_data and not isinstance(new_data["completed"], bool):
        return jsonify({"message": "Completed must be a boolean"}), 400

    new_task=Task(
        title=new_data["title"],
        completed=new_data.get("completed",False)  # makes completed value as false(default) if not provided in input
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

# Input validation in PUT

    # To validate whether input is a dictionary and if it is a dict then it is not empty
    if not isinstance(new_data, dict) or not new_data:
        return jsonify({"message": "Request body must be a non-empty JSON object"}), 400

    t=Task.query.filter_by(id=task_id).first()

    # To validate the the task id exists
    if t is None:
        return jsonify({"message":"Task not found"}),404
    
    # To validate whether input contains title
    if "title" not in new_data:
        return jsonify({"message":"Please provide a title for your task"}),400

    # To validate whether title is a string
    if not isinstance(new_data["title"],str):
        return jsonify({"message":"Title must be a string"}),400
    
    # To validate whether title is empty
    if not new_data["title"].strip():
        return jsonify({"message":"Title can't be an empty string"}),400

    # To validate whether input contains completed
    if "completed" not in new_data:
        return jsonify({"message": "Completed status is required"}), 400

    # To validate whether completed is a boolean
    if not isinstance(new_data["completed"], bool):
        return jsonify({"message": "Completed must be a boolean"}), 400

    t.title=new_data["title"]
    t.completed=new_data["completed"]
    db.session.commit()
    return jsonify({
        "id":t.id,
        "title":t.title,
        "completed":t.completed
    }),200

# PATCH API - Updates selected fields
@app.route("/tasks/<int:task_id>",methods=["PATCH"])
def patch_task(task_id):
    new_data=request.get_json()
    
    # To validate whether input is a dictionary and if it is a dict then it is not empty
    if not isinstance(new_data, dict) or not new_data:
        return jsonify({"message": "Request body must be a non-empty JSON object"}), 400

    t=Task.query.filter_by(id=task_id).first()
    
    if t is None:
        return jsonify({"message":"Task not found"}),404

    # To validate whether title is a string
    if "title" in new_data and not isinstance(new_data["title"],str):
        return jsonify({"message":"Title must be a string"}),400
        
    # To validate whether title is empty
    if "title" in new_data and not new_data["title"].strip():
        return jsonify({"message":"Title can't be an empty string"}),400
    
    if "title" in new_data:
        t.title=new_data["title"]

    # To validate whether completed is a boolean
    if "completed" in new_data and not isinstance(new_data["completed"], bool):
        return jsonify({"message": "Completed must be a boolean"}), 400

    if "completed" in new_data:
        t.completed=new_data["completed"]

    db.session.commit()

    return jsonify({
        "title":t.title,
        "id":t.id,
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