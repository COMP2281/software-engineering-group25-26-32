const d = new Date()
const year = d.getFullYear()
document.getElementById("toYear").value = year;
document.getElementById("fromYear").setAttribute("max", year);
document.getElementById("toYear").setAttribute("max", year);

div = document.getElementById("departmentFilters");
departments = async function fetchDepartments() {
    try {
        const response = await fetch('http://localhost:8000/departments');
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
        const response = await fetch('http://localhost:8000/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term: searchTerm, count: resultCount, fromYear: fromYear, toYear: toYear, includeUnknown: includeUnknown, authorField: authorField, departments: depts })
        });

        const results = await response.json();
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';

        if (results.length > 0) {
            // Debug response
            console.log(results);
            ctr = 0;
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

                button.innerHTML = "<b>" + item.name + "</b> &nbsp;-&nbsp; " + item.author + " (" + item.year + ")"; 

                h2.appendChild(button);
                div.appendChild(h2);

                let divCollapse = document.createElement('div');
                divCollapse.classList.add('accordion-collapse', 'collapse');
                divCollapse.setAttribute('id', 'collapse' + ctr);

                let divBody = document.createElement('div');
                divBody.classList.add('accordion-body');

                divBody.innerHTML = "<h4>Abstract:</h4>";
                if (item.abstract) {
                    divBody.innerHTML += item.abstract;
                } else {
                    divBody.innerHTML += "No abstract available.";
                }
                divBody.innerHTML += "<br><h4>Full Thesis:</h4>";
                if (item.pdf_url) {
                    divBody.innerHTML += `<a href="${item.pdf_url}" target="_blank">View PDF</a>`;
                    divBody.innerHTML += `<br><button id =summary-btn-${item.db_id} class="btn btn-secondary btn-sm mt-2 summary-btn">Summarise Thesis</button>`;
                } else {
                    divBody.innerHTML += "Not available.";
                }

                divCollapse.appendChild(divBody);
                div.appendChild(divCollapse);
                resultsDiv.appendChild(div);

                
            };
                document.querySelectorAll(`.summary-btn`).forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const db_id = this.id.split('-')[2];
                        this.disabled = true;
                        this.insertAdjacentHTML('afterend', `<div id = "summary-${db_id}"><br><h4>AI Summary:</h4><span>Generating summary...</span></div>`);
                        const summaryResponse = await fetch(`http://localhost:8000/summarise/${db_id}`);
                        const summaryData = await summaryResponse.json();
                        console.log(summaryData.summary);
                        let summary = summaryData.summary
                        var converter = new showdown.Converter();
                        summary = converter.makeHtml(summary);
                        document.getElementById(`summary-${db_id}`).innerHTML = `<br><h4>AI Summary:</h4>${summary}`;
                        this.style.display = "none";
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

