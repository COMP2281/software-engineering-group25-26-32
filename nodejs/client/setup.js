document.getElementById("uploadForm").addEventListener('submit', async function(e) {
    document.getElementById("message").textContent = ""; // Clear previous messages
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    const indexFileInput = document.getElementById("indexFileInput");
    const indexFile = indexFileInput.files[0];
    const idsFileInput = document.getElementById("idsFileInput");
    const idsFile = idsFileInput.files[0];
    console.log(file, indexFile, idsFile);
    const formData = new FormData();
    if (file){
        if (!(file.name.endsWith(".db") || file.name.endsWith(".csv"))) {
            document.getElementById("message").textContent = "Please select a valid DB or CSV file (.db/.csv).";
            return;
        }
        formData.append("file", file);
    } else{
        if (!indexFile && !idsFile) {
            document.getElementById("message").textContent = "Please select at least one file to upload.";
            return;
        }
        
    }
    if (indexFile){
        formData.append("indexFile", indexFile);
        if (!(indexFile.name.endsWith(".index"))) {
            document.getElementById("message").textContent = "Please select a valid index file (.index).";
            return;
        }
    }else{
        if (!file && !idsFile) {
            document.getElementById("message").textContent = "Please select at least one file to upload.";
            return;
        }
    }
    if (idsFile){
        formData.append("idsFile", idsFile);
        if (!(idsFile.name.endsWith(".npy"))) {
            document.getElementById("message").textContent = "Please select a valid IDs file (.npy).";
            return;
        }
    }else{
        if (!file && !indexFile) {
            document.getElementById("message").textContent = "Please select at least one file to upload.";
            return;
        }
    }
    document.getElementById("uploadBtn").disabled = true;
    const response = await fetch("http://localhost:8000/upload", {
        method: 'POST',
        credentials: 'include',
        body: formData
    });
    document.getElementById("uploadBtn").disabled = false;
    if (response.ok) {
        document.getElementById("message").textContent = "File uploaded successfully!";
        document.getElementById("uploadForm").reset();
    } else {
        document.getElementById("message").textContent = "Failed to upload file.";
    }
});
