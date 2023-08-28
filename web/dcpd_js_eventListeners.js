/* dcpd_js_eventListeners.js */

// ==========================
// Event Listeners
// ==========================

$(".search").on("input", function () {
    var searchText = $(this).val();
    if (searchText === "") {
        // If search text is empty, show all table rows
        $("#ports_table tbody tr").show();
    } else {
        $(".placeholder-row").hide();  // Hiding any placeholder rows
        // Filtering and displaying table rows based on search text
        $("#ports_table tbody tr").filter(function () {
            return $(this).text().toLowerCase().indexOf(searchText.toLowerCase()) === -1;
        }).hide();
        $("#ports_table tbody tr").filter(function () {
            return $(this).text().toLowerCase().indexOf(searchText.toLowerCase()) !== -1;
        }).show();
    }
});

// Show the Host Networking content and load the data
$('#view-host-networking').on('click', function(e){
    e.preventDefault();
    showContent('host-networking-content');

	// Load the host networking data and display it in the table
    loadHostNetworkingData();
});

document.getElementById('refresh-host-networking').addEventListener('click', function() {
    // Reload and display the host networking
    loadHostNetworkingData();
});

// Event listener for the CSV export button
$('#exportCSV').click(function() {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += ["Service Name", "External Port", "Internal Port", "Port Mapping", "Mapped App"].join(",") + "\n";
    
    // Loop through visible table rows and build CSV content
    $("#ports_table tbody tr:visible").each(function() {
        let row = [];
        $(this).find('td').each(function() {
            row.push($(this).text());
        });
        csvContent += row.join(",") + "\n";
    });

    // Creating a downloadable link for the CSV content
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "../data/dcpd.csv");
    document.body.appendChild(link);
    link.click();  // Triggering a click event to initiate the download
    document.body.removeChild(link);  // Removing the temporary link
});


document.getElementById('view-ports').addEventListener('click', function() {
    // Show the Ports content and hide others
    showContent('ports-content');
});

document.getElementById('view-info-log').addEventListener('click', function() {
    // Show the Info Log content, load and display the info log
    showContent('info-log-content');
    loadLog('../config/logs/dcpd_log_info.log', 'info-log-area');
});

document.getElementById('view-debug-log').addEventListener('click', function() {
    // Show the Debug Log content, load and display the debug log
    showContent('debug-log-content');
    loadLog('../config/logs/dcpd_log_debug.log', 'debug-log-area');
});

// Event listeners for refreshing log content
document.getElementById('refresh-info-log').addEventListener('click', function() {
    // Reload and display the info log
    loadLog('../config/logs/dcpd_log_info.log', 'info-log-area');
});

document.getElementById('refresh-debug-log').addEventListener('click', function() {
    // Reload and display the debug log
    loadLog('../config/logs/dcpd_log_debug.log', 'debug-log-area');
});

document.getElementById('view-debug-info').addEventListener('click', function() {
    // Show the Debug Info content and hide others
    showContent('debug-info-content');
    
    // Load and display the debug info from the file using the DATA_PATH constant
    loadLog(DATA_PATH + 'dcpd_debug.txt', 'debug-info-area');
});

document.getElementById('view-config-file').addEventListener('click', function() {
    // Show the Debug Info content and hide others
    showContent('config-file-content');
    
    // Load and display the debug info from the file using the DATA_PATH constant
    loadLog('../config/dcpd_config.py', 'config-file-area');
});

document.getElementById('view-stats-file').addEventListener('click', function() {
    // Show the Stats content and hide others
    showContent('stats-file-content');
    
    // Load and display the debug info from the file using the DATA_PATH constant
    loadLog('../data/dcpd_stats.txt', 'stats-file-area');
});

document.getElementById('refresh-debug-info').addEventListener('click', function() {
    // Reload and display the config file
    loadLog(DATA_PATH + 'dcpd_debug.txt', 'debug-info-area');
});

document.getElementById('refresh-config-file').addEventListener('click', function() {
    // Reload and display the config file
    loadLog('dcpd_config.py', 'config-file-area');
});

document.getElementById('refresh-stats-file').addEventListener('click', function() {
    // Reload and display the config file
    loadLog('../data/dcpd_stats.txt', 'stats-file-area');
});

// Event listeners for the export buttons
$('#exportInfoLog').click(function() {
    exportLog('../config/logs/dcpd_log_info.log', 'info-log-area');
});

$('#exportDebugLog').click(function() {
    exportLog('../config/logs/dcpd_log_debug.log', 'debug-log-area');
});

$('#exportDebugInfo').click(function() {
    exportLog(DATA_PATH + 'dcpd_debug.txt', 'debug-info-area');
});

// Event listener for exporting host networking data
$('#exportHostNetworking').click(function() {
    exportLog(DATA_PATH + 'dcpd_host_networking.csv', 'host-networking-area');
});

// Event listener for exporting config file
$('#exportConfigFile').click(function() {
    exportLog('../config/dcpd_config.py', 'config-file-area');
});

// Event listener for exporting stats file
$('#exportStatsFile').click(function() {
    exportLog('../data/dcpd_stats.txt', 'stats-file-area');
});

// Event listener for exporting redacted support file
$('#exportRedactedSupportFile').click(function() {
    exportRedactedSupportFile();
});

// Event listener for viewing README.md
document.getElementById('view-readme').addEventListener('click', function() {
    // Show the Debug Log content, load and display the debug log
    showContent('readme-content');
    loadLog('../README.md', 'readme-area');
});
 // Event listener for API Docs
document.addEventListener("DOMContentLoaded", function() {
	const currentHost = window.location.protocol + '//' + window.location.hostname + ':8092';
	const apiDocsLink = currentHost + '/apidocs/';
	document.getElementById('view-api-docs').setAttribute('href', apiDocsLink);
});