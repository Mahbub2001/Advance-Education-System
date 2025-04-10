import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = "learnbuddy"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Configuration (using OpenAI as example)
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # LLM_MODEL = "gpt-3.5-turbo"
    
    DATA_FOLDER = "./data"
    OUTPUT_FOLDER = "./output"
    
    DEFAULT_NUM_QUESTIONS = 5
    MCQ_TEMPLATE = """
    Generate {num_questions} multiple-choice questions based on the context.
    Each question should have 4 options with one correct answer.
    Format each question as follows:
    Q: [question text]
    A) [option 1]
    B) [option 2]
    C) [option 3]
    D) [option 4]
    Answer: [correct option letter]
    
    Context:
    {context}
    """
    
    WRITTEN_TEMPLATE = """
    Generate {num_questions} written answer questions based on the context.
    Format each question as follows:
    Q: [question text]
    
    Context:
    {context}
    """