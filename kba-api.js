document.addEventListener("DOMContentLoaded", function () {
    // Selecteer het formulier en het resultaatgedeelte
    const form = document.getElementById("kbaForm");
    const resultDiv = document.getElementById("kbaResult");

    // Voeg een eventlistener toe aan het formulier
    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Voorkom standaardformuliergedrag

        // Haal de vraag op uit het formulier
        const vraag = document.getElementById("kbaVraag").value;

        // Verstuur de vraag naar de API
        try {
            const response = await fetch("https://kba-project.onrender.com/kba", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ vraag }), // Vraag als JSON
            });

            if (!response.ok) {
                throw new Error(`API fout: ${response.status}`);
            }

            // Parseer de respons en toon het antwoord
            const data = await response.json();
            resultDiv.innerHTML = `<p><strong>Antwoord:</strong> ${data.antwoord}</p>`;
        } catch (error) {
            // Toon een foutmelding
            resultDiv.innerHTML = `<p style="color: red;">Fout: ${error.message}</p>`;
        }
    });
});