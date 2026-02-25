document.getElementById("uploadForm").addEventListener('submit', async function(e) {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file to upload.");
        return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("titleField", document.getElementById("titleField").value);
    formData.append("authorField", document.getElementById("authorField").value);
    formData.append("yearField", document.getElementById("yearField").value);
    formData.append("deptField", document.getElementById("deptField").value);
    formData.append("keywordsField", document.getElementById("keywordsField").value);
    formData.append("abstractField", document.getElementById("abstractField").value);
    formData.append("pdfUrlField", document.getElementById("pdfUrlField").value);
    formData.append("urlField", document.getElementById("urlField").value);
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
