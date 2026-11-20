
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

        // Add task title inside the div
        taskItem.textContent = task.title;

        // Add the task div to the task-list section
        taskList.appendChild(taskItem);
    });
}

// Call the function when the page loads
fetchTasks();
