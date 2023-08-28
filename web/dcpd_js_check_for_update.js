/* dcpd_js_check_for_update.js */

// ==========================
// Event Listeners
// ==========================



// =========================
// Function Declarations
// =========================

/**
 * Fetches the current and latest versions from ../data/dcpd_html.json.
 * Compares the two versions and displays an appropriate message.
 */
function checkForUpdate() {
    fetch(DATA_PATH + 'dcpd_html.json')
        .then(response => response.json())
        .then(data => {
            const currentVersion = data.current_version;
            const latestVersion = data.latest_version;

            const updateMessageElement = document.getElementById("update-info");
            
            if (currentVersion === latestVersion) {
                if (updateMessageElement) {
                    updateMessageElement.textContent = "No update available";
                    updateMessageElement.style.color = "green";
                }
            } else {
                if (updateMessageElement) {
                    updateMessageElement.textContent = `Latest Version: ${latestVersion}`;
                    updateMessageElement.style.color = "red";
					updateMessageElement.style.backgroundColor = "white";
					updateMessageElement.classList.add("blinking");
                }
            }
        })
        .catch(error => {
            console.error('Error fetching versions:', error);
        });
}