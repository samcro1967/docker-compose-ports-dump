/* dcpd_js_host.networking.js */

// ==========================
// Event Listeners
// ==========================

// When clicked, it will show the Host Networking content and load/display the data
document.getElementById('view-host-networking').addEventListener('click', function(e) {
    highlightActiveLink(this);
    showContent('host-networking-content');
    loadHostNetworkingData();  // Load and display the host networking data
});

// When clicked, it will reload and display the host networking data
document.getElementById('refresh-host-networking').addEventListener('click', function() {
    loadHostNetworkingData();
	reHighlightLastActiveLink();
});

// When clicked, it will export the host networking data
document.getElementById('exportHostNetworking').addEventListener('click', function() {
    exportLog(DATA_PATH + 'dcpd_host_networking.csv', 'host-networking-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
/**
 * Fetches and displays data from ../data/dcpd_host_networking.csv.
 */
function loadHostNetworkingData() {
    fetch(DATA_PATH + 'dcpd_host_networking.csv')
        .then(response => response.text()) 
        .then(data => {
            const rows = parseCSV(data);
            
			// Sort the rows numerically based on the 'id' field
			rows.sort((a, b) => Number(a.id) - Number(b.id));

            // Use the "populateTable" function or a similar function tailored for the host networking table
			populateHostNetworkingTable(rows);
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
function populateHostNetworkingTable(data) {
    const tableBody = $("#host_networking_table tbody");
    // Clear the tbody first
    tableBody.empty();
    data.forEach(row => {
        const tr = $("<tr>");
        tr.append($("<td>").text(row["id"].replace(/"/g, '')));
        tr.append($("<td>").text(row["service_name"].replace(/"/g, '')));
        tableBody.append(tr);
    });
}