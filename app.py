from retrieve_book import ChapterRetriever
from question_generator import QuestionGenerator
from config import Config
import json
import os
import logging
from time import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=== Optimized Question Generation System ===")
    print(f"Max chunk size: {Config.MAX_CHUNK_TOKENS} tokens")
    print(f"Max parallel chunks: {Config.MAX_WORKERS}\n")
    
    retriever = ChapterRetriever()
    generator = QuestionGenerator()
    
    book_title = input("Enter book title: ").strip()
    chapter_num = input("Enter chapter number: ").strip()
    question_type = input("Question type (mcq/written): ").lower().strip()
    num_questions = int(input(f"Number of questions (default {Config.DEFAULT_NUM_QUESTIONS}): ") or Config.DEFAULT_NUM_QUESTIONS)
    
    try:
        start_time = time()
        
        logger.info(f"Retrieving content for {book_title}, Chapter {chapter_num}...")
        chapter_content = retriever.get_full_chapter(book_title, chapter_num)
        
        if not chapter_content:
            logger.error("No content found for this chapter")
            return
            
        content_size = len(chapter_content.split())
        logger.info(f"Processing {content_size} words of chapter content...")
        
        logger.info(f"Generating {num_questions} {question_type} questions...")
        questions = generator.generate_questions(
            context=chapter_content,
            question_type=question_type,
            num_questions=num_questions
        )
        
        output_file = f"{book_title}_chapter_{chapter_num}_{question_type}.json"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_file)
        
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(questions, f, indent=2)
        
        elapsed = time() - start_time
        print(f"\nSuccessfully generated {len(questions)} questions in {elapsed:.2f} seconds!")
        print(f"Saved to: {output_path}")
        
        print("\nSample questions:")
        for i, q in enumerate(questions[:3], 1):
            print(f"\n{i}. {q['question']}")
            if q['type'] == 'mcq':
                for opt in q['options']:
                    print(f"   - {opt}")
                print(f"   Answer: {q['answer']}")
                print(f"   Explanation: {q.get('explanation', 'No explanation provided')}")
            else:
                print(f"   Sample Solution: {q.get('solution', 'No solution provided')}")
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()