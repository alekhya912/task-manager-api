// Get the task-list element from HTML
const taskList = document.getElementById("task-list");
const filterTasks = document.getElementById("filter-tasks");
const sortTasks = document.getElementById("sort-tasks");
let currentPage = 1;
const perPage = 5;

const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const pageInfo = document.getElementById("page-info");

// Function to fetch and display all tasks
async function fetchTasks() {

    const filterValue = filterTasks.value;
    const sortValue = sortTasks.value;

    let url = `/tasks?page=${currentPage}&per_page=${perPage}&sort=${sortValue}`;

    if (filterValue !== "all") {
        url += `&completed=${filterValue}`;
    }  

    const response = await fetch(url);

    // Check whether the API request was successful
    if (!response.ok) {
        taskList.textContent = "Unable to load tasks. Please try again.";
        return;
    }

    // Convert the response into JSON
    const data = await response.json();

    // Update the current page information
    pageInfo.textContent = `Page ${data.page} of ${data.total_pages}`;

    // Disable Previous button on the first page
    prevBtn.disabled = data.page === 1;

    // Disable Next button on the last page
    nextBtn.disabled = data.page >= data.total_pages;

    // Clear existing tasks before displaying updated tasks
    taskList.innerHTML = "";

    // Display a message when there are no tasks
    if (data.tasks.length === 0) {
        taskList.textContent = "No tasks found!";
        pageInfo.textContent = "No tasks";
        return;
    }

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

        // Create an Edit button
        const editBtn = document.createElement("button");
        editBtn.textContent = "Edit";
        
        // Edit the task when the button is clicked
        editBtn.addEventListener("click", async function() {

            // Ask the user for the updated task title
            const newTitle = prompt("Enter the updated task title:", task.title);

            if (newTitle === null) {
                return;
            }

            if (!newTitle.trim()) {
                alert("Task title cannot be empty!");
                return;
            }

            // Send PUT request to Flask API
            const response = await fetch(`/tasks/${task.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: newTitle.trim(),
                    completed: task.completed
                })
            });

            // Refresh tasks after successful update
            if (response.ok) {
                fetchTasks();
            }
        });
        

        // Create a Delete button
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";

        // Delete the task when the button is clicked
        deleteBtn.addEventListener("click", async function() {

            if (!confirm("Are you sure you want to delete this task?")) {
                return;
            }

            const response = await fetch(`/tasks/${task.id}`, {
                method: "DELETE"
            });

            if (response.ok) {

            // If this was the last task on the current page,
            // move back to the previous page
            if (data.tasks.length === 1 && currentPage > 1) {
                currentPage--;
            }

            fetchTasks();
        }
        });


        // Add the Edit button to the task div
        taskItem.appendChild(editBtn);

        // Add the Delete button to the task div
        taskItem.appendChild(deleteBtn);

    
        // Add the task div to the task-list section
        taskList.appendChild(taskItem);
    });
}

filterTasks.addEventListener("change", function() {
    currentPage = 1;
    fetchTasks();
});

sortTasks.addEventListener("change", function() {
    currentPage = 1;
    fetchTasks();
});

// Get the Add Task button
const addTaskBtn = document.getElementById("add-task-btn");

// Get the task input field
const taskTitleInput = document.getElementById("task-title");

// Go to the previous page
prevBtn.addEventListener("click", function() {
    if (currentPage > 1) {
        currentPage--;
        fetchTasks();
    }
});

// Go to the next page
nextBtn.addEventListener("click", function() {
    currentPage++;
    fetchTasks();
});



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
        currentPage=1;
        fetchTasks();
    }
    else {
        const data = await response.json();
        alert(data.message || "Unable to add task. Please try again.");
    }
});

// Add a task when Enter is pressed
taskTitleInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        addTaskBtn.click();
    }
});


fetchTasks();