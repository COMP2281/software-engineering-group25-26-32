document.getElementById("uploadForm").addEventListener('submit', async function(e) {
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
        formData.append("file", file);
    } else{
        if (!indexFile && !idsFile) {
            alert("Please select at least one file to upload.");
            return;
        }
        if (!(file.name.endsWith(".db") || file.name.endsWith(".csv"))) {
            alert("Please select a valid DB or CSV file.");
            return;
        }
    }
    if (indexFile){
        formData.append("indexFile", indexFile);
        if (!file && !indexFile) {
            alert("Please select at least one file to upload.");
            return;
        }
        if (!(indexFile.name.endsWith(".index"))) {
            alert("Please select a valid index file (.index).");
            return;
        }
    }
    if (idsFile){
        formData.append("idsFile", idsFile);
        if (!file && !idsFile) {
            alert("Please select at least one file to upload.");
            return;
        }
        if (!(idsFile.name.endsWith(".npy"))) {
            alert("Please select a valid IDs file (.npy).");
            return;
        }
    }
    const response = await fetch("http://localhost:8000/upload", {
        method: 'POST',
        credentials: 'include',
        body: formData
    });
    if (response.ok) {
        alert("File uploaded successfully!");
        document.getElementById("uploadForm").reset();
    } else {
        alert("Failed to upload file.");
    }
});
