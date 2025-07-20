document.addEventListener('DOMContentLoaded', () => {
    console.log("Resume System: DOM fully loaded and parsed.");

    const uploadButton = document.getElementById("uploadButton");
    const fileInput = document.getElementById("resumeFile");
    const resultDiv = document.getElementById("result");

    if (!uploadButton) {
        console.error("CRITICAL ERROR: Upload button ('uploadButton') not found in HTML!");
        if (resultDiv) resultDiv.innerHTML = '<h3 class="status-heading error">Page Error: Upload button element is missing.</h3>';
        return;
    }
    if (!fileInput) {
        console.error("CRITICAL ERROR: File input ('resumeFile') not found in HTML!");
        if (resultDiv) resultDiv.innerHTML = '<h3 class="status-heading error">Page Error: File input element is missing.</h3>';
        return;
    }
    if (!resultDiv) {
        // If resultDiv itself is missing, we can only log to console.
        console.error("CRITICAL ERROR: Result div ('result') not found in HTML! Cannot display messages on page.");
        return;
    }

    uploadButton.addEventListener("click", function(event) {
        console.log("Event: 'Upload & Shortlist' button clicked.");
        event.preventDefault(); // Stop any default button action (like form submission)
        console.log("Action: event.preventDefault() called.");

        uploadButton.disabled = true; // Disable button to prevent multiple clicks
        resultDiv.innerHTML = '<h3 class="status-heading processing">Processing your resume, please wait...</h3>';
        console.log("UI Update: 'Processing...' message shown.");

        const file = fileInput.files[0];

        if (!file) {
            console.warn("Validation: No file selected by the user.");
            resultDiv.innerHTML = '<h3 class="status-heading error">⚠️ Please select a PDF resume file first.</h3>';
            fileInput.value = ""; // Clear any lingering selection state
            uploadButton.disabled = false;
            return;
        }

        console.log(`File Selected: Name: '${file.name}', Type: '${file.type}', Size: ${file.size} bytes.`);

        if (file.type !== "application/pdf") {
            console.warn(`Validation: Invalid file type selected: '${file.type}'. Expected 'application/pdf'.`);
            resultDiv.innerHTML = '<h3 class="status-heading error">⚠️ Invalid File Type: Please select a PDF file only.</h3>';
            fileInput.value = ""; // Clear the invalid file selection
            uploadButton.disabled = false;
            return;
        }

        const formData = new FormData();
        formData.append("file", file); // The backend expects the file under the key 'file'
        console.log("Network: FormData prepared. Initiating fetch request to '/shortlist'.");

        fetch("http://127.0.0.1:5000/shortlist", { // Ensure your Flask server is running at this address
            method: "POST",
            body: formData,
        })
        .then(response => {
            console.log(`Network Response: Received response. Status: ${response.status} ${response.statusText}.`);
            if (!response.ok) {
                // If HTTP status is not OK (e.g., 400, 500), try to parse error from server
                return response.json() // Attempt to parse a JSON error structure from the server
                    .then(errJson => {
                        console.error("Network Response: Server returned JSON error payload:", errJson);
                        throw new Error(errJson.error || `Server Error ${response.status}: ${response.statusText}. Check server logs.`);
                    })
                    .catch(() => { // If parsing JSON error fails, response body might not be JSON
                        return response.text().then(text => {
                            console.error(`Network Response: Server returned non-JSON error text (Status ${response.status}):`, text.substring(0, 500));
                            throw new Error(`Server Error ${response.status}: ${response.statusText}. Response: ${text.substring(0, 100)}...`);
                        });
                    });
            }
            console.log("Network Response: Status OK. Attempting to parse response as JSON...");
            return response.json(); // This can also throw an error if the response body is not valid JSON
        })
        .then(data => {
            console.log("Data Handling: Successfully parsed JSON data from server response:", data);

            // Defensive check: if server sent 200 OK but with an 'error' field in JSON
            if (data.error) {
                console.error("Data Handling: Server response was OK, but contained an error message:", data.error);
                resultDiv.innerHTML = `<h3 class="status-heading error">❌ Application Error: ${data.error}</h3>`;
                return; // Stop further processing for this case
            }

            // Build the HTML output based on the received data
            let statusClass = data.message && data.message.includes("shortlisted ✅") ? 'success' : 'error';
            let htmlOutput = `<h3 class="status-heading ${statusClass}">${data.message || "Processing Complete."}</h3>`;
            htmlOutput += `<div class="details">`;

            if (data.keywords && data.keywords.length > 0) {
                htmlOutput += `<strong>Matched Skills (${data.keywords.length}):</strong>
                               <ul>${data.keywords.map(skill => `<li>${skill}</li>`).join("")}</ul>`;
            } else {
                // This message is shown if no keywords are matched, regardless of shortlisting status.
                // The H3 above already indicates if it was "not shortlisted".
                htmlOutput += `<p>No skills from our predefined list were found in this resume.</p>`;
            }

            if (data.dominant_skill_categories && data.dominant_skill_categories.length > 0) {
                htmlOutput += `<strong>Potential Dominant Skill Categories:</strong>
                               <ul>${data.dominant_skill_categories.map(category => `<li>${category}</li>`).join("")}</ul>`;
            } else if (data.keywords && data.keywords.length > 0) {
                // Only show this if keywords were found, but no dominant categories were determined
                 htmlOutput += `<p>Could not determine dominant skill categories from the matched skills.</p>`;
            }
            htmlOutput += `</div>`; // Close .details div

            resultDiv.innerHTML = htmlOutput;
            console.log("UI Update: resultDiv updated with final HTML content derived from server data.");
            // For easier debugging, log the actual HTML that was set:
            // console.log("--- BEGIN resultDiv.innerHTML ---");
            // console.log(resultDiv.innerHTML);
            // console.log("--- END resultDiv.innerHTML ---");
        })
        .catch(error => {
            // This .catch() handles errors from the fetch operation itself (network down),
            // errors thrown from the !response.ok block (server errors),
            // errors from response.json() if parsing fails (malformed JSON from server),
            // and any JavaScript errors within the .then(data => {...}) block.
            console.error("Critical Error in Fetch/Promise Chain:", error);
            resultDiv.innerHTML = `<h3 class="status-heading error">❌ An Error Occurred:</h3>
                                   <div class="details"><p>${error.message}</p>
                                   <p>Please open your browser's Developer Console (F12, then click 'Console') for more technical details.</p></div>`;
            console.log("UI Update: resultDiv updated with error message due to promise rejection or JS error.");
        })
        .finally(() => {
            uploadButton.disabled = false; // Re-enable the button in all cases (success or error)
            fileInput.value = "";          // Clear the file input so the same file can be re-selected if needed
            console.log("Cleanup: Upload process finished. Button re-enabled, file input cleared.");
        });
    });
    console.log("Resume System: Event listener for 'uploadButton' attached successfully.");
});

console.log("Resume System: script.js loaded and initial checks complete.");