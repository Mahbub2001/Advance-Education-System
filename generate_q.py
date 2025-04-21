from retrieve_book import ChapterRetriever
from question_generator import QuestionGenerator
from config import Config
import json
import os
import logging
from time import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionGeneratorApp:
    def __init__(self):
        self.retriever = ChapterRetriever()
        self.generator = QuestionGenerator()
    
    def generate_questions(self, book_title: str, chapter_num: str, question_type: str, 
                         num_questions: int = Config.DEFAULT_NUM_QUESTIONS,
                         weaknesses: list = None, strengths: list = None) -> dict:
        """
        Generate questions based on the given parameters
        
        Args:
            book_title: Title of the book
            chapter_num: Chapter number
            question_type: 'mcq' or 'written'
            num_questions: Number of questions to generate
            weaknesses: List of student weaknesses to target
            strengths: List of student strengths to avoid
            
        Returns:
            Dictionary containing:
            - questions: List of generated questions
            - output_path: Path where questions were saved
            - time_taken: Time taken in seconds
        """
        result = {
            'questions': [],
            'output_path': None,
            'time_taken': 0,
            'success': False,
            'error': None
        }
        
        try:
            start_time = time()
            
            logger.info(f"Retrieving content for {book_title}, Chapter {chapter_num}...")
            chapter_content = self.retriever.get_full_chapter(book_title, chapter_num)
            
            if not chapter_content:
                raise ValueError("No content found for this chapter")
                
            content_size = len(chapter_content.split())
            logger.info(f"Processing {content_size} words of chapter content...")
            
            logger.info(f"Generating {num_questions} {question_type} questions...")
            questions = self.generator.generate_questions(
                context=chapter_content,
                question_type=question_type,
                num_questions=num_questions,
                weaknesses=weaknesses,
                strengths=strengths
            )
            
            # Create output filename
            output_file = f"{book_title}_chapter_{chapter_num}_{question_type}"
            if weaknesses or strengths:
                output_file += "_personalized"
            output_file += ".json"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_file)
            
            os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(questions, f, indent=2)
            
            elapsed = time() - start_time
            logger.info(f"Successfully generated {len(questions)} questions in {elapsed:.2f} seconds")
            
            result.update({
                'questions': questions,
                'output_path': output_path,
                'time_taken': elapsed,
                'success': True
            })
            
        except Exception as e:
            logger.error(f"Error in question generation: {str(e)}")
            result['error'] = str(e)
            
        return result
    
    def print_sample_questions(self, questions: list, num_samples: int = 3):
        """Print sample questions from the generated list"""
        print("\nSample questions:")
        for i, q in enumerate(questions[:], 1):
            print(f"\n{i}. {q['question']}")
            if q['type'] == 'mcq':
                for opt in q['options']:
                    print(f"   - {opt}")
                print(f"   Answer: {q['answer']}")
                print(f"   Explanation: {q.get('explanation', 'No explanation provided')}")
            else:
                print(f"   Sample Solution: {q.get('solution', 'No solution provided')}")


# Example usage
app = QuestionGeneratorApp()

# # Example 1: Basic MCQ generation
# basic_result = app.generate_questions(
#     book_title="chemistry9_10",
#     chapter_num="Eight",
#     question_type="mcq",
#     num_questions=5
# )

# if basic_result['success']:
#     app.print_sample_questions(basic_result['questions'])
#     print(f"\nQuestions saved to: {basic_result['output_path']}")
# else:
#     print(f"Error: {basic_result['error']}")

# Example 2: Personalized written questions
personalized_result = app.generate_questions(
    book_title="chemistry9_10",
    chapter_num="Eight",
    question_type="written",
    num_questions=3,
    weaknesses=[
        "Lacks specific details about the number of divisions and cells produced",
        "Missing specific terminology which is crucial for a complete understanding"
    ],
    strengths=[
        "Understanding of basic concepts",
        "Good at memorizing processes"
    ]
)

if personalized_result['success']:
    app.print_sample_questions(personalized_result['questions'])
    print(f"\nPersonalized questions saved to: {personalized_result['output_path']}")
else:
    print(f"Error: {personalized_result['error']}")
    
    