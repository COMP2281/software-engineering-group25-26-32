// On load, add the file names to the dropdown menu
async function loadFiles() {
    const res = await fetch("http://localhost:8000/downloadableFiles", {
        method: 'GET',
        credentials: 'include'
    });

    const data = await res.json();
    console.log(data.files);
    
    const selector = document.getElementById("fileList");
    selector.innerHTML = ""; // Reset options

    for (const file of data.files) {
        const option = document.createElement("option");
        option.value = file;
        if (file.includes("/")) {
            fileName = file.split("/").slice(-1)[0]; // Get just the file name, not the path
        } else if (file.includes("\\")) {
            fileName = file.split("\\").slice(-1)[0]; // Handle Windows paths
        } else {
            fileName = file; // No path, just the file name
        }
        option.textContent = fileName;
        selector.appendChild(option);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadFiles();
});

// Download the selected file
document.getElementById("downloadFile").addEventListener('click', async function() {
    const select = document.getElementById("fileList");
    const fileName = select.value;


    var statusMess = document.getElementById("statusMessage");
    if (!fileName) {
        statusMess.innerHTML = "Please select a file to download.";
        statusMess.style.color = "red";
        return;
    }

    statusMess.innerHTML = "Downloading file, please wait...";
    statusMess.style.color = "blue";

    try {

        const response = await fetch(
            `http://localhost:8000/download/${encodeURIComponent(fileName)}`,
            { credentials: "include" }
        );

        if (response.ok) {

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);

            statusMess.innerHTML = "File downloaded successfully: " + fileName;
            statusMess.style.color = "green";

        } else {

            const errorData = await response.json();
            statusMess.innerHTML = "Error downloading file: " + errorData.detail;
            statusMess.style.color = "red";

        }

    } catch (err) {

        console.error(err);
        statusMess.innerHTML = "Download failed due to a network error.";
        statusMess.style.color = "red";

    }
});

// Delete the file instead WARNING: THIS IS VERY DANGEROUS
document.getElementById("deleteFile").addEventListener('click', async function() {
    const select = document.getElementById("fileList");
    const fileName = select.value;

    var statusMess = document.getElementById("statusMessage");
    if (!fileName) {
        statusMess.innerHTML = "Please select a file to delete.";
        statusMess.style.color = "red";
        return;
    }

    if (!confirm(`Are you sure you want to delete the file: ${fileName}? This action cannot be undone.`)) {
        return;
    }

    statusMess.innerHTML = "Deleting file, please wait...";
    statusMess.style.color = "blue";

    try {
        const response = await fetch(
            `http://localhost:8000/deleteFile/${encodeURIComponent(fileName)}`,
            { method: "DELETE", credentials: "include" }
        );

        if (response.ok) {
            const data = await response.json();
            statusMess.innerHTML = data.message;
            statusMess.style.color = "green";
            loadFiles(); // Refresh the file list after deletion
        } else {
            const errorData = await response.json();
            statusMess.innerHTML = "Error deleting file: " + errorData.detail;
            statusMess.style.color = "red";
        }

    } catch (err) {
        console.error(err);
        statusMess.innerHTML = "Deletion failed due to a network error.";
        statusMess.style.color = "red";
    }
});

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
        const responseData = await response.json();

        console.log(responseData);
        statusMess.innerHTML = responseData.message;
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
        const responseData = await response.json();
        statusMess.innerHTML = responseData.message;
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