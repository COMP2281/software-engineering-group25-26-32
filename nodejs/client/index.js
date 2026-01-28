document.getElementById('searchForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const searchTerm = document.getElementById('searchTerm').value;

    try {
        const response = await fetch('http://localhost:8080/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term: searchTerm })
        });

        const results = await response.json();
        const resultsList = document.getElementById('results');
        resultsList.innerHTML = '';

        if (results.length > 0) {
            results.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.name; // Assuming the database has a "name" column
                resultsList.appendChild(li);
            });
        } else {
            document.getElementById('message').innerText = 'No results found.';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('message').innerText = 'An error occurred.';
    }
});
