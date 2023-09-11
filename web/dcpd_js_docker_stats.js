/* dcpd_js_docker_stats.js */

// ==========================
// Event Listeners
// ==========================

// Add an event listener to the element with ID 'view-docker-stats'
// When clicked, it displays the Docker Stats content, hides other content, and loads the Docker stats from the specified file
document.getElementById('view-docker-stats').addEventListener('click', function() {
    highlightActiveLink(this);
    showContent('docker-stats-content');
    loadDockerStats('../data/dcpd_docker_stats.txt', 'docker-stats-area');
});

// Add an event listener to the element with ID 'refresh-docker-stats'
// When clicked, it reloads and displays the Docker stats from the specified file
document.getElementById('refresh-docker-stats').addEventListener('click', function() {
    loadDockerStats('../data/dcpd_docker_stats.txt', 'docker-stats-area');
	reHighlightLastActiveLink();
});

// Add an event listener to the element with ID 'exportDockerStats'
// When clicked, it exports the Docker stats to a file
document.getElementById('exportDockerStats').addEventListener('click', function() {
    exportLog('../data/dcpd_docker_stats.txt', 'docker-stats-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
function loadDockerStats(file, containerId) {
    // Fetch file content
    fetch(file).then(response => response.text()).then(data => {
        const lines = data.trim().split('\n');
        let htmlOutput = '<table>';

        // Process each line
        for (let line of lines) {
            // Use regex to split by multiple spaces, but not on single spaces (to prevent breaking 'MEM USAGE / LIMIT', etc.)
            const items = line.split(/\s{2,}/);
            htmlOutput += '<tr>';

            // Process each item
            for (let item of items) {
                htmlOutput += '<td>' + item + '</td>';
            }

            htmlOutput += '</tr>';
        }

        htmlOutput += '</table>';

        document.getElementById(containerId).innerHTML = htmlOutput;
    });
}