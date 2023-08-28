/* dcpd_js_stats_file.js */

// ==========================
// Event Listeners
// ==========================

// Add an event listener to the element with ID 'view-stats-file'
document.getElementById('view-stats-file').addEventListener('click', function(e) {
    highlightActiveLink(this);
	showContent('stats-file-content');
	loadLog('../data/dcpd_stats.txt', 'stats-file-area');
});

// Add an event listener to the element with ID 'refresh-stats-file'
document.getElementById('refresh-stats-file').addEventListener('click', function(e) {
	loadLog('../data/dcpd_stats.txt', 'stats-file-area');
	reHighlightLastActiveLink();
});

// Add an event listener to the element with ID 'exportStatsFile'
document.getElementById('exportStatsFile').addEventListener('click', function(e) {
	exportLog('../data/dcpd_stats.txt', 'stats-file-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
