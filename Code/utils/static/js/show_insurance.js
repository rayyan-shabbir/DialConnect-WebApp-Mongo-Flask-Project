// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Define the goHome function
    function goHomeUser() {
        // Redirect to the user_table page
        window.location.href = '/user_table';  // Adjust the URL to your homepage if needed
    }

    // Expose the goHome function globally
    window.goHomeUser = goHomeUser;

    // Define the goHome function
    function goHomeAdmin() {
        // Redirect to the user_table page
        window.location.href = '/admin_table';  // Adjust the URL to your homepage if needed
    }

    // Expose the goHome function globally
    window.goHomeAdmin = goHomeAdmin;
});
