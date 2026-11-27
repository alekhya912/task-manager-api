
def test_get_tasks(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json["tasks"] == []
    assert response.json["page"] == 1
    assert response.json["total_tasks"] == 0


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Learn pytest"}
    )

    assert response.status_code == 201
    assert response.json["title"] == "Learn pytest"


def test_get_task_by_id(client):
    # First, create a task
    create_response = client.post(
        "/tasks",
        json={"title": "Learn Flask"}
    )

    # Get the ID of the created task
    task_id = create_response.json["id"]

    # Request that task using its ID
    response = client.get(f"/tasks/{task_id}")

    # Check the response
    assert response.status_code == 200
    assert response.json["title"] == "Learn Flask"



def test_update_task(client):
    # First, create a task
    create_response = client.post(
        "/tasks",
        json={"title": "Learn Flask"}
    )

    task_id = create_response.json["id"]

    # Update the task
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Learn Flask and pytest",
            "completed": True
        }
    )

    # Check the response
    assert response.status_code == 200
    assert response.json["title"] == "Learn Flask and pytest"
    assert response.json["completed"] == True


def test_patch_task(client):
    # Create a task
    create_response = client.post(
        "/tasks",
        json={"title": "Learn Python"}
    )

    task_id = create_response.json["id"]

    # Update only the completed field
    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True}
    )

    # Check the response
    assert response.status_code == 200
    assert response.json["title"] == "Learn Python"
    assert response.json["completed"] == True


def test_delete_task(client):
    # First, create a task
    create_response = client.post(
        "/tasks",
        json={"title": "Learn Python"}
    )

    task_id = create_response.json["id"]

    # Delete the task
    response = client.delete(f"/tasks/{task_id}")

    # Check whether deletion was successful
    assert response.status_code == 200

    # Try retrieving the deleted task
    get_response = client.get(f"/tasks/{task_id}")

    # Check whether it no longer exists
    assert get_response.status_code == 404


def test_create_task_without_title(client):
    response = client.post(
        "/tasks",
        json={}
    )

    assert response.status_code == 400


def test_patch_task_invalid_completed(client):
    # Create a task
    create_response = client.post(
        "/tasks",
        json={"title": "Learn Python"}
    )

    task_id = create_response.json["id"]

    # Send invalid data
    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": "hello"}
    )

    # Check whether the API rejects it
    assert response.status_code == 400


def test_get_nonexistent_task(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404


def test_filter_completed_tasks(client):
    # Create first task
    task1 = client.post(
        "/tasks",
        json={"title": "Learn Python"}
    )

    # Create second task
    task2 = client.post(
        "/tasks",
        json={"title": "Learn Flask"}
    )

    # Mark the first task as completed
    task_id = task1.json["id"]

    client.patch(
        f"/tasks/{task_id}",
        json={"completed": True}
    )

    # Get only completed tasks
    response = client.get("/tasks?completed=true")

    # Check the response
    assert response.status_code == 200
    assert len(response.json["tasks"]) == 1
    assert response.json["tasks"][0]["title"] == "Learn Python"



def test_sort_tasks_ascending(client):
    # Create three tasks
    client.post("/tasks", json={"title": "Python"})
    client.post("/tasks", json={"title": "Django"})
    client.post("/tasks", json={"title": "Flask"})

    # Request tasks in ascending order
    response = client.get("/tasks?sort=asc")

    # Check the response
    assert response.status_code == 200

    titles = [
        task["title"]
        for task in response.json["tasks"]
    ]

    assert titles == ["Python", "Django", "Flask"]


def test_sort_tasks_descending(client):
    # Create three tasks
    client.post("/tasks", json={"title": "Python"})
    client.post("/tasks", json={"title": "Django"})
    client.post("/tasks", json={"title": "Flask"})

    # Request tasks in descending order
    response = client.get("/tasks?sort=desc")

    assert response.status_code == 200

    titles = [
        task["title"]
        for task in response.json["tasks"]
    ]

    assert titles == ["Flask", "Django", "Python"]


def test_task_pagination(client):
    # Create 7 tasks
    for i in range(7):
        client.post(
            "/tasks",
            json={"title": f"Task {i + 1}"}
        )

    # Request the first page
    response = client.get("/tasks?page=1&per_page=5")

    assert response.status_code == 200
    assert len(response.json["tasks"]) == 5
    assert response.json["page"] == 1
    assert response.json["total_pages"] == 2

    # Request the second page
    response = client.get("/tasks?page=2&per_page=5")

    assert response.status_code == 200
    assert len(response.json["tasks"]) == 2
    assert response.json["page"] == 2


def test_invalid_page_number(client):
    # Create 3 tasks
    for i in range(3):
        client.post(
            "/tasks",
            json={"title": f"Task {i + 1}"}
        )

    # Request a page that doesn't exist
    response = client.get("/tasks?page=5&per_page=5")

    assert response.status_code == 400


def test_invalid_sort_parameter(client):
    response = client.get("/tasks?sort=random")

    assert response.status_code == 400

def test_invalid_completed_filter(client):
    response = client.get("/tasks?completed=yes")

    assert response.status_code == 400

def test_invalid_page_value(client):
    response = client.get("/tasks?page=abc")

    assert response.status_code == 400

def test_invalid_per_page(client):
    response = client.get("/tasks?per_page=0")

    assert response.status_code == 400

def test_query_parameters(client):
    response = client.get("/tasks?hello=hi")

    assert response.status_code == 400

def test_not_found_endpoint(client):
    response = client.get("/unknown")

    assert response.status_code == 404

def test_invalid_method(client):
    response = client.put("/")

    assert response.status_code == 405