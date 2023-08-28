/* dcpd_js_date_and_time.js */

// ==========================
// Event Listeners
// ==========================



// =========================
// Function Declarations
// =========================

/**
 * Updates the date and time elements with the current date, time, and time zone.
 * 
 * This function calculates the current date and time, formats them using the provided options,
 * and updates the content of the 'date-time' and 'time-zone' HTML elements to display the
 * formatted values. It also includes the resolved time zone using Intl.DateTimeFormat.
 */
function showDateTime() {
    // Get the current date and time
    const date = new Date();
    
    // Define formatting options for date and time
    const options = {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    };
    
    // Format date and time using the specified options
    const formattedDateTime = date.toLocaleDateString('en-US', options);
    
    // Get the resolved time zone using Intl.DateTimeFormat
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Update the corresponding HTML elements with the formatted date, time, and time zone
    document.getElementById('date-time').textContent = formattedDateTime;
    document.getElementById('time-zone').textContent = timeZone;
}