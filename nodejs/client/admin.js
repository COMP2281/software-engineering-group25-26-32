// Rebuild the database
document.getElementById("dbu").addEventListener('click', async function() {
    // Apply a status message to the user
    var statusMess = document.getElementById("statusMessage");
    statusMess.innerHTML = "Updating database, please wait...";
    statusMess.style.color = "red";

    const response = await fetch("http://localhost:8000/update-db",{
        method: 'POST',
        credentials: 'include'
    });
    if (response.ok) {
        statusMess.innerHTML = "Database updated successfully!<br>";
        statusMess.innerHTML += response.message;
        statusMess.style.color = "green";
    } else {
        const errorData = await response.json();
        statusMess.innerHTML = "Error updating database: " + errorData.detail;
    }
    console.log(response);
});

// Reindex from the database
document.getElementById("idx").addEventListener('click', async function() {
    // Apply a status message to the user
    var statusMess = document.getElementById("statusMessage");
    statusMess.innerHTML = "Reindexing based off of the current database, please wait...";
    statusMess.style.color = "red";

    const response = await fetch("http://localhost:8000/index",{
        method: 'POST',
        credentials: 'include'
    });

    if (response.ok) {
        statusMess.innerHTML = "Reindexing successful!<br>";
        statusMess.innerHTML += statusMess.message;
        statusMess.style.color = "green";
    } else {
        const errorData = await response.json();
        statusMess.innerHTML = "Error reindexing: " + errorData.detail;
    }
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
    if (response.ok) {
        alert("Admin user created successfully");
        document.getElementById("newAdminUsername").value = "";
        document.getElementById("newAdminPassword").value = "";
    } else{
        const errorData = await response.json();
        alert("Error creating admin user: " + errorData.detail);
    }
    console.log(response);
});

document.getElementById("deleteAdminForm").addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById("deletedAdminUsername").value;
    const response = await fetch("http://localhost:8000/delete-admin?username=" + encodeURIComponent(username),{
        method: 'DELETE',
        credentials: 'include'
    });
    if (response.ok) {
        alert("Admin user deleted successfully");
        document.getElementById("deletedAdminUsername").value = "";
    } else {
        const errorData = await response.json();
        alert("Error deleting admin user: " + errorData.detail);
    }
    console.log(response);
});

document.getElementById("logout").addEventListener('click', async function() {
    const response = await fetch("http://localhost:8000/logout",{
        method: 'POST',
        credentials: 'include'
    });
    if (response.ok) {
        window.location.href = 'login.html';
    } else {
        alert("Error during logout");
    }
});