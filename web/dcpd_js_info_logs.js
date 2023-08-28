/* dcpd_js_debug_info.js */

// ==========================
// Event Listeners
// ==========================

// Add an event listener to the element with ID 'view-info-log'
document.getElementById('view-info-log').addEventListener('click', function(e) {
    highlightActiveLink(this);
	showContent('info-log-content');
	loadLog('../config/logs/dcpd_log_info.log', 'info-log-area');
});

// Add an event listener to the element with ID 'refresh-info-log'
document.getElementById('refresh-info-log').addEventListener('click', function(e) {
	loadLog('../config/logs/dcpd_log_info.log', 'info-log-area');
	reHighlightLastActiveLink();
});

// Add an event listener to the element with ID 'exportInfoLog'
document.getElementById('exportInfoLog').addEventListener('click', function(e) {
	exportLog('../config/logs/dcpd_log_info.log', 'info-log-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
