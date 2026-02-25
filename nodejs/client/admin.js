document.getElementById("dbu").addEventListener('click', async function() {
    const response = await fetch("http://localhost:8000/update-db",{
        method: 'POST',
        credentials: 'include'
    });
    console.log(response);
});

document.getElementById("createAdminForm").addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById("newAdminUsername").value;
    const password = document.getElementById("newAdminPassword").value;
    const response = await fetch("http://localhost:8000/create-admin",{
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ "username": username, "password": password }),
        headers: { 'Content-Type': 'application/json' }
    });
    console.log(response);
});