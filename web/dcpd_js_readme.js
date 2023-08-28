/* dcpd_js_readme.js */

// ==========================
// Event Listeners
// ==========================

// Add an event listener to the element with ID 'view-readme'
// When clicked, it will show the README content and then load and display the content of the README.md file
document.getElementById('view-readme').addEventListener('click', function() {
    // Highlight the 'view-readme' link and remove 'active' from others
    highlightActiveLink(document.getElementById('view-readme'));

    showContent('readme-content');
    loadLog('../README.md', 'readme-area');
});

// =========================
// Function Declarations
// =========================
