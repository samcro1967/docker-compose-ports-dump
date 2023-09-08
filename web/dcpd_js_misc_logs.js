/* dcpd_js_misc_logs.js */

// ==========================
// Event Listeners
// ==========================

// Add an event listener for 'view-misc-log' 
document.getElementById('view-misc-log').addEventListener('click', function(e) {
    highlightActiveLink(this);
    showContent('misc-log-content');
    loadLog(document.getElementById('log-selector').value, 'misc-log-area');
});

// Add an event listener to refresh the log
document.getElementById('refresh-misc-log').addEventListener('click', function(e) {
    loadLog(document.getElementById('log-selector').value, 'misc-log-area');
    reHighlightLastActiveLink();
});

// Add an event listener to export the log
document.getElementById('exportMiscLog').addEventListener('click', function(e) {
    exportLog(document.getElementById('log-selector').value, 'misc-log-area');
    reHighlightLastActiveLink();
});

// Add an event listener to the log dropdown selector
document.getElementById('log-selector').addEventListener('change', function(e) {
    loadLog(this.value, 'misc-log-area');
});

// =========================
// Function Declarations
// =========================
