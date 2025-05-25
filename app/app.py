"""Task Management API for CmpE 58E DevSecOps Pipeline Project.

This module implements a RESTful API for managing tasks with CRUD operations.
It serves as a sample application for demonstrating DevSecOps pipeline security checks.
"""

import uuid
from datetime import datetime
import sqlite3
import os
from flask import Flask, jsonify, request

# BREAK LINTING: Syntax error and bad indentation
# def bad_function():
#     print("This is badly indented")
#   print("This will cause a syntax error due to inconsistent indentation")

# def another_bad_function()
#     print("This is missing a colon")

app = Flask(__name__)

tasks = {}

API_KEY = "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"
DATABASE_PASSWORD = "super_secret_password123!"


@app.route("/")
def hello():
    """Return a greeting message for the root endpoint.

    Returns:
        JSON response with a greeting message
    """
    return jsonify({"message": "Hello, security world!"})


@app.route("/health")
def health():
    """Return the health status of the application.

    Returns:
        JSON response with health status and current timestamp
    """
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Retrieve all tasks.

    Returns:
        JSON response with a list of all tasks
    """
    return jsonify({"tasks": list(tasks.values())})


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task.

    Expects a JSON payload with at least a 'title' field.


    Returns:
        JSON response with the created task data and 201 status code on success,
        or error message with 400 status code if validation fails
    """
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    task_id = str(uuid.uuid4())
    new_task = {
        "id": task_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }
    tasks[task_id] = new_task
    return jsonify(new_task), 201


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    """Retrieve a specific task by ID.

    Args:
        task_id: The unique identifier of the task

    Returns:
        JSON response with task data or 404 error if task not found
    """
    task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task.

    Args:
        task_id: The unique identifier of the task to update

    Returns:
        JSON response with updated task data or appropriate error message
    """
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    task = tasks[task_id]
    if "title" in data:
        task["title"] = data["title"]
    if "description" in data:
        task["description"] = data["description"]
    if "completed" in data:
        task["completed"] = data["completed"]

    task["updated_at"] = datetime.now().isoformat()
    return jsonify(task)


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by ID.

    Args:
        task_id: The unique identifier of the task to delete

    Returns:
        JSON response with deletion confirmation or 404 error if task not found
    """
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404

    deleted_task = tasks.pop(task_id)
    return jsonify({"message": "Task deleted", "task": deleted_task})


@app.route("/stats")
def get_stats():
    """Get statistics about tasks.

    Calculates and returns metrics including total tasks, completed tasks,
    and completion rate.

    Returns:
        JSON response with task statistics
    """
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks.values() if task["completed"])

    return jsonify(
        {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": 0 if total_tasks == 0 else completed_tasks / total_tasks,
            "server_time": datetime.now().isoformat(),
        }
    )


@app.route("/search", methods=["GET"])
def search_tasks():
    """Search for tasks by keyword - VULNERABLE TO SQL INJECTION.

    This function contains a deliberate SQL injection vulnerability
    that should be detected by CodeQL.

    Returns:
        JSON response with matching tasks
    """
    keyword = request.args.get("q", "")
    # SECURITY VULNERABILITY: Direct use of user input in SQL query
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id TEXT, title TEXT, description TEXT)"
    )
    # Populate in-memory DB with our tasks
    for task_id, task in tasks.items():
        cursor.execute(
            "INSERT INTO tasks VALUES (?, ?, ?)",
            (task_id, task["title"], task["description"]),
        )
    # VULNERABLE QUERY - Using string formatting instead of parameterized query
    query = f"SELECT * FROM tasks WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return jsonify({"results": results})


@app.route("/execute", methods=["POST"])
def execute_command():
    """Command injection vulnerability - CodeQL will flag this"""
    data = request.get_json()
    command = data.get("command", "")

    # VULNERABLE: Direct execution of user input
    result = os.system(command)

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
