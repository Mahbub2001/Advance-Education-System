from openai import OpenAI
from typing import Dict, List, Optional
from config import Config
import re
import logging
from concurrent.futures import ThreadPoolExecutor
from diskcache import Cache
import textstat

class ExamPaperReviewer:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.logger = logging.getLogger(__name__)
        self.cache = Cache(Config.REVIEW_CACHE_DIR)
        
    def review_exam_paper(self, questions: List[Dict[str, str]]) -> Dict:
        """
        Review an exam paper containing questions and answers
        Each question should be a dict with:
        - 'question': The question text
        - 'model_answer': The ideal answer
        - 'student_answer': The student's response
        - 'marks': (optional) The maximum marks for this question
        """
        if not questions:
            raise ValueError("No questions provided for review")
            
        cache_key = f"exam_review_{hash(str(questions))}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            results = {
                "questions": [],
                "overall_score": 0,
                "feedback_summary": {
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": []
                }
            }
            
            total_score = 0
            total_possible = 0
            
            for i, q in enumerate(questions):
                question_result = self._review_question(
                    question=q.get('question', ''),
                    sample_solution=q.get('model_answer', ''),
                    user_solution=q.get('student_answer', ''),
                    max_marks=q.get('marks', 1)  
                )
                
                results["questions"].append(question_result)
                total_score += question_result["score"]
                total_possible += q.get('marks', 1)
                
                if i < 3:  
                    results["feedback_summary"]["strengths"].extend(
                        question_result["strengths"][:1]
                    )
                    results["feedback_summary"]["weaknesses"].extend(
                        question_result["weaknesses"][:1]
                    )
                    results["feedback_summary"]["suggestions"].extend(
                        question_result["suggestions"][:1]
                    )
            
            if total_possible > 0:
                results["overall_score"] = round((total_score / total_possible) * 100, 1)
            
            self.cache[cache_key] = results
            return results
            
        except Exception as e:
            self.logger.error(f"Exam paper review failed: {str(e)}")
            raise

    def _review_question(self, question: str, sample_solution: str, user_solution: str, max_marks: int = 1) -> Dict:
        """Review a single exam question and answer"""
        prompt = Config.EXAM_QUESTION_REVIEW_TEMPLATE.format(
            question=question,
            sample_solution=sample_solution,
            user_solution=user_solution
        )
        
        response = self._call_llm(prompt)
        return self._parse_question_response(response, max_marks)

    def _call_llm(self, prompt: str) -> str:
        """Make API call to LLM"""
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": Config.SITE_URL,
                    "X-Title": Config.SITE_NAME,
                },
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM API call failed: {str(e)}")
            raise

    @staticmethod
    def _parse_question_response(text: str, max_marks: int) -> Dict:
        """Parse the response for a single question review"""
        result = {
            "score": 0,
            "marks_awarded": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "detailed_feedback": text
        }
        score_match = re.search(r"Final Score:\s*(\d+)", text)
        if score_match:
            try:
                score_pct = min(100, max(0, int(score_match.group(1))))
                result["score"] = score_pct
                result["marks_awarded"] = round((score_pct / 100) * max_marks, 1)
            except:
                pass
        
        strengths_section = re.search(r"Strengths:\s*(.*?)(?=\n\s*\n|\Z)", text, re.DOTALL | re.IGNORECASE)
        if strengths_section:
            result["strengths"] = [
                s.strip() for s in strengths_section.group(1).split("\n") 
                if s.strip() and (s.strip().startswith('-') or s.strip().startswith('*'))
            ]
            result["strengths"] = [s.lstrip('-* ').strip() for s in result["strengths"]]
        
        weaknesses_section = re.search(r"Weaknesses:\s*(.*?)(?=\n\s*\n|\Z)", text, re.DOTALL | re.IGNORECASE)
        if weaknesses_section:
            result["weaknesses"] = [
                s.strip() for s in weaknesses_section.group(1).split("\n") 
                if s.strip() and (s.strip().startswith('-') or s.strip().startswith('*'))
            ]
            result["weaknesses"] = [s.lstrip('-* ').strip() for s in result["weaknesses"]]
        
        suggestions_section = re.search(r"Suggested Improvements:\s*(.*?)(?=\n\s*\n|\Z)", text, re.DOTALL | re.IGNORECASE)
        if not suggestions_section:
            suggestions_section = re.search(r"Suggested Improvements:\s*(.*?)(?=Weaknesses:|\Z)", text, re.DOTALL | re.IGNORECASE)
        
        if suggestions_section:
            result["suggestions"] = [
                s.strip() for s in suggestions_section.group(1).split("\n") 
                if s.strip() and (s.strip().startswith('-') or s.strip().startswith('*') or s.strip()[0].isdigit())
            ]
            result["suggestions"] = [re.sub(r'^[\d\-*\.\s]+', '', s).strip() for s in result["suggestions"]]
        
        return result

    def _calculate_readability(self, text: str) -> Dict:
        """Calculate readability metrics for a question/answer"""
        if not text.strip():
            return {}
            
        metrics = {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "gunning_fog": textstat.gunning_fog(text),
            "word_count": len(text.split()),
            "sentence_count": textstat.sentence_count(text),
            "difficult_words": textstat.difficult_words(text)
        }
        
        return metrics