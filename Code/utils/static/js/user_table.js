function showMessage(message) {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.style.display = 'block';

    // Hide the message after 3 seconds
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 3000);
}

function confirmDelete(deleteUrl) {
    const confirmation = confirm("Are you sure you want to delete this record?");
    if (confirmation) {
        fetch(deleteUrl, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    showMessage("Record deleted successfully!!");
                    // Reload the page or handle the UI update as needed
                    location.reload();
                } else {
                    showMessage("Failed to delete the record.");
                }
            })
            .catch(() => showMessage("Failed to delete the record."));
    }
}

// Search functionality
document.getElementById('search').addEventListener('input', function () {
    const query = this.value.toLowerCase();
    const rows = document.querySelectorAll('#insuranceTableBody tr');
    rows.forEach(row => {
        const insuranceName = row.cells[1].textContent.toLowerCase();
        row.style.display = insuranceName.includes(query) ? '' : 'none';
    });
});

// Auto-hide flash message after 3 seconds
document.addEventListener("DOMContentLoaded", function () {
    const flashMessage = document.getElementById('flashMessage');
    if (flashMessage) {
        setTimeout(() => {
            flashMessage.style.display = 'none';
        }, 3000);
    }
});