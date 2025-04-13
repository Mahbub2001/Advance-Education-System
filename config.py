import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = "learnbuddy"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    LLM_MODEL = "deepseek/deepseek-r1-distill-llama-70b:free"
    SITE_URL = os.getenv("SITE_URL", "http://localhost")
    SITE_NAME = os.getenv("SITE_NAME", "LearnBuddy")
    
    DATA_FOLDER = "./data"
    OUTPUT_FOLDER = "./output"
    
    DEFAULT_NUM_QUESTIONS = 5
    MCQ_TEMPLATE = """Generate exactly {num_questions} multiple-choice questions from this textbook chapter.
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

    Chapter Content:
    {context}"""
        
    WRITTEN_TEMPLATE = """Generate exactly {num_questions} short-answer questions from this textbook chapter.
    Each question should require a paragraph-length response.

    Format each exactly like:
    Q: [question text]

    Chapter Content:
    {context}"""