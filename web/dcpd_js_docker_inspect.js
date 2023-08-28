/* dcpd_js_docker_inspect.js */

// ==========================
// Event Listeners
// ==========================

// Show the docker inspect content, hide other content, and load the data when clicked
document.getElementById('view-docker-inspect').addEventListener('click', function() {
    highlightActiveLink(this);
    showContent('docker-inspect-content');
    loadDockerInspectData();
});

// Refresh the docker inspect data when clicked
document.getElementById('refresh-docker-inspect').addEventListener('click', function() {
    loadDockerInspectData();
	reHighlightLastActiveLink();
});

// Export the docker inspect data when clicked
document.getElementById('exportDockerInspect').addEventListener('click', function() {
    exportLog(DATA_PATH + 'dcpd_container_ports.csv', 'docker-inspect-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================

/**
 * Fetches and displays data from ../data/dcpd_container_ports.csv.
 */
function loadDockerInspectData() {
	console.log('Attempting to load Docker Inspect data...');
    fetch(DATA_PATH + 'dcpd_container_ports.csv')
        .then(response => response.text()) 
        .then(data => {
            const rows = parseCSV(data);
            
			// Sort the rows numerically based on the 'id' field
			rows.sort((a, b) => Number(a.id) - Number(b.id));

            // Poulate the table
			populateDockerInspectTable(rows);
        })
        .catch(error => {
            console.error('Error fetching host networking data:', error);
        });
}

/**
 * Function to populate the host networking table with given data.
 *
 * @param {Array} data - An array of objects to populate the table.
 */
function populateDockerInspectTable(data) {
	console.log('Populating Docker Inspect table with data:', data);
    const tableBodyDockerInspect = $("#docker_inspect_table tbody");
    // Clear the tbody first
    tableBodyDockerInspect.empty();
    data.forEach(row => {
        const tr = $("<tr>");
        tr.append($("<td>").text(row["id"].replace(/"/g, '')));
        tr.append($("<td>").text(row["container_name"].replace(/"/g, '')));
        tr.append($("<td>").text(row["internal_port"].replace(/"/g, '')));
        tr.append($("<td>").text(row["external_port"].replace(/"/g, '')));
        tr.append($("<td>").text(row["mapping_name"].replace(/"/g, '')));
        tr.append($("<td>").text(row["mapping_value"].replace(/"/g, '')));
        tr.append($("<td>").text(row["protocol"].replace(/"/g, '')));
        tableBodyDockerInspect.append(tr);
    });
}