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
3. One correct answer

Format each exactly like:
Q: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
Answer: [letter]

Content Excerpt:
{context}"""
    
    WRITTEN_TEMPLATE = """Generate exactly {num_questions} short-answer questions from this textbook excerpt.
Each question should require a paragraph-length response.

Format each exactly like:
Q: [question text]

Content Excerpt:
{context}"""