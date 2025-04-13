import os
from dotenv import load_dotenv
import math

load_dotenv()

class Config:
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = "learnbuddy"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    LLM_MODEL = "deepseek/deepseek-r1-distill-llama-70b:free"
    SITE_URL = os.getenv("SITE_URL", "http://localhost")
    SITE_NAME = os.getenv("SITE_NAME", "LearnBuddy")
    
    # Content Handling Parameters
    MAX_CHUNK_TOKENS = 3000 
    MAX_CHUNKS = 10
    SINGLE_BATCH_THRESHOLD = 2000 
    QUESTIONS_PER_CHUNK = 3
    MAX_WORKERS = 4 
    CACHE_DIR = "./.chapter_cache"
    MAX_CONTEXT_WINDOW = 8000  
    SAFETY_MARGIN = 0.9 
    
    # Review System Parameters
    MAX_REVIEW_LENGTH = 10000 
    REVIEW_CACHE_DIR = "./.review_cache"
    REVIEW_WEIGHTS = {
        "content": 0.4,
        "structure": 0.3,
        "grammar": 0.2,
        "readability": 0.1
    }
    
    # Paths
    DATA_FOLDER = "./data"
    OUTPUT_FOLDER = "./output"
    
    # Defaults
    DEFAULT_NUM_QUESTIONS = 5
    
    # Templates
    MCQ_TEMPLATE = """Generate exactly {num_questions} multiple-choice questions from this textbook excerpt.
Each question must have:
1. A clear question stem
2. 4 plausible options (A-D)
3. One correct answer with a 1-2 line explanation

Format each exactly like:
Q: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Answer: [letter]
Explanation: [brief explanation]

Content Excerpt:
{context}"""

    WRITTEN_TEMPLATE = """Generate exactly {num_questions} short-answer questions from this textbook excerpt.
Each question should require a paragraph-length response and include a sample solution.

Format each exactly like:
Q: [question text]
Solution: [sample solution using textbook content and general knowledge]

Content Excerpt:
{context}"""

    # Templates
    CONTENT_REVIEW_TEMPLATE = """Analyze this {paper_type} for content quality. Evaluate:
1. Thesis clarity and focus
2. Argument strength and evidence
3. Originality of ideas
4. Depth of analysis
5. Relevance to subject

Provide specific feedback in this format:
Strengths:
- [Strength 1]
- [Strength 2]

Weaknesses:
- [Weakness 1]
- [Weakness 2]

Suggestions:
- [Suggestion 1]
- [Suggestion 2]

Score: [0-100]

Paper Content:
{content}"""

    STRUCTURE_REVIEW_TEMPLATE = """Evaluate this paper's structure:
1. Logical flow between paragraphs
2. Section organization
3. Introduction and conclusion effectiveness
4. Transition quality
5. Overall coherence

Provide feedback in this format:
Feedback:
- [General feedback]

Organization:
- [Org feedback 1]
- [Org feedback 2]

Flow:
- [Flow feedback 1]
- [Flow feedback 2]

Score: [0-100]

Paper Content:
{content}"""

    GRAMMAR_REVIEW_TEMPLATE = """Identify and correct all grammatical, punctuation, and style errors.
For each error, provide:
[Incorrect text] → [Corrected text]
[Explanation of error]

Example:
He go to school → He goes to school
(Subject-verb agreement error)

Content:
{content}"""