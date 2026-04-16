const API_BASE = 'http://localhost:8000/api';

// Selectors
const queryInput = document.getElementById('query-input');
const btnRun = document.getElementById('btn-run');
const btnSeed = document.getElementById('btn-seed');
const tableList = document.getElementById('table-list');
const emptyState = document.getElementById('empty-state');
const loader = document.getElementById('loader');
const resultsContent = document.getElementById('results-content');
const sqlDisplay = document.getElementById('sql-display');
const tableHead = document.getElementById('table-head');
const tableBody = document.getElementById('table-body');

/**
 * Initialize the App
 */
async function init() {
    await fetchSchema();
    
    btnRun.addEventListener('click', handleRunQuery);
    btnSeed.addEventListener('click', handleSeedData);
    
    // Allow Cmd+Enter to run query
    queryInput.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            handleRunQuery();
        }
    });
}

/**
 * Fetch and Render Schema Sidebar
 */
async function fetchSchema() {
    try {
        const response = await fetch(`${API_BASE}/tables`);
        const data = await response.json();
        
        tableList.innerHTML = '';
        
        if (data.tables.length === 0) {
            tableList.innerHTML = '<div class="table-item"><div class="table-name">No tables found</div></div>';
            return;
        }

        data.tables.forEach(table => {
            const item = document.createElement('div');
            item.className = 'table-item';
            item.innerHTML = `
                <div class="table-name">${table.name}</div>
                <div class="table-stats">${table.columns.length} columns • ${table.row_count} rows</div>
            `;
            tableList.appendChild(item);
        });
    } catch (error) {
        console.error('Error fetching schema:', error);
        tableList.innerHTML = '<div class="table-item" style="color: var(--error)">Error loading schema</div>';
    }
}

/**
 * Handle Query Execution
 */
async function handleRunQuery() {
    const question = queryInput.value.trim();
    if (!question) return;

    // UI States
    emptyState.style.display = 'none';
    resultsContent.style.display = 'none';
    loader.style.display = 'flex';
    btnRun.disabled = true;
    btnRun.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (response.ok) {
            renderResults(data);
        } else {
            showError(data.detail || 'An error occurred');
        }
    } catch (error) {
        showError('Could not connect to backend server. Make sure it is running on port 8000.');
    } finally {
        loader.style.display = 'none';
        btnRun.disabled = false;
        btnRun.innerHTML = '<i class="fas fa-play"></i> &nbsp; Run Query';
        // Refresh sidebar stats
        fetchSchema();
    }
}

/**
 * Render Results to Table
 */
function renderResults(data) {
    resultsContent.style.display = 'flex';
    sqlDisplay.textContent = data.generated_sql;

    // Reset table
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';

    if (data.results.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="100%" style="text-align: center; color: var(--text-muted); padding: 40px;">Query returned no data</td></tr>';
        return;
    }

    // Get headers from first result
    const headers = Object.keys(data.results[0]);
    const headerRow = document.createElement('tr');
    headers.forEach(h => {
        const th = document.createElement('th');
        th.textContent = h;
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);

    // Build rows
    data.results.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach(h => {
            const td = document.createElement('td');
            td.textContent = row[h] !== null ? row[h] : 'NULL';
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

/**
 * Handle Database Seeding
 */
async function handleSeedData() {
    if (!confirm('This will wipe your current database and seed it with fresh sample data. Continue?')) return;
    
    btnSeed.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Seeding...';
    btnSeed.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/seed`, { method: 'POST' });
        if (response.ok) {
            alert('Database seeded successfully!');
            await fetchSchema();
        }
    } catch (error) {
        alert('Failed to seed database.');
    } finally {
        btnSeed.innerHTML = '<i class="fas fa-magic"></i> Seed Sample Data';
        btnSeed.disabled = false;
    }
}

/**
 * Show Error Message
 */
function showError(message) {
    resultsContent.style.display = 'none';
    emptyState.style.display = 'flex';
    emptyState.innerHTML = `
        <i class="fas fa-exclamation-circle" style="color: var(--error); opacity: 1;"></i>
        <p style="color: var(--error); font-weight: 500;">Error: ${message}</p>
    `;
}

// Start the app
init();
