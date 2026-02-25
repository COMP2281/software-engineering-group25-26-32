document.getElementById("dbu").addEventListener('click', async function() {
    const response = await fetch("http://localhost:8000/update-db",{
        method: 'POST',
        credentials: 'include'
    });
    console.log(response);
});