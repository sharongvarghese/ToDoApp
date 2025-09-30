document.addEventListener("DOMContentLoaded", () => {
  const editButtons = document.querySelectorAll(".edit-btn");
  const editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const editTaskInput = document.getElementById("editTaskInput");
  const editTaskPriority = document.getElementById("editTaskPriority");
  const editForm = document.getElementById("editForm");

  editButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();

      // Get task data from button
      const taskId = btn.getAttribute("data-id");
      const taskText = btn.getAttribute("data-task");
      const taskPriority = btn.getAttribute("data-priority");

      // Pre-fill modal fields
      editTaskInput.value = taskText;
      editTaskPriority.value = taskPriority;

      // Update form action dynamically
      editForm.action = `/edit/${taskId}`;

      // Show modal
      editModal.show();
    });
  });
});

function confirmDelete(taskName) {
    return confirm(`Are you sure you want to delete the task: "${taskName}"?`);
}

// Toggle task completion status
document.querySelectorAll('.toggle-task').forEach(checkbox => {
  checkbox.addEventListener('change', function() {
    const taskId = this.dataset.id;
    fetch(`/toggle/${taskId}`, { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        const label = this.nextElementSibling;
        if(data.completed) {
          label.classList.add('text-success', 'text-decoration-line-through');
        } else {
          label.classList.remove('text-success', 'text-decoration-line-through');
        }
      });
  });
});

