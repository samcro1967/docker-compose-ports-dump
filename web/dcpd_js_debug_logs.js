/* dcpd_js_debug_logs.js */

// ==========================
// Event Listeners
// ==========================

// When clicked, it will show the Debug Log content and load/display the debug log
document.getElementById('view-debug-log').addEventListener('click', function(e) {
    highlightActiveLink(this);
    showContent('debug-log-content');
    loadLog('../config/logs/dcpd_log_debug.log', 'debug-log-area');
});

// When clicked, it will reload and display the debug log
document.getElementById('refresh-debug-log').addEventListener('click', function() {
    loadLog('../config/logs/dcpd_log_debug.log', 'debug-log-area');
	reHighlightLastActiveLink();
});

// When clicked, it will export the debug log
document.getElementById('exportDebugLog').addEventListener('click', function() {
    exportLog('../config/logs/dcpd_log_debug.log', 'debug-log-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
