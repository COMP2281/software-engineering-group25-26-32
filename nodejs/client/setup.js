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
    }
    if (indexFile){
        formData.append("indexFile", indexFile);
    }
    if (idsFile){
        formData.append("idsFile", idsFile);
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
