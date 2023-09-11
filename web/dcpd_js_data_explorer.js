/* dcpd_js_data_explorer.js */

// ==========================
// Event Listeners
// ==========================

/**
 * Add a click event listener to the 'view-data-explorer' button.
 * This listener highlights the active link, shows the data explorer content, 
 * loads the data using the default value from the dropdown, and sets the dropdown 
 * to its first option.
 */
document.getElementById('view-data-explorer').addEventListener('click', function() {
    highlightActiveLink(this);
    showContent('data-explorer-content');
    
    // Get the dropdown and set its default selected index to 0.
    const dropdown = document.getElementById('data_explorer_dropdown');
    dropdown.selectedIndex = 0; // This sets the dropdown to its first option.
    
    // Retrieve the value from the dropdown.
    const defaultSource = dropdown.value;
    
    // Load the data using the default value.
    loadData(defaultSource);
});

/**
 * Add a change event listener to the 'data_explorer_dropdown' select element.
 * This listener loads the data based on the selected value from the dropdown.
 */
document.getElementById('data_explorer_dropdown').addEventListener('change', function() {
    const selectedSource = this.value;
    loadData(selectedSource);
});

/**
 * Add a click event listener to the 'refresh-data-explorer' button.
 * This listener reloads the data based on the currently selected value from the dropdown.
 */
document.getElementById('refresh-data-explorer').addEventListener('click', function() {
    const currentSource = document.getElementById('data_explorer_dropdown').value;
    loadData(currentSource);
    reHighlightLastActiveLink();
});

/**
 * Add a click event listener to the 'exportDataExplorer' button.
 * This listener exports the data based on the currently selected value from the dropdown.
 */
document.getElementById('exportDataExplorer').addEventListener('click', function() {
    const currentSource = document.getElementById('data_explorer_dropdown').value;
    const filePathMap = {
        'docker-inspect': 'dcpd_docker_inspect.csv',
        'docker-ps': 'dcpd_docker_ps.csv',
        'host-networking': 'dcpd_host_networking.csv'
    };
    exportLog(DATA_PATH + filePathMap[currentSource], 'data-explorer-area');
    reHighlightLastActiveLink();
});


// =========================
// Function Declarations
// =========================

/**
 * Load data based on the specified source type.
 * @param {string} sourceType - The type of data source to load.
 */
function loadData(sourceType) {
    const dataPathMap = {
        'docker-inspect': 'dcpd_docker_inspect.csv',
        'docker-ps': 'dcpd_docker_ps.csv',
        'host-networking': 'dcpd_host_networking.csv'
    };

    fetch(DATA_PATH + dataPathMap[sourceType])
        .then(response => response.text())
        .then(data => {
            const rows = parseCSV(data);
            rows.sort((a, b) => Number(a.id) - Number(b.id));

            createTableFromData(rows);
        })
        .catch(error => {
            console.error(`Error fetching ${sourceType} data:`, error);
        });
}

/**
 * Create a table element and populate it with data.
 * @param {Array} data - The data to populate the table with.
 */
function createTableFromData(data) {
    if (data.length === 0) return;

    // Create a new table
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');
    table.appendChild(thead);
    table.appendChild(tbody);

    // Create the table headers
    const headers = Object.keys(data[0]);
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Populate the table body
    data.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            td.textContent = row[header];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    // Clear any previous table in the section and Append the new table
    const contentSection = document.getElementById('data-explorer-table-section');
    contentSection.innerHTML = ''; // Clear previous table data
    contentSection.appendChild(table);
}
