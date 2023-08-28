/* dcpd_script.js */

/**
 * dcpd_script.js
 * 
 * The primary script that orchestrates the overall functionalities of the page.
 * 
 * Features:
 * - Initializes content when the DOM is ready.
 * - Populates tables with CSV data.
 * - Handles styling and presentation based on dynamic data.
 * - Provides utilities to display current date-time, update the footer, 
 *   and check for application updates.
 */

// =========================
// DOM Initialization
// =========================

$(document).ready(function () {
    // By default, highlight the "Docker Compose Ports" link
    const dockerComposeLink = $('#view-ports');
    if (dockerComposeLink.length) {
        highlightActiveLink(dockerComposeLink[0]);
    }

    /**
     * Fetches data from a CSV file and populates the table on the web page.
     */
	fetchAndPopulateTable();

    /**
     * Load and apply the styling properties for the web page.
     * The styles are defined in dcpd_html.json and are applied as CSS Custom Properties.
     */
    loadWebpageStyles();

    /**
     * Display the current date and time on the web page.
     */
    showDateTime();

    /**
     * Update the footer section of the web page.
     * The data is fetched from dcpd_html.json.
     */
    updateFooter();

    /**
     * Display the location and temperature data on the web page.
     * The data is fetched from dcpd_html.json.
     */
    updateLocationAndTemperature();

    /**
     * By default, when the page loads, the content section that displays port details is shown.
     */
    showContent('ports-content');

    /**
     * Checks if there are any updates available for the application.
     */
    checkForUpdate();

});