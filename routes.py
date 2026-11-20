from flask import Blueprint, jsonify, request
from models import Task
import math
from extensions import db
import logging

logger = logging.getLogger(__name__)

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.filter_by(id=task_id).first()

    if task is None:
        return jsonify({"message": "Task not found"}), 404

    return jsonify({
        "id": task.id,
        "title": task.title,
        "completed": task.completed
    }), 200

# GET API - Retrieve all the tasks by using query parameters
@tasks_bp.route("", methods=["GET"])
def get_tasks():

    # rejecting unsupported query parameters
    allowed_params={"completed","sort","page","per_page"}

    invalid_params=set(request.args.keys())-allowed_params

    if invalid_params:
        return jsonify({
            "message":"Invalid query parameters",
            "invalid parameters":list(invalid_params)
        }),400

    # Query Parameters

    # completed param    
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

    if per_page > 100:
        return jsonify({"message":"Tasks per page to display should not exceed 100"}),400

    if page < 1 or per_page < 1:
        return jsonify({"message": "Page and per_page must be positive integers"}), 400

    total_tasks = query.count()    # Retrieves total count of tasks

    total_pages= math.ceil((total_tasks/per_page))

    if total_pages > 0 and page>total_pages:
        return jsonify({"message":"Enter a valid page number"}),400

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
@tasks_bp.route("", methods=["POST"])
def add_task():

    new_data=request.get_json()

# Input validation in POST

    # To validate whether input is a dictionary and if it is a dict then it is not empty
    if not isinstance(new_data, dict) or not new_data:
            return jsonify({"message": "Request body must be a non-empty JSON object"}), 400

    # To allow only 2 fields i.e. completed and title as valid in input
    allowed_fields = {"title", "completed"}
        
    invalid_fields = set(new_data.keys()) - allowed_fields
        
    if invalid_fields:
        return jsonify({
                "message": "Invalid fields",
                "invalid_fields": list(invalid_fields)
        }), 400

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

    # trying to insert a task into PostgreSQL, but the database operation fails to handle we use try-catch
    try:
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to create task")
        return jsonify({
            "message":"Failed to create task"
        }) , 500

    
    return jsonify({
        "id":new_task.id,
        "title":new_task.title,
        "completed":new_task.completed
    }),201


# PUT API - Update an existing task
@tasks_bp.route("<int:task_id>", methods=["PUT"])  
def update_task(task_id):
    new_data=request.get_json()

# Input validation in PUT

    # To validate whether input is a dictionary and if it is a dict then it is not empty
    if not isinstance(new_data, dict) or not new_data:
        return jsonify({"message": "Request body must be a non-empty JSON object"}), 400

    # To allow only 2 fields i.e. completed and title as valid in input
    allowed_fields = {"title", "completed"}

    invalid_fields = set(new_data.keys()) - allowed_fields

    if invalid_fields:
        return jsonify({
        "message": "Invalid fields",
        "invalid_fields": list(invalid_fields)
    }), 400


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

    
    try:
        t.title=new_data["title"]
        t.completed=new_data["completed"]  
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to update task using PUT")
        return jsonify({
                "message":"Failed to create task"
            }),500
    
    return jsonify({
        "id":t.id,
        "title":t.title,
        "completed":t.completed
    }),200



# PATCH API - Updates selected fields
@tasks_bp.route("<int:task_id>",methods=["PATCH"])
def patch_task(task_id):
    new_data=request.get_json()
    
    # To validate whether input is a dictionary and if it is a dict then it is not empty
    if not isinstance(new_data, dict) or not new_data:
        return jsonify({"message": "Request body must be a non-empty JSON object"}), 400
    
    # To allow only 2 fields i.e. completed and title as valid in input
    allowed_fields = {"title", "completed"}
    
    invalid_fields = set(new_data.keys()) - allowed_fields
    
    if invalid_fields:
        return jsonify({
            "message": "Invalid fields",
            "invalid_fields": list(invalid_fields)
        }), 400

    t=Task.query.filter_by(id=task_id).first()
    
    if t is None:
        return jsonify({"message":"Task not found"}),404

    # To validate whether title is a string
    if "title" in new_data and not isinstance(new_data["title"],str):
        return jsonify({"message":"Title must be a string"}),400
        
    # To validate whether title is empty
    if "title" in new_data and not new_data["title"].strip():
        return jsonify({"message":"Title can't be an empty string"}),400

    # To validate whether completed is a boolean
    if "completed" in new_data and not isinstance(new_data["completed"], bool):
        return jsonify({"message": "Completed must be a boolean"}), 400


    try:
        if "completed" in new_data:
            t.completed=new_data["completed"]
        if "title" in new_data:
            t.title=new_data["title"]
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to update task using PATCH")
        return jsonify({
                "message":"Failed to create task"
            }),500

    return jsonify({
        "title":t.title,
        "id":t.id,
        "completed":t.completed
    }),200


# DELETE API - Delete an existing task
@tasks_bp.route("<int:task_id>",methods=["DELETE"])
def delete_task(task_id):

    t=Task.query.filter_by(id=task_id).first()

    if t is None:
        return jsonify({"message": "Task not found"}),404
    
    try:
        db.session.delete(t)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to DELETE task ")
        return jsonify({
                "message":"Failed to create task"
            }),500

    
    return jsonify({
        "message":"Task deleted successfully!"
    }),200