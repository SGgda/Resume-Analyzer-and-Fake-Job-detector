import operator
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# --- Load the spaCy Model ---
# This loads the large English model. It might take a moment the first time.
try:
    nlp = spacy.load('en_core_web_lg')
except OSError:
    print("Downloading 'en_core_web_lg' model from spaCy...")
    spacy.cli.download('en_core_web_lg')
    nlp = spacy.load('en_core_web_lg')
    
# --- NLTK Setup for Lemmatization ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# --- SKILL DATABASE ---
# A comprehensive list of skills. This can be expanded.
SKILLS_DB = [
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'html', 'css', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
    'react', 'angular', 'vue', 'node.js', 'express.js', 'django', 'flask', 'spring', 'ruby on rails', '.net', 'next.js',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'firebase', 'dynamodb', 'oracle', 'sqlite', 'cassandra',
    'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'heroku', 'digitalocean', 'terraform', 'ansible',
    'git', 'github', 'gitlab', 'jira', 'jenkins', 'ci/cd',
    'machine learning', 'artificial intelligence', 'ai', 'ml', 'deep learning', 'data science', 'nlp', 'natural language processing',
    'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'pandas', 'numpy', 'matplotlib', 'seaborn',
    'rest', 'api', 'graphql', 'microservices',
    'agile', 'scrum', 'testing', 'automation', 'selenium', 'jest', 'mocha', 'chai',
    'linux', 'bash', 'scripting',
    'tailwind css', 'bootstrap', 'sass', 'less', 'material-ui',
    'typescript', 'axios'
]

# --- spaCy Skill Extraction ---
def extract_skills(text):
    """Extracts skills from text using spaCy's matcher."""
    doc = nlp(text.lower())
    matcher = spacy.matcher.Matcher(nlp.vocab)
    
    # Create patterns for each skill in our database
    for skill in SKILLS_DB:
        pattern = [{'LOWER': term} for term in skill.split()]
        matcher.add(skill, [pattern])
        
    matches = matcher(doc)
    
    # Extract the matched text and normalize it
    found_skills = set()
    for match_id, start, end in matches:
        skill_text = doc[start:end].text
        found_skills.add(skill_text)
        
    return found_skills

# --- NLTK Lemmatization Tokenizer ---
class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

# --- Main Ranking Function ---
def rank_resumes(job_description, resumes_data):
    if not job_description or not resumes_data:
        return []

    resume_filenames = list(resumes_data.keys())
    resume_texts = list(resumes_data.values())

    # --- 1. Calculate Context Score (TF-IDF) ---
    vectorizer = TfidfVectorizer(stop_words='english', tokenizer=LemmaTokenizer())
    vectorizer.fit([job_description])
    jd_vector = vectorizer.transform([job_description])
    resumes_vectors = vectorizer.transform(resume_texts)
    context_scores = cosine_similarity(jd_vector, resumes_vectors)[0]

    # --- 2. Calculate Skill Score (spaCy) ---
    required_skills = extract_skills(job_description)
    if not required_skills: # Handle case where no skills are found in JD
        return [] 
        
    skill_scores = []
    for resume_text in resume_texts:
        candidate_skills = extract_skills(resume_text)
        matched_skills = required_skills.intersection(candidate_skills)
        
        # Calculate score as the ratio of matched skills to required skills
        score = len(matched_skills) / len(required_skills) if required_skills else 0
        skill_scores.append(score)

    # --- 3. Combine Scores into a Hybrid Score ---
    hybrid_scores = []
    for i in range(len(context_scores)):
        context_score = context_scores[i]
        skill_score = skill_scores[i]
        
        # Weighted average: 60% skill match, 40% context match
        final_score = (0.6 * skill_score) + (0.4 * context_score)
        hybrid_scores.append(final_score)

    # --- 4. Rank based on the Hybrid Score ---
    resume_scores = {resume_filenames[i]: hybrid_scores[i] for i in range(len(hybrid_scores))}
    sorted_resumes = sorted(resume_scores.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_resumes