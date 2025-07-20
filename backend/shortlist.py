import json
import base64
import cgi
import io
import fitz  # PyMuPDF
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# --- Configuration: Keyword Weights ---
WEIGHTED_KEYWORDS = {
    'python': 3, 'java': 3, 'c#': 3, 'javascript': 3, 'typescript': 3, 'sql': 3,
    'react': 4, 'angular': 4, 'vue': 4, 'node.js': 4,
    'django': 4, 'flask': 4, 'spring boot': 4, '.net': 4, 'express.js': 4,
    'machine learning': 5, 'data science': 5, 'artificial intelligence': 5, 'ai': 5,
    'cloud': 5, 'aws': 5, 'azure': 5, 'gcp': 5, 'google cloud': 5,
    'docker': 5, 'kubernetes': 5, 'devops': 5, 'ci/cd': 5,
    'html': 2, 'css': 2, 'api': 2, 'restful': 2, 'git': 2,
    'nosql': 2, 'mongodb': 2, 'postgresql': 2, 'mysql': 2,
    'data analysis': 2, 'jenkins': 2,
    'agile': 1, 'scrum': 1, 'project management': 1,
    'communication': 1, 'problem solving': 1, 'graphql': 1
}

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


def advanced_shortlisting(text):
    """Analyzes resume text using NLP and weighted scoring."""
    text_lower = text.lower()
    tokens = word_tokenize(text_lower)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = {lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in stop_words}

    score = 0
    matched_keywords = set()

    for keyword, weight in WEIGHTED_KEYWORDS.items():
        if ' ' in keyword:
            if keyword in text_lower:
                score += weight
                matched_keywords.add(keyword)
        else:
            if lemmatizer.lemmatize(keyword) in lemmatized_tokens:
                score += weight
                matched_keywords.add(keyword)

    justification = f"Calculated score based on {len(matched_keywords)} matched skills."
    return score, sorted(list(matched_keywords)), justification


def handler(event, context):
    """
    Netlify Function handler for processing resume uploads.
    """
    try:
        if event['httpMethod'] != 'POST':
            return {'statusCode': 405, 'body': 'Method Not Allowed'}

        content_type = event['headers'].get('content-type', '')
        body_decoded = base64.b64decode(event['body'])
        fp = io.BytesIO(body_decoded)

        fs = cgi.FieldStorage(fp=fp, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type})
        file_item = fs['file']

        if not file_item.filename.lower().endswith('.pdf'):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Only PDF files are allowed.'})}

        pdf_bytes = file_item.file.read()

        text = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()

        shortlisting_score_threshold = 10
        score, matched_keywords, justification = advanced_shortlisting(text)
        is_shortlisted = score >= shortlisting_score_threshold
        result_message = f"Resume shortlisted ✅ (Score: {score}/{shortlisting_score_threshold}+)" if is_shortlisted else f"Resume not shortlisted ❌ (Score: {score}, Required: {shortlisting_score_threshold})"

        dominant_skill_categories = []
        if matched_keywords:
            skill_group_counts = {group: 0 for group in CONCEPTUAL_SKILL_GROUPS}
            for kw in matched_keywords:
                for group, skills in CONCEPTUAL_SKILL_GROUPS.items():
                    if kw in skills:
                        skill_group_counts[group] += 1
            max_count = max(skill_group_counts.values()) if any(skill_group_counts.values()) else 0
            if max_count > 0:
                dominant_skill_categories = sorted([g for g, c in skill_group_counts.items() if c == max_count])

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                "message": result_message,
                "score": score,
                "shortlisting_threshold": shortlisting_score_threshold,
                "justification": justification,
                "keywords": matched_keywords,
                "dominant_skill_categories": dominant_skill_categories
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'An unexpected server error occurred: {str(e)}'})
        }