const apiUrl = "https://kba-project.onrender.com";

async function uploadDocuments() {
    const files = document.getElementById("files").files;
    const formData = new FormData();

    for (let file of files) {
        formData.append("files", file);
    }

    try {
        const response = await fetch(`${apiUrl}/upload/`, {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        alert(result.message);
        fetchDocuments(); // Refresh de lijst met documenten
    } catch (error) {
        console.error("Fout bij uploaden:", error);
    }
}

async function deleteDocument() {
    const filename = document.getElementById("filename").value;
    const formData = new FormData();
    formData.append("filename", filename);

    try {
        const response = await fetch(`${apiUrl}/documents/`, {
            method: "DELETE",
            body: formData,
        });
        const result = await response.json();
        alert(result.message);
        fetchDocuments(); // Refresh de lijst met documenten
    } catch (error) {
        console.error("Fout bij verwijderen:", error);
    }
}

async function fetchDocuments() {
    try {
        const response = await fetch(`${apiUrl}/documents/`);
        const result = await response.json();

        const documentsList = document.getElementById("documents");
        documentsList.innerHTML = "";

        result.documents.forEach((doc) => {
            const li = document.createElement("li");
            li.textContent = doc.name;
            documentsList.appendChild(li);
        });
    } catch (error) {
        console.error("Fout bij ophalen documenten:", error);
    }
}

// Haal documenten op zodra de pagina laadt
document.addEventListener("DOMContentLoaded", fetchDocuments);
