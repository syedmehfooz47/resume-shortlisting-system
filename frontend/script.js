document.addEventListener('DOMContentLoaded', () => {
    console.log("Resume System: DOM fully loaded and parsed.");

    const uploadButton = document.getElementById("uploadButton");
    const fileInput = document.getElementById("resumeFile");
    const resultDiv = document.getElementById("result");

    if (!uploadButton || !fileInput || !resultDiv) {
        console.error("CRITICAL ERROR: A required HTML element ('uploadButton', 'resumeFile', or 'result') was not found.");
        if (resultDiv) resultDiv.innerHTML = '<h3 class="status-heading error">Page Error: A required element is missing.</h3>';
        return;
    }

    uploadButton.addEventListener("click", function(event) {
        console.log("Event: 'Upload & Shortlist' button clicked.");
        event.preventDefault();

        uploadButton.disabled = true;
        resultDiv.innerHTML = '<h3 class="status-heading processing">Processing your resume, please wait...</h3>';
        console.log("UI Update: 'Processing...' message shown.");

        const file = fileInput.files[0];

        if (!file) {
            console.warn("Validation: No file selected.");
            resultDiv.innerHTML = '<h3 class="status-heading error">⚠️ Please select a PDF resume file first.</h3>';
            uploadButton.disabled = false;
            return;
        }

        if (file.type !== "application/pdf") {
            console.warn(`Validation: Invalid file type: '${file.type}'.`);
            resultDiv.innerHTML = '<h3 class="status-heading error">⚠️ Invalid File Type: Please select a PDF file only.</h3>';
            uploadButton.disabled = false;
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        console.log("Network: FormData prepared. Initiating fetch request to Netlify Function.");

        fetch("/.netlify/functions/shortlist", {
            method: "POST",
            body: formData,
        })
        .then(response => {
            console.log(`Network Response: Status: ${response.status} ${response.statusText}.`);
            if (!response.ok) {
                return response.json().then(errJson => {
                    console.error("Network Response: Server returned JSON error:", errJson);
                    throw new Error(errJson.error || `Server Error ${response.status}.`);
                }).catch(() => {
                    throw new Error(`Server Error ${response.status}: ${response.statusText}.`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Data Handling: Successfully parsed JSON data:", data);

            if (data.error) {
                console.error("Data Handling: Server response contained an error message:", data.error);
                resultDiv.innerHTML = `<h3 class="status-heading error">❌ Application Error: ${data.error}</h3>`;
                return;
            }

            const isShortlisted = data.score >= data.shortlisting_threshold;
            let statusClass = isShortlisted ? 'success' : 'error';
            let htmlOutput = `<h3 class="status-heading ${statusClass}">${data.message || "Processing Complete."}</h3>`;

            htmlOutput += `<div class="details">`;

            if (data.score !== undefined) {
                 htmlOutput += `<p><strong>Score:</strong> ${data.score} (Threshold: ${data.shortlisting_threshold})</p>`;
            }
             if (data.justification) {
                 htmlOutput += `<p><em>${data.justification}</em></p>`;
             }

            if (data.keywords && data.keywords.length > 0) {
                htmlOutput += `<strong>Matched Skills (${data.keywords.length}):</strong>
                               <ul>${data.keywords.map(skill => `<li>${skill}</li>`).join("")}</ul>`;
            } else {
                htmlOutput += `<p>No skills from our predefined list were found in this resume.</p>`;
            }

            if (data.dominant_skill_categories && data.dominant_skill_categories.length > 0) {
                htmlOutput += `<strong>Potential Dominant Skill Categories:</strong>
                               <ul>${data.dominant_skill_categories.map(category => `<li>${category}</li>`).join("")}</ul>`;
            } else if (data.keywords && data.keywords.length > 0) {
                 htmlOutput += `<p>Could not determine dominant skill categories from the matched skills.</p>`;
            }

            htmlOutput += `</div>`;
            resultDiv.innerHTML = htmlOutput;
            console.log("UI Update: resultDiv updated with final content.");
        })
        .catch(error => {
            console.error("Critical Error in Fetch/Promise Chain:", error);
            resultDiv.innerHTML = `<h3 class="status-heading error">❌ An Error Occurred:</h3>
                                   <div class="details"><p>${error.message}</p>
                                   <p>Please check the browser's Developer Console (F12) for more details.</p></div>`;
        })
        .finally(() => {
            uploadButton.disabled = false;
            fileInput.value = "";
            console.log("Cleanup: Upload process finished. Button re-enabled, file input cleared.");
        });
    });
    console.log("Resume System: Event listener for 'uploadButton' attached successfully.");
});

console.log("Resume System: script.js loaded and initial checks complete.");