/* dcpd_js_container_logs.js */

// ==========================
// Event Listeners
// ==========================

// New event listener for 'view-container-logs'
document.getElementById('view-container-logs').addEventListener('click', function(e) {
    highlightActiveLink(this);
    showContent('container-logs-content');
    fetchContainerLogs();
});

// =========================
// Function Declarations
// =========================
function fetchContainerLogs() {
    // Derive the current host based on the window's location properties
    const currentHost = window.CONFIG.API_BASE_URL;

    // Construct the API logs endpoint using the current host
    const logsEndpoint = currentHost + '/api/proxy/logs';

    // Make an AJAX call to the constructed endpoint
    $.ajax({
        url: logsEndpoint,
        type: 'GET',
        success: function(response) {
            // Assuming the returned data structure is {logs: '...logs here...'}
            // Clear any existing content and insert the new logs into the #container-logs-content div
            $('#container-logs-content').html('<div class="sticky-header"><h1>Container Logs</h1></div><pre>' + response.logs + '</pre>');
            
            // Display the logs section
            $('#container-logs-content').show();
        },
        error: function(error) {
            console.error('Failed to fetch logs:', error);
            $('#container-logs-content').append('<p>Error fetching logs.</p>').show();
        }
    });
}
