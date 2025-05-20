import unittest
import json
from app.app import app, tasks


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        tasks.clear()

    def test_hello(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Hello, security world!"})

    def test_health(self):
        response = self.app.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("status" in response.json)
        self.assertEqual(response.json["status"], "healthy")
        self.assertTrue("timestamp" in response.json)

    def test_get_tasks_empty(self):
        response = self.app.get("/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"tasks": []})

    def test_create_task(self):
        task_data = {"title": "Test Task", "description": "This is a test task"}
        response = self.app.post(
            "/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue("id" in response.json)
        self.assertEqual(response.json["title"], "Test Task")
        self.assertEqual(response.json["description"], "This is a test task")
        self.assertFalse(response.json["completed"])

    def test_create_task_missing_title(self):
        task_data = {"description": "Missing title"}
        response = self.app.post(
            "/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("error" in response.json)

    def test_get_single_task(self):
        task_data = {"title": "Get Single Task Test"}
        response = self.app.post(
            "/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        task_id = response.json["id"]

        response = self.app.get(f"/tasks/{task_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], task_id)
        self.assertEqual(response.json["title"], "Get Single Task Test")

    def test_get_nonexistent_task(self):
        response = self.app.get("/tasks/nonexistent-id")
        self.assertEqual(response.status_code, 404)

    def test_update_task(self):
        task_data = {"title": "Original Title"}
        response = self.app.post(
            "/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        task_id = response.json["id"]

        update_data = {"title": "Updated Title", "completed": True}
        response = self.app.put(
            f"/tasks/{task_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["title"], "Updated Title")
        self.assertTrue(response.json["completed"])

    def test_delete_task(self):
        task_data = {"title": "Task to Delete"}
        response = self.app.post(
            "/tasks", data=json.dumps(task_data), content_type="application/json"
        )
        task_id = response.json["id"]

        response = self.app.delete(f"/tasks/{task_id}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("message" in response.json)

        response = self.app.get(f"/tasks/{task_id}")
        self.assertEqual(response.status_code, 404)

    def test_stats(self):
        self.app.post(
            "/tasks",
            data=json.dumps({"title": "Task 1"}),
            content_type="application/json",
        )

        task2_response = self.app.post(
            "/tasks",
            data=json.dumps({"title": "Task 2"}),
            content_type="application/json",
        )
        task2_id = task2_response.json["id"]

        self.app.put(
            f"/tasks/{task2_id}",
            data=json.dumps({"completed": True}),
            content_type="application/json",
        )

        response = self.app.get("/stats")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total_tasks"], 2)
        self.assertEqual(response.json["completed_tasks"], 1)
        self.assertEqual(response.json["completion_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
