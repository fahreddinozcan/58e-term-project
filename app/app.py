import uuid
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = {}


@app.route("/")
def hello():
    return jsonify({"message": "Hello, security world!"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": list(tasks.values())})


@app.route("/tasks", methods=["POST"])
def create_task():
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
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
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
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404

    deleted_task = tasks.pop(task_id)
    return jsonify({"message": "Task deleted", "task": deleted_task})


@app.route("/stats")
def get_stats():
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
