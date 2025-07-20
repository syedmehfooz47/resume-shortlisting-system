import os
import fitz  # PyMuPDF
import werkzeug.utils
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from algorithms import advanced_shortlisting, WEIGHTED_KEYWORDS  # <-- IMPORT the new function

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Conceptual groups for profiling remain useful for the final output
CONCEPTUAL_SKILL_GROUPS = {
    'Programming Languages': ['python', 'java', 'c#', 'javascript', 'typescript'],
    'Web Frameworks & Libraries': ['django', 'flask', 'spring boot', '.net', 'express.js', 'react', 'angular', 'vue',
                                   'node.js'],
    'Web Technologies': ['html', 'css', 'api', 'restful', 'graphql'],
    'Databases': ['sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
    'Data Science & AI': ['machine learning', 'data analysis', 'data science', 'artificial intelligence', 'ai'],
    'Cloud & DevOps': ['cloud', 'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'ci/cd', 'jenkins',
                       'git', 'devops'],
    'Methodologies & Soft Skills': ['agile', 'scrum', 'project management', 'communication', 'problem solving']
}


@app.route('/shortlist', methods=['POST'])
def shortlist_resumes():
    filepath = None
    original_filename_for_logging = "N/A"

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request.'}), 400

        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected for upload.'}), 400

        original_filename_for_logging = file.filename
        filename = werkzeug.utils.secure_filename(original_filename_for_logging)

        if not filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        app.logger.info(f"File '{filename}' saved to '{filepath}'")

        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()

        app.logger.info(f"Extracted {len(text)} characters from '{filename}'.")

        # --- Use the advanced algorithm from algorithms.py ---
        shortlisting_score_threshold = 10  # Configurable score threshold
        score, matched_keywords, justification = advanced_shortlisting(text)

        is_shortlisted = score >= shortlisting_score_threshold
        result_message = (
            f"Resume '{original_filename_for_logging}' shortlisted ✅ (Score: {score}/{shortlisting_score_threshold}+)" if is_shortlisted
            else f"Resume '{original_filename_for_logging}' not shortlisted ❌ (Score: {score}, Required: {shortlisting_score_threshold})")
        app.logger.info(f"Shortlisting result for '{filename}': {result_message}")

        # --- Profiling based on matched keywords (Conceptual Clustering) ---
        dominant_skill_categories = []
        if matched_keywords:
            skill_group_counts = {group: 0 for group in CONCEPTUAL_SKILL_GROUPS}
            for kw in matched_keywords:
                for group, skills in CONCEPTUAL_SKILL_GROUPS.items():
                    if kw in skills:
                        skill_group_counts[group] += 1

            max_count = 0
            if any(skill_group_counts.values()):
                max_count = max(skill_group_counts.values())

            if max_count > 0:
                dominant_skill_categories = sorted([
                    group for group, count in skill_group_counts.items() if count == max_count
                ])

        app.logger.info(f"Identified dominant skill categories: {dominant_skill_categories}")

        return jsonify({
            "message": result_message,
            "score": score,
            "shortlisting_threshold": shortlisting_score_threshold,
            "justification": justification,
            "keywords": matched_keywords,
            "dominant_skill_categories": dominant_skill_categories
        }), 200

    except Exception as e:
        app.logger.error(f"An unexpected error occurred. File: '{original_filename_for_logging}'. Error: {str(e)}",
                         exc_info=True)
        return jsonify({'error': 'An unexpected server error occurred.'}), 500
    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            app.logger.info(f"Cleaned up file: '{filepath}'")


@app.route('/')
def home():
    return "✅ ATS Resume Shortlisting Backend is Running. (Advanced NLP Version)"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)