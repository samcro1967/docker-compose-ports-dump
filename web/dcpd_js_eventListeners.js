/* dcpd_js_eventListeners.js */

// ==========================
// Event Listeners
// ==========================

document.addEventListener('DOMContentLoaded', function() {
    // Using the body as the parent and delegate the event to the ".search" input field
    document.body.addEventListener('input', function(e) {
        if (e.target.matches('.search')) {
            const searchText = e.target.value;

            // If the search input is empty, display all rows in the "#ports_table"
            if (searchText === "") {
                document.querySelectorAll("#ports_table tbody tr").forEach(row => row.style.display = '');
            } else {
                // Hide the placeholder row if any input is present
                const placeholderRow = document.querySelector(".placeholder-row");
                if (placeholderRow) placeholderRow.style.display = 'none';

                // Check each row in the table to determine if it matches the search input
                document.querySelectorAll("#ports_table tbody tr").forEach(row => {
                    if (row.textContent.toLowerCase().includes(searchText.toLowerCase())) {
                        row.style.display = ''; // Display rows that match
                    } else {
                        row.style.display = 'none'; // Hide rows that do not match
                    }
                });
            }
        }
    });
});


// Add an event listener for the 'exportCSV' button
document.getElementById('exportCSV').addEventListener('click', function() {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += ["Service Name", "External Port", "Internal Port", "Port Mapping", "Mapped App"].join(",") + "\n";

    // For each visible row in the table, extract its data and add it to the CSV content
    document.querySelectorAll("#ports_table tbody tr").forEach(row => {
        if (getComputedStyle(row).display !== 'none') {
            const rowData = Array.from(row.querySelectorAll('td')).map(td => td.textContent);
            csvContent += rowData.join(",") + "\n";
        }
    });

    // Convert the CSV content into a downloadable link and initiate the download process
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "../data/dcpd.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// Add an event listener for the 'view-ports' button to display the ports content
document.getElementById('view-ports').addEventListener('click', function() {
    highlightActiveLink(this);
	showContent('ports-content');
});

// Add an event listener for the 'exportRedactedSupportFile' button to initiate the export process
document.getElementById('exportRedactedSupportFile').addEventListener('click', function() {
    exportRedactedSupportFile();
});