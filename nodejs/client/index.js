window.addEventListener('DOMContentLoaded', async (event) => {
    let data = await fetch('http://localhost:8000/');
    const json = await data.json();
    document.getElementById("message").innerText = json.message;
});
