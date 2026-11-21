
// Get the task-list element from HTML
const taskList = document.getElementById("task-list");

// Function to fetch and display all tasks
async function fetchTasks() {

    // Send GET request to Flask API
    const response = await fetch("/tasks");

    // Convert the response into JSON
    const data = await response.json();

    // Clear existing tasks before displaying updated tasks
    taskList.innerHTML = "";

    // Loop through all tasks received from the API
    data.tasks.forEach(task => {

        // Create a new div for each task
        const taskItem = document.createElement("div");

        // Create a checkbox
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";

        // Set checkbox status based on task.completed
        checkbox.checked = task.completed;

        // Update task status when checkbox is clicked
        checkbox.addEventListener("change", async function() {

            const response = await fetch(`/tasks/${task.id}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    completed: checkbox.checked
                })
            });

            if (response.ok) {
                fetchTasks();
            }
        });

        // Create a span for the task title
        const taskTitle = document.createElement("span");
        taskTitle.textContent = task.title;

        // Add checkbox and title to the task div
        taskItem.appendChild(checkbox);
        taskItem.appendChild(taskTitle);

        // Create a Delete button
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";

        // Delete the task when the button is clicked
        deleteBtn.addEventListener("click", async function() {

            const response = await fetch(`/tasks/${task.id}`, {
                method: "DELETE"
            });

            if (response.ok) {
                fetchTasks();
            }
        });

        // Add the Delete button to the task div
        taskItem.appendChild(deleteBtn);

        // Add the task div to the task-list section
        taskList.appendChild(taskItem);
    });
}


// Get the Add Task button
const addTaskBtn = document.getElementById("add-task-btn");

// Get the task input field
const taskTitleInput = document.getElementById("task-title");



// When the Add Task button is clicked
addTaskBtn.addEventListener("click", async function() {

    // Get the task title entered by the user
    const title = taskTitleInput.value.trim();

    // Check if the input is empty
    if (!title) {
        alert("Please enter a task");
        return;
    }

    // Send POST request to Flask API
    const response = await fetch("/tasks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title
        })
    });

    // If the task is successfully created
    if (response.ok) {
        taskTitleInput.value = "";
        fetchTasks();
    }
});


fetchTasks();