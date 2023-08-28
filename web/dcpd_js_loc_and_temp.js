/* dcpd_js_loc_and_temp.js */

// ==========================
// Event Listeners
// ==========================



// =========================
// Function Declarations
// =========================

/**
 * Updates the location and temperature information in the DOM.
 * 
 * This function fetches data from 'dcpd_html.json', which presumably contains location
 * and temperature information. Upon successful fetching, the function updates the temperature
 * elements with both Fahrenheit and Celsius values, as well as the location element in the DOM.
 * Any error that occurs during fetching is caught and logged to the console.
 */
function updateLocationAndTemperature() {
    fetch(DATA_PATH + 'dcpd_html.json')
        .then(response => response.json())
        .then(data => {
            // Update location and temperature in the DOM
            const temperatureElement = document.getElementById('temperature');
            temperatureElement.innerText = `${data.temperature_F} / ${data.temperature_C}`;
            document.getElementById('location').innerText = data.location;
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}