document.addEventListener("DOMContentLoaded", function () {
    // Get flash messages from Flask
    const flashMessages = JSON.parse(document.getElementById('flash-messages').textContent);

    // If there are any flash messages
    if (flashMessages.length > 0) {
        // Loop through each message and display it in a custom alert box
        flashMessages.forEach(function ([category, message]) {
            showAlert(message, category);
        });
    }
});

function showAlert(message, category) {
    // Create the alert box element
    const alertBox = document.createElement('div');
    alertBox.className = `custom-alert ${category}`;
    alertBox.innerHTML = `
        <h3>${category.charAt(0).toUpperCase() + category.slice(1)}</h3>
        <p>${message}</p>
        <button class="close-btn" onclick="this.parentElement.remove()">Close</button>
    `;
    document.body.appendChild(alertBox);
}
