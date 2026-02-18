const d = new Date()
const year = d.getFullYear()
document.getElementById("toYear").value = year;

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

    try {
        const response = await fetch('http://localhost:8000/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term: searchTerm, count: resultCount, fromYear: fromYear, toYear: toYear, includeUnknown: includeUnknown })
        });

        const results = await response.json();
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';

        if (results.length > 0) {
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

                divBody.innerHTML = "<h5>Abstract:</h5>";
                if (item.abstract) {
                    divBody.innerHTML += item.abstract;
                } else {
                    divBody.innerHTML += "No abstract available.";
                }
                divBody.innerHTML += "<br><h5>Full Thesis:</h5>";
                if (item.pdf_url) {
                    divBody.innerHTML += `<a href="${item.pdf_url}" target="_blank">View PDF</a>`;
                } else {
                    divBody.innerHTML += "Not available.";
                }

                divCollapse.appendChild(divBody);
                div.appendChild(divCollapse);

                resultsDiv.appendChild(div);
            };
        } else {
            document.getElementById('results').innerText = 'No results found.';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerText = 'An error occurred.';
    }
});