/* dcpd_js_docker_ps.js */

// ==========================
// Event Listeners
// ==========================

// Show the docker ps content, hide other content, and load the data when clicked
document.getElementById('view-docker-ps').addEventListener('click', function() {
    highlightActiveLink(this);
    document.getElementById('view-docker-ps').classList.add('active');
    showContent('docker-ps-content');
    loadDockerpsData();
});

// Refresh the docker ps data when clicked
document.getElementById('refresh-docker-ps').addEventListener('click', function() {
    loadDockerpsData();
	reHighlightLastActiveLink();
});

document.getElementById('exportDockerps').addEventListener('click', function() {
    exportLog(DATA_PATH + 'dcpd_container_info.csv', 'docker-ps-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================

/**
 * Fetches and displays data from ../data/dcpd_container_info.csv.
 */
function loadDockerpsData() {
	console.log('Attempting to load Docker ps data...');
    fetch(DATA_PATH + 'dcpd_container_info.csv')
        .then(response => response.text()) 
        .then(data => {
            const rows = parseCSV(data);
            
			// Sort the rows numerically based on the 'id' field
			rows.sort((a, b) => Number(a.id) - Number(b.id));

            // Poulate the table
			populateDockerpsTable(rows);
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
function populateDockerpsTable(data) {
	console.log('Populating Docker ps table with data:', data);
    const tableBodyDockerps = $("#docker_ps_table tbody");
    // Clear the tbody first
    tableBodyDockerps.empty();
    data.forEach(row => {
        const tr = $("<tr>");
		tr.append($("<td>").text(row["ID"].replace(/"/g, '')));
        tr.append($("<td>").text(row["IMAGE"].replace(/"/g, '')));
        tr.append($("<td>").text(row["COMMAND"].replace(/"/g, '')));
        tr.append($("<td>").text(row["CREATED AT"].replace(/"/g, '')));
        tr.append($("<td>").text(row["STATUS"].replace(/"/g, '')));
        tr.append($("<td>").text(row["NAMES"].replace(/"/g, '')));
        tableBodyDockerps.append(tr);
    });
}