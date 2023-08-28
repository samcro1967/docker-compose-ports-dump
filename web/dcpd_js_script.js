/* dcpd_script.js */

/**
 * This script provides various functionalities:
 * 1. Search functionality for filtering table rows based on user input.
 * 2. CSV Export functionality to allow users to download the table's visible rows as a CSV file.
 * 3. Content Display functionality to toggle between different sections of content.
 * 4. Log Fetch functionality to fetch and display logs.
 * 5. Table Initialization to fetch CSV data and populate the table on page load.
 */

// =========================
// DOM Initialization
// =========================
$(document).ready(function () {
    // Fetch CSV data and populate the table
	fetchAndPopulateTable();

    // Call the function to load and apply the styles
    loadWebpageStyles();

    // Show current date and time
    showDateTime();

    // Update footer with data from dcpd_html.json
    updateFooter();

    // Update location and temperature from dcpd_html.json
    updateLocationAndTemperature();

    // On document ready, show the ports content by default.
    showContent('ports-content');

    // Check for updates
    checkForUpdate();

});
