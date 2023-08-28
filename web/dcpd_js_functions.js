// =========================
// Function Declarations
// =========================

// =========================
// Path Constants
// =========================
const DATA_PATH = '../data/';

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
                    updateMessageElement.textContent = "Update Available";
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

// Function to export logs
function exportLog(logPath, targetElementId) {
    $.ajax({
        type: "GET",
        url: logPath,
        dataType: "text",
        success: function(data) {
            var blob = new Blob([data], { type: 'text/plain' });
            var url = URL.createObjectURL(blob);
            var link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", logPath.split('/').pop());
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },
        error: function() {
            $("#" + targetElementId).text("Error exporting log.");
        }
    });
}

/**
 * Fetch CSV data and populate the table.
 */
function fetchAndPopulateTable() {
    $.get('../data/dcpd.csv', function (data) {
        const rows = parseCSV(data);
        populateTable(rows);
        $("#ports_table").tablesorter({
            theme: 'default',
            widgets: ['zebra', 'filter', 'stickyHeaders'],
            widgetOptions: {
                filter_external: '.search',
                filter_defaultFilter: { 1: '~{q}' },
                filter_columnFilters: true,
            }
        });
    });
}

/**
 * Fetches and applies background and text color styles from ../data/dcpd_html.json.
 */
function loadWebpageStyles() {
    fetch(DATA_PATH + 'dcpd_html.json')
        .then(response => response.json())
        .then(data => {
            // Assign values from the JSON to CSS Custom Properties
            document.documentElement.style.setProperty('--dynamic-background-color', data.background_color);
            document.documentElement.style.setProperty('--dynamic-text-color', data.text_color);
        })
        .catch(error => {
            console.error('Error fetching webpage styles:', error);
        });
}

/**
 * Fetches and displays data from ../data/dcpd_host_networking.csv.
 */
function loadHostNetworkingData() {
    fetch(DATA_PATH + 'dcpd_host_networking.csv')
        .then(response => response.text()) 
        .then(data => {
            const rows = parseCSV(data);
            
			// Sort the rows numerically based on the 'id' field
			rows.sort((a, b) => Number(a.id) - Number(b.id));

            // Use the "populateTable" function or a similar function tailored for the host networking table
			populateHostNetworkingTable(rows);
        })
        .catch(error => {
            console.error('Error fetching host networking data:', error);
        });
}

/**
 * Function to populate the host networking table with given data.
 *
 * @param {Array} data - An array of objects to populate the table.
 */
function populateHostNetworkingTable(data) {
    const tableBody = $("#host_networking_table tbody");
    // Clear the tbody first
    tableBody.empty();
    data.forEach(row => {
        const tr = $("<tr>");
        tr.append($("<td>").text(row["id"].replace(/"/g, '')));
        tr.append($("<td>").text(row["service_name"].replace(/"/g, '')));
        tableBody.append(tr);
    });
}

/**
 * Updates the date, time, and timezone on the interface.
 * 
 * This function fetches the current date, time, and timezone using the browser's
 * built-in Date and Intl.DateTimeFormat APIs. After fetching the details, it
 * updates the respective DOM elements to reflect these values.
 */
function updateDateTime() {
    // Get the current date and time
    let now = new Date();

    // Convert the date and time to string format
    let dateString = now.toLocaleDateString();
    let timeString = now.toLocaleTimeString();

    // Get the current timezone using the Intl API
    let timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    // Update the 'current-date-time' element with the fetched date and time
    document.getElementById('current-date-time').textContent = dateString + ' ' + timeString;

    // Update the 'timezone' element with the fetched timezone
    document.getElementById('time-zone').textContent = `Timezone: ${timeZone}`;
}

/**
 * Displays the specified content section and hides others.
 * 
 * Given the ID of a content section, this function displays that particular section
 * and hides all other predefined sections. Additionally, depending on the content
 * section that is being displayed, it also handles the visibility of related containers
 * such as 'datetime-container', 'location_temperature-container', and 'footer-container'.
 *
 * @param {string} contentId - The ID of the content section to be displayed.
 */
function showContent(contentId) {
    // Hide all predefined content sections
    $('#ports-content').hide();
    $('#host-networking-content').hide();
    $('#info-log-content').hide();
    $('#debug-log-content').hide();
    $('#debug-info-content').hide();
    $('#config-file-content').hide();
    $('#stats-file-content').hide();
    $('#readme-content').hide();

    // Display the content section specified by the 'contentId' parameter
    $('#' + contentId).show();

    // If the specified content section is 'ports-content', show the related containers
    // Otherwise, hide them
    if (contentId === 'ports-content') {
        $('#datetime-container').show();
        $('#location_temperature-container').show();
        $('#footer-container').show();
    } else {
        $('#datetime-container').hide();
        $('#location_temperature-container').hide();
        $('#footer-container').hide();
    }
}

/**
 * Fetches log data from the specified file and displays it in the specified HTML element.
 * 
 * This function fetches log data from the provided file path and updates the content of
 * the HTML element with the provided ID to display the fetched log data. It utilizes the
 * Fetch API to retrieve the log data asynchronously.
 *
 * @param {string} filePath - The path to the log file to fetch.
 * @param {string} elementId - The ID of the HTML element to display the fetched log data.
 */
function loadLog(filePath, elementId) {
    // Fetch the log file content using the provided file path
    fetch(filePath)
        .then(response => response.text())  // Extract the response as text
        .then(data => {
            // Update the content of the specified HTML element with the fetched log data
            document.getElementById(elementId).textContent = data;
        })
        .catch(error => {
            // Handle errors by logging an error message
            console.error('Error fetching logs:', error);
        });
}

/**
 * Fetches footer data from a JSON file and updates the corresponding elements.
 * 
 * This function fetches footer data from a JSON file named 'dcpd_html.json' and updates
 * the content of specific HTML elements to display the retrieved information. It utilizes
 * the Fetch API to retrieve JSON data asynchronously.
 */
function updateFooter() {
    // Fetch the JSON data from 'dcpd_html.json' file
    fetch(DATA_PATH + 'dcpd_html.json')
        .then(response => response.json())  // Extract the response as JSON
        .then(data => {
            // Update the HTML elements with the retrieved footer data
            document.getElementById('current-file-name').textContent = data.html_file_name;
            document.getElementById('file-update-time').textContent = data.last_updated;
        })
        .catch(error => {
            // Handle errors by logging an error message
            console.error('Error fetching data:', error);
        });
}

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

/**
 * Parses CSV data into an array of objects.
 * 
 * This function takes a CSV data string and parses it into an array of objects,
 * where each object represents a row of data from the CSV. It first splits the data
 * into rows and extracts the header row. Then, it maps each row to an object with
 * keys from the header and values from the respective columns. The function ensures
 * that rows with the correct number of columns are processed and any quotes around
 * values are removed.
 *
 * @param {string} data - CSV data string to be parsed.
 * @returns {Array} - An array of objects representing rows of CSV data.
 */
function parseCSV(data) {
    const rows = data.split("\n");
    const header = rows[0].split(',');
    const columnCount = header.length;

    return rows.slice(1).map(row => {
        const columns = row.split(",");
        if (columns.length === columnCount) {
            const rowData = {};
            for (let i = 0; i < columnCount; i++) {
                rowData[header[i]] = columns[i].replace(/"/g, '');
            }
            return rowData;
        }
    }).filter(row => row !== undefined);
}

/**
 * Refreshes the table by fetching CSV data and repopulating it.
 * 
 * This function triggers the refresh of the table by first destroying any existing
 * table sorters, clearing the table body, fetching new CSV data asynchronously, parsing
 * the data using the parseCSV function, populating the table with the parsed data using
 * the populateTable function, and finally applying tablesorter to the table with the
 * appropriate widgets and options.
 */
function refreshTable() {
    // Destroy any existing table sorter, clear table body
    $("#ports_table").trigger('destroy');
    $("#ports_table tbody").empty();
    
    // Fetch new CSV data with timestamp to prevent caching
    $.get(DATA_PATH + 'dcpd.csv' + new Date().getTime(), function (data) {
        const rows = parseCSV(data);
        
        // Note: "populateTable" function is referenced but not defined in the provided code.
        populateTable(rows);  // Call the populateTable function
        
        // Apply tablesorter to the table with widgets and options
        $("#ports_table").tablesorter({
            theme: 'default',
            widgets: ['zebra', 'filter', 'stickyHeaders'],
            widgetOptions: {
                filter_external: '.search',
                filter_defaultFilter: { 1: '{q}' },
                filter_columnFilters: true,
            }
        });
    });
}

/**
 * Function to populate the table with given data.
 *
 * @param {Array} data - An array of objects to populate the table.
 */
function populateTable(data) {
	const tableBody = $("#ports_table tbody");

	// For each row in the data, append a table row to the table body.
	data.forEach(row => {
		const tr = $("<tr>");
		// For each column in the data, append a table cell to the table row.
		// Additionally, any quotes from the CSV data are removed.
		tr.append($("<td>").text(row["Service Name"].replace(/"/g, '')));
		tr.append($("<td>").text(row["External Port"].replace(/"/g, '')));
		tr.append($("<td>").text(row["Internal Port"].replace(/"/g, '')));
		tr.append($("<td>").text(row["Port Mapping"].replace(/"/g, '')));
		tr.append($("<td>").text(row["Mapped App"].replace(/"/g, '')));
		tableBody.append(tr);
	});
}

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

// Function to trigger download of the redacted support file
function exportRedactedSupportFile() {
    let fileUri = "../data/redacted_dcpd_files.zip";

    let link = document.createElement("a");
    link.setAttribute("href", fileUri);
    link.setAttribute("download", "redacted_dcpd_files.zip");
    document.body.appendChild(link);
    link.click();  // Triggering a click event to initiate the download
    document.body.removeChild(link);  // Removing the temporary link
}