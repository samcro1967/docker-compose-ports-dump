/* dcpd_js_functions.js */

// =========================
// Path Constants
// =========================

const DATA_PATH = '../data/';

// =========================
// Utility Functions
// =========================

/**
 * Parses a CSV string into an array of objects.
 *
 * @param {string} data - The CSV data to be parsed.
 * @returns {Array} - An array of objects representing rows of CSV data.
 */
function parseCSV(data) {
    const rows = data.split("\n");
    const header = rows[0].split(',');
    const columnCount = header.length;

    return rows.slice(1).map(row => {
        const columns = splitCSVRow(row);
        if (columns.length === columnCount) {
            const rowData = {};
            for (let i = 0; i < columnCount; i++) {
                rowData[header[i].trim()] = columns[i].replace(/"/g, '').trim();
            }
            return rowData;
        }
    }).filter(row => row !== undefined);
}

/**
 * Splits a CSV row string into its individual columns, taking into account quoted fields.
 *
 * This function handles CSV rows where fields can optionally be wrapped in double quotes.
 * Fields with embedded commas will only be correctly parsed if they are wrapped in double quotes.
 *
 * @param {string} row - The CSV row string to be split.
 * @returns {Array<string>} An array of strings where each string represents a field from the CSV row.
 *
 * @example
 * // returns ['John', 'Doe', 'New York, NY', 'Engineer']
 * splitCSVRow('John,Doe,"New York, NY",Engineer');
 */
function splitCSVRow(row) {
    const result = [];
    let startValueIndex = 0;
    let inQuotes = false;
    for (let i = 0; i < row.length; i++) {
        if (row[i] === '"') {
            inQuotes = !inQuotes;  // toggle state
        }
        if (row[i] === ',' && !inQuotes) {
            result.push(row.substring(startValueIndex, i));
            startValueIndex = i + 1;
        }
    }
    result.push(row.substring(startValueIndex));
    return result;
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

// =========================
// Webpage Style Management
// =========================

/**
 * Fetches and applies background and text color styles from ../data/dcpd_html.json.
 */
function loadWebpageStyles() {
	console.log("loadWebpageStyles is called");
    fetch(DATA_PATH + 'dcpd_html.json')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched data:", data);
			// Assign values from the JSON to CSS Custom Properties
            document.documentElement.style.setProperty('--dynamic-background-color', data.background_color);
            document.documentElement.style.setProperty('--dynamic-accent-color', data.accent_color);
            document.documentElement.style.setProperty('--dynamic-text-color', data.text_color);
            document.documentElement.style.setProperty('--dynamic-font-name', data.font_name);
            document.documentElement.style.setProperty('--dynamic-font-link', data.font_link);
            document.documentElement.style.setProperty('--dynamic-font-size', data.font_size);
            
            // Log font-related data to the console
            console.log('Font Name:', data.font_name);
            console.log('Font Link:', data.font_link);
            console.log('Font Size:', data.font_size);

            // Append the font link after styles have been set:
            var dynamicFontLink = getComputedStyle(document.documentElement).getPropertyValue('--dynamic-font-link').trim();
			console.log("Dynamic Font Link:", dynamicFontLink);
            if (dynamicFontLink && dynamicFontLink !== "--dynamic-font-link") {
                console.log("Appending font link to head");
				var linkElement = document.createElement("link");
                linkElement.setAttribute("rel", "stylesheet");
                linkElement.setAttribute("href", dynamicFontLink);
				console.log(linkElement);
                
                document.head.appendChild(linkElement);
            } else {
                console.warn('Dynamic font link not found or invalid.');
            }
        })
        .catch(error => {
            console.error('Error fetching webpage styles:', error);
        });
}

// =========================
// Content Display Management
// =========================

/**
 * Displays the specified content section and hides others.
 *
 * @param {string} contentId - The ID of the content section to be displayed.
 */
function showContent(contentId) {
    // Hide all predefined content sections
    $('#ports-content').hide();
    $('#docker-inspect-content').hide();
    $('#docker-ps-content').hide();
    $('#docker-stats-content').hide();
    $('#host-networking-content').hide();
    $('#info-log-content').hide();
    $('#debug-log-content').hide();
    $('#debug-info-content').hide();
    $('#config-file-content').hide();
    $('#stats-file-content').hide();
    $('#readme-content').hide();
    $('#api-docs-content').hide();

    // Hide all footer-related elements
    $('#datetime-container').hide();
    $('#location_temperature-container').hide();
    $('#rounded-footer-container').hide(); // We are hiding the parent container of both #footer-container and version container

    // Display the content section specified by the 'contentId' parameter
    $('#' + contentId).show();

    // If the specified content section is 'ports-content', show the related containers
    if (contentId === 'ports-content') {
        $('#datetime-container').show();
        $('#location_temperature-container').show();
        $('#rounded-footer-container').show(); // We show the parent container which contains both footer info and version info
    }
}

// =========================
// Log Management
// =========================

/**
 * Exports a log file by initiating a download.
 *
 * @param {string} logPath - The path to the log file.
 * @param {string} targetElementId - The ID of the target element to display errors.
 */
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
 * Fetches log data from a specified file and displays it in a given HTML element.
 *
 * @param {string} filePath - The path to the log file.
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

// =========================
// Table Management
// =========================

/**
 * Fetches CSV data and populates the table with its content.
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
 * Refreshes the table by fetching new CSV data and repopulating it.
 */
function refreshTable() {
    // Destroy any existing table sorter, clear table body
    $("#ports_table").trigger('destroy');
    $("#ports_table tbody").empty();
    
    // Fetch new CSV data with timestamp to prevent caching
    $.get(DATA_PATH + 'dcpd.csv?' + new Date().getTime(), function (data) {
        const rows = parseCSV(data);
        
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

// =========================
// Export Functions
// =========================

/**
 * Initiates the download of the redacted support file.
 */
function exportRedactedSupportFile() {
    let fileUri = "../data/redacted_dcpd_files.zip";

    let link = document.createElement("a");
    link.setAttribute("href", fileUri);
    link.setAttribute("download", "redacted_dcpd_files.zip");
    document.body.appendChild(link);
    link.click();  // Triggering a click event to initiate the download
    document.body.removeChild(link);  // Removing the temporary link
}

// =========================
// Sidenav Functions
// =========================

// Variables to store the last clicked sidenav link
let lastActiveLink = null;

/**
 * Removes the 'active' class from all sidenav links.
 */
function removeAllActiveClasses() {
    const links = document.querySelectorAll('.sidenav a');
    links.forEach(link => link.classList.remove('active'));
}

/**
 * Highlights the given link and removes highlights from other links.
 * Also, stores this link as the last clicked link.
 * @param {Element} activeLink - The link that was clicked.
 */
function highlightActiveLink(activeLink) {
    removeAllActiveClasses();
    activeLink.classList.add('active');
    lastClickedLink = activeLink;  // Stores the last clicked sidenav link
}

/**
 * Re-highlights the last clicked sidenav link.
 */
function reHighlightLastActiveLink() {
    if (lastClickedLink) {
        lastClickedLink.classList.add('active');
    }
}