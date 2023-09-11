/* dcpd_js_links.js */

// ==========================
// Event Listeners
// ==========================

// Add click event listener for the "view-links" link
document.getElementById('view-links').addEventListener('click', function(event) {
    // Prevent the default action of the link (navigation)
    event.preventDefault();

    // Display the "links-content" section and hide others
    showContent('links-content');

    // Highlight the 'view-links' link and remove 'active' from others
    highlightActiveLink(this);

    // Construct the API docs link using the current host
    const apiDocsLink = window.CONFIG.API_BASE_URL + '/apidocs/';

    // Update the actual API link within the Links content section
    document.getElementById('actual-api-doc-link').setAttribute('href', apiDocsLink);
});

// =========================
// Function Declarations
// =========================
