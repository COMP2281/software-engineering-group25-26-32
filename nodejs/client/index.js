const API_URL = "https://api.piggypiggyyoinkyoink.website"; // Change this if your backend is hosted elsewhere

const d = new Date()
const year = d.getFullYear()
document.getElementById("toYear").value = year;
document.getElementById("fromYear").setAttribute("max", year);
document.getElementById("toYear").setAttribute("max", year);

// Converts Markdown text to HTML
function renderMarkdownToHtml(mdText) {
    const converter = new showdown.Converter();
    const html = converter.makeHtml(mdText || "");
    return DOMPurify.sanitize(html);
}

const citationStyles = ['UKHarvard', 'APA', 'MLA', 'Chicago', 'IEEE', 'Harvard'];
const citationModes = ['full', 'intext', 'footnote'];

function citationCreate(item, style = "UKHarvard", mode = "full") {
    const authorRaw = item.author?.trim() || "Unknown Author";
    const year = item.year || "n.d.";
    const title = item.name || "Untitled";
    const university = item.university || "Durham University";
    const repository = "Durham e-Theses"; // Default for UKHarvard

    const authorParts = authorRaw.split(/\s+/);
    const firstName = authorParts.slice(0, -1).join(" ") || "Unknown";
    const lastName = authorParts.slice(-1)[0] || "Author";

    const url = item.pdf_url || "#";

    function formatAuthor(style, mode) {
        switch (style) {
            case "UKHarvard":
                return `${lastName.toUpperCase()}, ${firstName}`;
            case "APA":
                if (mode === "intext") return `(${lastName}, ${year})`;
                return `${lastName}, ${firstName.charAt(0)}. (${year}).`;
            case "MLA":
                if (mode === "intext") return `(${lastName})`;
                return `${lastName}, ${firstName}.`;
            case "Chicago":
                if (mode === "intext") return `(${lastName} ${year})`;
                return `${firstName} ${lastName}`;
            case "IEEE":
                if (mode === "intext") return `[YOUR CITATION NUMBER]`;
                return `${firstName.charAt(0)}. ${lastName}`;
            case "Harvard":
                if (mode === "intext") return `(${lastName} ${year})`;
                return `${lastName}, ${firstName.charAt(0)}.`;
            default:
                return `${lastName}, ${firstName}`;
        }
    }

    const authorFormatted = formatAuthor(style, mode);
    let citation = "";
    switch (style) {
        case "UKHarvard":
            citation = `${authorFormatted} (${year}). ${title}, ${repository}. ${url}`;
            break;
        case "APA":
            citation = mode === "intext"
                ? authorFormatted
                : `${authorFormatted} ${title}. (${university}). ${url}`;
            break;
        case "MLA":
            citation = mode === "intext"
                ? authorFormatted
                : `${authorFormatted} "${title}." (${university}, ${year}). ${url}`;
            break;
        case "Chicago":
            citation = mode === "intext"
                ? authorFormatted
                : `${authorFormatted}. "${title}." (${university}, ${year}). ${url}`;
            break;
        case "IEEE":
            citation = mode === "intext"
                ? authorFormatted
                : `${authorFormatted}, "${title}," ${university}, ${year}. ${url}`;
            break;
        case "Harvard":
            citation = mode === "intext"
                ? authorFormatted
                : `${authorFormatted} (${year}) ${title}. (${university}). ${url}`;
            break;
        default:
            citation = `${authorFormatted} (${year}). ${title}. (${university}). ${url}`;
    }
    return citation;
}

let div = document.getElementById("departmentFilters");
let departments = async function fetchDepartments() {
    try {
        const response = await fetch(`${API_URL}/departments`);
        const departments = await response.json();
        // console.log(departments);
        for (const dept of departments) {
            if (dept === "") continue; // Skip empty department names
            div.classList.add('form-check');
            let input = document.createElement('input');
            input.classList.add('form-check-input');
            input.classList.add('dept-checkbox');
            input.type = 'checkbox';
            input.id = dept;
            input.value = dept;
            let label = document.createElement('label');
            label.classList.add('form-check-label');
            label.setAttribute('for', dept);
            label.textContent = dept;
            div.appendChild(input);
            div.appendChild(label);
            div.appendChild(document.createElement('br'));
        }
    } catch (error) {
        console.error("Error fetching departments:", error);
    }
}
div.style.display = "none";
document.getElementById("unknownDeptSpan").style.display = "none";
departments();

document.getElementById("searchBtn").addEventListener('click', function() {
    const searchTerm = document.getElementById('searchTerm').value;
    let authorField = document.getElementById('author').value;

    // Check if searchTerm AND authorField are empty, if so reject search
    if (!searchTerm && !authorField) {
        document.getElementById('searchTerm').setCustomValidity('Please enter a search term or author name.');
    } else {
        document.getElementById('searchTerm').setCustomValidity('');
    }
});

document.getElementById('searchForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const searchTerm = document.getElementById('searchTerm').value;
    let resultCount = document.getElementById('resultCount').value;
    let fromYear = document.getElementById('fromYear').value;
    let toYear = document.getElementById('toYear').value;
    let includeUnknown = document.getElementById('includeUnknown').checked;

    resultCount = parseInt(resultCount) || 10; // Default to 10 if input is invalid
    fromYear = parseInt(fromYear) || 0; // Default to 0 if input is invalid
    toYear = parseInt(toYear) || 3000; // Default to 3000 if input is invalid
    let authorField = document.getElementById('author').value;
    let depts = Array.from(document.querySelectorAll('.dept-checkbox:checked')).map(cb => cb.value)

    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term: searchTerm, count: resultCount, fromYear: fromYear, toYear: toYear, includeUnknown: includeUnknown, authorField: authorField, departments: depts })
        });

        const results = await response.json();
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';

        if (results.length > 0) {
            // Debug response
            // console.log(results);
            let ctr = 0;
            resultsDiv.innerHTML = "<h2>Search Results:</h2>";
            for (const item of results) {

                ctr++;
                let div = document.createElement('div');
                div.classList.add('accordion-item');
                let h2 = document.createElement('h2');
                h2.classList.add('accordion-header');
                h2.setAttribute('id', 'heading' + ctr);
                // Handle 'nan' values for year
                if (item.year == 0) {
                    item.year = "Unknown Year";
                }
                if (item.author == 0) {
                    item.author = "Unknown Author";
                }
                let button = document.createElement('button');
                button.classList.add('accordion-button', 'collapsed');
                button.setAttribute('type', 'button');
                button.setAttribute('data-bs-toggle', 'collapse');
                button.setAttribute('data-bs-target', '#collapse' + ctr);
                button.setAttribute('aria-expanded', 'false');
                button.setAttribute('aria-controls', 'collapse' + ctr);

                button.innerHTML = "<b>" + item.name + "</b> &nbsp;-&nbsp; " + item.author + " (" + item.year + ")" + (" | " + Math.round(item.score * 100) / 100 + " relevance"); 

                h2.appendChild(button);
                div.appendChild(h2);

                let divCollapse = document.createElement('div');
                divCollapse.classList.add('accordion-collapse', 'collapse');
                divCollapse.setAttribute('id', 'collapse' + ctr);

                let divBody = document.createElement('div');
                divBody.classList.add('accordion-body');

                divBody.innerHTML = "<h4>Abstract:</h4>";
                if (item.abstract) {
                    // Remove the "Abstract:" prefix if it exists
                    if (item.abstract.toLowerCase().startsWith("abstract:")) {
                        item.abstract = item.abstract.substring(9).trim();
                    }
                    divBody.innerHTML += item.abstract;
                } else {
                    divBody.innerHTML += "No abstract available.";
                }
                divBody.innerHTML += "<br><h4>Full Thesis:</h4>";
                if (item.pdf_url) {
                    divBody.innerHTML += `<a href="${item.pdf_url}" target="_blank">View PDF</a>`;
                    divBody.innerHTML += `<br><button id =summary-btn-${item.db_id} class="btn btn-secondary btn-sm mt-2 summary-btn">Summarise Thesis</button>`;
                    divBody.innerHTML += `<input type = "text" id = "summary-query-${item.db_id}" class = "form-control form-control-sm mt-2 summary-query" placeholder = "Enter Question about thesis"></input>`;
                    divBody.innerHTML += `<button id =summary-query-btn-${item.db_id} class="btn btn-secondary btn-sm mt-2 summary-query-btn" disabled>Ask Question</button>`;
                    divBody.innerHTML += `<div id = "summary-${item.db_id}" style = "display: none;"><br><h4>AI Summary:</h4><span>Generating summary...</span></div>`;
                } else {
                    divBody.innerHTML += "Not available.";
                }

                // Citation for thesis for APA, MLA, Chicago, IEEE, and Harvard styles
                // Click text to copy citation to clipboard, button to switch between styles, button for in-text/footnote citation
                let currentCitation = "UKHarvard";
                let currentMode = "full";
                
                let citation = citationCreate(item);

                divBody.innerHTML += `
                    <br>
                    <h4 id="citation-header-${item.db_id}">Citation (Style: ${currentCitation}, Mode: ${currentMode}):</h4>
                    <button id="citation-style-btn-${item.db_id}" class="btn btn-secondary btn-sm mt-2 citation-style-btn">Switch Citation Style</button>
                    <button id="citation-mode-btn-${item.db_id}" class="btn btn-secondary btn-sm mt-2 citation-mode-btn">Toggle Mode</button>
                    <br>
                    <div id="citation-${item.db_id}" style="cursor: pointer; background-color: #f8f9fa; padding: 5px; border-radius: 4px;" title="Click to copy citation">
                        ${citationCreate(item, currentCitation, currentMode)}
                    </div>
                `;

                divCollapse.appendChild(divBody);
                div.appendChild(divCollapse);
                resultsDiv.appendChild(div);

                const citationHeader = document.getElementById(`citation-header-${item.db_id}`);
                const citationDiv = document.getElementById(`citation-${item.db_id}`);

                document.getElementById(`citation-style-btn-${item.db_id}`).addEventListener('click', () => {
                    let idx = citationStyles.indexOf(currentCitation);
                    currentCitation = citationStyles[(idx + 1) % citationStyles.length]; // cycle styles
                    citationHeader.innerText = `Citation (Style: ${currentCitation}, Mode: ${currentMode}):`;
                    citationDiv.innerText = citationCreate(item, currentCitation, currentMode);
                });

                document.getElementById(`citation-mode-btn-${item.db_id}`).addEventListener('click', () => {
                    currentMode = currentMode === "full" ? "intext" : "full"; // toggle mode
                    citationHeader.innerText = `Citation (Style: ${currentCitation}, Mode: ${currentMode}):`;
                    citationDiv.innerText = citationCreate(item, currentCitation, currentMode);
                });

                citationDiv.addEventListener('click', () => {
                    navigator.clipboard.writeText(citationDiv.innerText)
                        .then(() => alert("Citation copied to clipboard!"));
                });
                
            };
                document.querySelectorAll(`.summary-btn`).forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const db_id = this.id.split('-')[2];
                        this.disabled = true;
                        // this.insertAdjacentHTML('afterend', `<div id = "summary-${db_id}"><br><h4>AI Summary:</h4><span>Generating summary...</span></div>`);
                        document.getElementById(`summary-${db_id}`).style.display = "block";
                        const summaryResponse = await fetch(`${API_URL}/summarise/${db_id}`);
                        let summaryDiv = document.getElementById(`summary-${db_id}`);
                        summaryDiv.innerHTML = `<br><h4>AI Summary:</h4>`;
                        if (!summaryResponse.ok) {
                            summaryDiv.innerHTML += `<span>Error generating summary.</span>`;
                            return;
                        }
                        const summaryData = await summaryResponse.json();
                        const htmlSummary = renderMarkdownToHtml(summaryData.summary);
                        document.getElementById(`summary-${db_id}`).innerHTML = `<br><h4>AI Summary:</h4>${htmlSummary}`;
                        this.style.display = "none";
                    });
                });

                document.querySelectorAll(`.summary-query-btn`).forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const db_id = this.id.split('-')[3];
                        const query = document.getElementById(`summary-query-${db_id}`).value;
                        this.disabled = true;
                        document.getElementById(`summary-query-${db_id}`).disabled = true;
                        this.insertAdjacentHTML('afterend', `<div id = "summary-query-response-${db_id}"><br><h4>AI Response:</h4><span>Generating response...</span></div>`);
                        const summaryResponse = await fetch(`${API_URL}/summarise/${db_id}?query=${encodeURIComponent(query)}`);
                        if (!summaryResponse.ok) {
                            document.getElementById(`summary-query-response-${db_id}`).innerHTML = `<br><h4>AI Response:</h4><span>Error generating response.</span>`;
                            return;
                        }
                        const summaryData = await summaryResponse.json();
                        console.log(summaryData.summary);
                        const htmlSummary = renderMarkdownToHtml(summaryData.summary);
                        document.getElementById(`summary-query-response-${db_id}`).innerHTML = `<br><h4>AI Response:</h4>${htmlSummary}`;
                        this.disabled = false;
                        document.getElementById(`summary-query-${db_id}`).disabled = false;

                    });
                });
                document.querySelectorAll(`.summary-query`).forEach(input => {
                    input.addEventListener('input', function() {
                        const db_id = this.id.split('-')[2];
                        document.getElementById(`summary-query-btn-${db_id}`).disabled = this.value.trim() === "";
                    });
                });
        } else {
            document.getElementById('results').innerText = 'No results found.';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerText = 'An error occurred.';
    }
});

document.getElementById("includeAllDepts").addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.dept-checkbox');
    checkboxes.forEach(cb => cb.checked = false); // Uncheck all department checkboxes
    if (this.checked) {
        document.getElementById("departmentFilters").style.display = "none";
        document.getElementById("unknownDeptSpan").style.display = "none";

    } else {
        document.getElementById("departmentFilters").style.display = "block";
        document.getElementById("unknownDeptSpan").style.display = "block";

    }
});

