from embeddings_manager import EmbeddingsManager
from question_generator import QuestionGenerator
from config import Config
import json
import os

def ensure_output_folder():
    if not os.path.exists(Config.OUTPUT_FOLDER):
        os.makedirs(Config.OUTPUT_FOLDER)

def generate_questions():
    print("Question Generation")
    print("------------------")
    
    embeddings_manager = EmbeddingsManager()
    question_generator = QuestionGenerator()
    
    available_books = set()
    results = embeddings_manager.index.query(
        vector=[0]*384,
        top_k=1,
        include_metadata=True
    )
    if results['matches']:
        available_books.add(results['matches'][0]['metadata']['book'])
    
    if not available_books:
        print("No books found in Pinecone. Run ingest.py first.")
        return
    
    print("\nAvailable books:")
    for i, book in enumerate(available_books, 1):
        print(f"{i}. {book}")
    
    book_title = input("\nEnter book title (or leave blank for any): ").strip()
    if book_title and book_title not in available_books:
        print("Book not found in Pinecone")
        return
    
    chapters = embeddings_manager.list_available_chapters(book_title)
    if not chapters:
        print("No chapters found for this book")
        return
    
    print("\nAvailable chapters:")
    for i, chap in enumerate(chapters, 1):
        print(f"{i}. {chap}")
    
    chapter_name = input("\nEnter chapter name/number: ").strip()
    if chapter_name not in chapters:
        print("Chapter not found")
        return
    
    question_type = input("Question type (mcq/written): ").strip().lower()
    if question_type not in ['mcq', 'written']:
        print("Invalid question type")
        return
    
    try:
        num_questions = int(input(f"Number of questions (default {Config.DEFAULT_NUM_QUESTIONS}): ") or Config.DEFAULT_NUM_QUESTIONS)
    except ValueError:
        num_questions = Config.DEFAULT_NUM_QUESTIONS
    
    # Generate questions
    # chapter_content = embeddings_manager.retrieve_chapter_content(
    #     chapter_name, 
    #     book_title if book_title else None,
    #     top_k=min(20, num_questions * 3)
    # )
    
    if question_type == 'mcq':
        questions = question_generator.generate_mcq_questions(chapter_content, num_questions)
    else:
        questions = question_generator.generate_written_questions(chapter_content, num_questions)
    
    # Save and display results
    ensure_output_folder()
    safe_chapter_name = "".join(c if c.isalnum() else "_" for c in chapter_name)
    output_filename = f"{safe_chapter_name}_{question_type}_questions.json"
    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
    
    with open(output_path, 'w') as f:
        json.dump(questions, f, indent=2)
    
    print(f"\nGenerated {len(questions)} questions saved to {output_path}")
    print("\nSample questions:")
    for i, q in enumerate(questions[:3], 1):
        if question_type == 'mcq':
            print(f"\n{i}. {q['question']}")
            for opt in q['options']:
                print(f"   {opt}")
            print(f"   Answer: {q['answer']}")
        else:
            print(f"{i}. {q['question']}")

if __name__ == "__main__":
    generate_questions()