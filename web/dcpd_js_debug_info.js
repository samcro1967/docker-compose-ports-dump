/* dcpd_js_debug_info.js */

// ==========================
// Event Listeners
// ==========================

// Add an event listener to the element with ID 'view-debug-info'
// When clicked, it will show the Debug Info content, hide other content, and load/display the debug info
document.getElementById('view-debug-info').addEventListener('click', function(e) {
    e.preventDefault();
    highlightActiveLink(this);

    showContent('debug-info-content');
    loadLog(DATA_PATH + 'dcpd_debug.txt', 'debug-info-area');
});

// When clicked, it will reload and display the debug info
document.getElementById('refresh-debug-info').addEventListener('click', function(e) {
    loadLog(DATA_PATH + 'dcpd_debug.txt', 'debug-info-area');
	reHighlightLastActiveLink();
});

// Add an event listener to the element with ID 'exportDebugInfo'
// When clicked, it will export the debug info
document.getElementById('exportDebugInfo').addEventListener('click', function(e) {
    exportLog(DATA_PATH + 'dcpd_debug.txt', 'debug-info-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
