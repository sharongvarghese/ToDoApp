document.addEventListener("DOMContentLoaded", () => {
  // === Edit Modal ===
  const editButtons = document.querySelectorAll(".edit-btn");
  const editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const editTaskInput = document.getElementById("editTaskInput");
  const editTaskPriority = document.getElementById("editTaskPriority");
  const editForm = document.getElementById("editForm");

  editButtons.forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      const taskId = btn.dataset.id;
      const taskText = btn.dataset.task;
      const taskPriority = btn.dataset.priority;

      editTaskInput.value = taskText;
      editTaskPriority.value = taskPriority;
      editForm.action = `/edit/${taskId}`;
      editModal.show();
    });
  });



  // === Card Delete Confirmation ===
  document.querySelectorAll(".delete-card-form").forEach(form => {
    form.addEventListener("submit", function(e) {
      const cardName = this.dataset.cardName;
      if(!confirm(`Are you sure you want to delete card: "${cardName}"? All tasks inside will also be deleted.`)) {
        e.preventDefault();
      }
    });
  });

  // === Toggle Task Completion ===
  document.querySelectorAll('.toggle-task').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const taskId = this.dataset.id;
      fetch(`/toggle/${taskId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
          const label = this.nextElementSibling;
          if(data.completed) {
            label.classList.add('text-success', 'text-decoration-line-through');
            label.classList.remove('text-light');
          } else {
            label.classList.remove('text-success', 'text-decoration-line-through');
            label.classList.add('text-light');
          }
        });
    });
  });
});
