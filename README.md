# Advanced Resume Shortlisting System (ATS)

This project is a full-stack web application designed to automate the initial screening of resumes. It utilizes Natural Language Processing (NLP) and a weighted scoring system to analyze PDF resumes, providing a more intelligent and nuanced shortlisting decision than simple keyword matching.

🔗 **Live Demo**: [https://resume-shortlisting-system.vercel.app](https://resume-shortlisting-system.vercel.app)

---

## 🚀 Features

- **PDF Resume Upload**: A clean web interface to upload candidate resumes in PDF format.  
- **NLP-Powered Analysis**: Extracts text and processes it using tokenization, lemmatization, and stop-word removal to accurately identify skills.  
- **Weighted Scoring System**: Assigns different levels of importance to various skills, allowing for a more realistic evaluation of a candidate's qualifications.  
- **Automated Shortlisting**: Compares the calculated score against a configurable threshold to automatically decide if a resume should be shortlisted.  
- **Candidate Profiling**: Performs conceptual clustering by grouping matched skills into dominant categories (e.g., "Data Science & AI", "Cloud & DevOps") to provide a quick overview of a candidate's strengths.  
- **Dynamic Results**: Presents the analysis, including the score, matched keywords, and dominant skill categories, directly on the web page.

---

## 🛠️ Tech Stack

### Backend:
- **Framework**: Flask  
- **PDF Parsing**: PyMuPDF  
- **NLP**: Natural Language Toolkit (NLTK)  
- **CORS**: Flask-CORS  

### Frontend:
- **HTML5**  
- **CSS3**  
- **Vanilla JavaScript** (for API calls)

---

## 🧠 System Architecture & Logic

The application follows a standard client-server architecture. The workflow is as follows:

### 1. File Upload (Frontend):
The user selects a PDF file via the `index.html` page. A JavaScript `fetch` event sends this file as a POST request to the backend `/shortlist` endpoint.

### 2. Text Extraction (Backend):
The Flask server receives the file and saves it temporarily. It then uses the PyMuPDF library to extract all raw text from the PDF document.

### 3. NLP & Scoring (Algorithm Core):
- The raw text is passed to the `advanced_shortlisting` function in `algorithms.py`.
- Inside this function, NLTK processes the text: it’s tokenized, stop words are removed, and each word is reduced to its root form (lemmatization).
- The algorithm iterates through a pre-defined dictionary of weighted keywords. It checks for multi-word phrases (e.g., “machine learning”) in the original text and single words in the processed (lemmatized) text.
- A final score is calculated by summing the weights of all matched keywords.

### 4. Decision & Profiling (Backend):
- The calculated score is returned to `app.py`, where it is compared against a `shortlisting_score_threshold` to make a shortlist decision.
- The matched keywords are also used to identify “Dominant Skill Categories” for candidate profiling.

### 5. Display Results (Frontend):
- The backend sends a JSON object containing the decision, score, matched skills, and skill categories back to the browser.
- JavaScript then dynamically renders this information on the page for the user to see.

---

## ⚙️ Setup and Installation

Follow these steps carefully to run the project locally. You will need **two terminals**.

### 🧾 Prerequisites
- Python 3.8+  
- pip (Python package installer)

---

### 1. Clone the Repository

```bash
git clone https://github.com/syedmehfooz47/resume-shortlisting-system.git
cd resume-shortlisting-system
````

---

### 2. Set Up the Backend (Terminal 1)

#### a. Create and Activate the Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate   # For PowerShell
```

Your terminal prompt should now start with `(.venv)`.

#### b. Install Required Packages

```powershell
pip install -r backend/requirements.txt
```

#### c. Download NLTK Data Models (One-Time Setup)

```powershell
python backend/setup_nltk.py
```

#### d. Run the Flask Server

```powershell
cd backend
python app.py
```

The server will now be running at:
📍 `http://127.0.0.1:5000`
(Keep this terminal open)

---

### 3. Set Up the Frontend (Terminal 2)

#### a. Open a New Terminal

#### b. Navigate to the Frontend Directory

```powershell
cd frontend
```

#### c. Serve the Frontend Files

```powershell
python -m http.server
```

This starts a simple server on port 8000.

---

### 4. Access the Application

Open your browser and go to:
🌐 `http://localhost:8000`

You can now upload resumes and view the analysis results.

---

## 👥 Author

* [Syed Mehfooz](https://github.com/syedmehfooz47)

---

## 📂 Repository

🔗 [GitHub Repository](https://github.com/syedmehfooz47/resume-shortlisting-system)

```
