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
        const resultsList = document.getElementById('results');
        resultsList.innerHTML = '';

        if (results.length > 0) {
            results.forEach(item => {
                const li = document.createElement('li');
                // Handle 'nan' values for year
                if (item.year == 0) {
                    item.year = "Unknown Year";
                }
                if (item.author == 0) {
                    item.author = "Unknown Author";
                }
                li.textContent = item.name + " - " + item.author + " (" + item.year + ")"; 
                resultsList.appendChild(li);
                document.getElementById('message').innerText = '';

            });
        } else {
            document.getElementById('message').innerText = 'No results found.';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('message').innerText = 'An error occurred.';
    }
});