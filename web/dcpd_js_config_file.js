/* dcpd_js_config_file.js */

// ==========================
// Event Listeners
// ==========================

// When clicked, it will show the Config File content, hide other content, and load/display the config file
document.getElementById('view-config-file').addEventListener('click', function(e) {
    highlightActiveLink(this);
    showContent('config-file-content');
    loadLog('../config/dcpd_config.py', 'config-file-area');
});

// When clicked, it will reload and display the config file
document.getElementById('refresh-config-file').addEventListener('click', function(e) {
    loadLog('dcpd_config.py', 'config-file-area');
	reHighlightLastActiveLink();
});

// When clicked, it will export the config file
document.getElementById('exportConfigFile').addEventListener('click', function(e) {
    exportLog('../config/dcpd_config.py', 'config-file-area');
	reHighlightLastActiveLink();
});

// =========================
// Function Declarations
// =========================
