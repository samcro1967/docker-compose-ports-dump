/* dcpd_js_apidocs.js */

// ==========================
// Event Listeners
// ==========================

// Event listener that gets triggered when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Derive the current host based on the window's location properties
    const currentHost = window.location.protocol + '//' + window.location.hostname + ':51763';

    // Construct the API docs link using the current host
    const apiDocsLink = currentHost + '/apidocs/';

    // Update the actual API link within the API Docs content section
    document.getElementById('actual-api-doc-link').setAttribute('href', apiDocsLink);

    // Add click event listener for the "view-api-docs" link
    document.getElementById('view-api-docs').addEventListener('click', function(event) {
        // Prevent the default action of the link (navigation)
        event.preventDefault();

        // Display the API Docs content section and hide others
        showContent('api-docs-content');

        // Highlight the 'view-api-docs' link and remove 'active' from others
        highlightActiveLink(this);
    });
});

// =========================
// Function Declarations
// =========================
