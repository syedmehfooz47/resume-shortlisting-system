import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# --- Configuration: Keyword Weights ---
# Assign higher weights to more critical or specialized skills.
WEIGHTED_KEYWORDS = {
    # Core Programming & Languages (Weight: 3)
    'python': 3, 'java': 3, 'c#': 3, 'javascript': 3, 'typescript': 3, 'sql': 3,

    # High-Value Frameworks & Libraries (Weight: 4)
    'react': 4, 'angular': 4, 'vue': 4, 'node.js': 4,
    'django': 4, 'flask': 4, 'spring boot': 4, '.net': 4, 'express.js': 4,

    # Specialized & High-Demand Fields (Weight: 5)
    'machine learning': 5, 'data science': 5, 'artificial intelligence': 5, 'ai': 5,
    'cloud': 5, 'aws': 5, 'azure': 5, 'gcp': 5, 'google cloud': 5,
    'docker': 5, 'kubernetes': 5, 'devops': 5, 'ci/cd': 5,

    # Foundational & General Skills (Weight: 2)
    'html': 2, 'css': 2, 'api': 2, 'restful': 2, 'git': 2,
    'nosql': 2, 'mongodb': 2, 'postgresql': 2, 'mysql': 2,
    'data analysis': 2, 'jenkins': 2,

    # Soft Skills & Methodologies (Weight: 1)
    'agile': 1, 'scrum': 1, 'project management': 1,
    'communication': 1, 'problem solving': 1, 'graphql': 1
}


def advanced_shortlisting(text):
    """
    Analyzes resume text using NLP techniques and a weighted scoring system.

    Args:
        text (str): The text content of the resume.

    Returns:
        tuple: A tuple containing the total score (int), a sorted list of matched
               keywords (list), and a justification string (str).
    """
    if not text:
        return 0, [], "No text was extracted from the resume."

    # --- 1. NLP Preprocessing ---
    text_lower = text.lower()
    tokens = word_tokenize(text_lower)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # Lemmatize tokens, excluding stop words and short non-alphabetic tokens
    lemmatized_tokens = {lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in stop_words}

    # --- 2. Weighted Keyword Matching & Scoring ---
    score = 0
    matched_keywords = set()

    for keyword, weight in WEIGHTED_KEYWORDS.items():
        # Check for multi-word keywords (phrases) in the original text
        if ' ' in keyword:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                score += weight
                matched_keywords.add(keyword)
        # Check for single-word keywords in the lemmatized tokens
        else:
            if lemmatizer.lemmatize(keyword) in lemmatized_tokens:
                score += weight
                matched_keywords.add(keyword)

    # --- 3. Result Justification ---
    justification = f"Calculated score based on {len(matched_keywords)} matched skills. "
    if not matched_keywords:
        justification += "No relevant skills from our list were found."

    return score, sorted(list(matched_keywords)), justification