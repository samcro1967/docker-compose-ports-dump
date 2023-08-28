/* dcpd_js_update_footer.js */

// ==========================
// Event Listeners
// ==========================



// =========================
// Function Declarations
// =========================

/**
 * Fetches footer data from a JSON file and updates the corresponding elements.
 * 
 * This function fetches footer data from a JSON file named 'dcpd_html.json' and updates
 * the content of specific HTML elements to display the retrieved information. It utilizes
 * the Fetch API to retrieve JSON data asynchronously.
 */
function updateFooter() {
    // Fetch the JSON data from 'dcpd_html.json' file
    fetch(DATA_PATH + 'dcpd_html.json')
        .then(response => response.json())  // Extract the response as JSON
        .then(data => {
            // Update the HTML elements with the retrieved footer data
            document.getElementById('current-file-name').textContent = data.html_file_name;
            document.getElementById('file-update-time').textContent = data.last_updated;
        })
        .catch(error => {
            // Handle errors by logging an error message
            console.error('Error fetching data:', error);
        });
}