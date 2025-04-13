from openai import OpenAI
from typing import List, Dict
from config import Config
import re
import logging

class QuestionGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.logger = logging.getLogger(__name__)
        
    def generate_questions(self, context: str, question_type: str, num_questions: int) -> List[Dict]:
        if not context:
            raise ValueError("Empty context provided")
            
        if question_type not in ['mcq', 'written']:
            raise ValueError("Invalid question type. Choose 'mcq' or 'written'")
            
        if num_questions <= 0:
            raise ValueError("Number of questions must be positive")

        try:
            if question_type == 'mcq':
                return self._generate_mcqs(context, num_questions)
            else:
                return self._generate_written(context, num_questions)
        except Exception as e:
            self.logger.error(f"Question generation failed: {str(e)}")
            raise

    def _generate_mcqs(self, context: str, num_questions: int) -> List[Dict]:
        prompt = Config.MCQ_TEMPLATE.format(
            num_questions=num_questions,
            context=context
        )
        
        response = self._call_llm(prompt)
        return self._parse_mcq_response(response)

    def _generate_written(self, context: str, num_questions: int) -> List[Dict]:
        prompt = Config.WRITTEN_TEMPLATE.format(
            num_questions=num_questions,
            context=context
        )
        
        response = self._call_llm(prompt)
        return self._parse_written_response(response)

    def _call_llm(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": Config.SITE_URL,
                    "X-Title": Config.SITE_NAME,
                },
                model=Config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM API call failed: {str(e)}")
            raise

    @staticmethod
    def _parse_mcq_response(text: str) -> List[Dict]:
        questions = []
        current_q = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith('q:'):
                if current_q:
                    questions.append(current_q)
                current_q = {
                    'question': line[2:].strip(),
                    'options': [],
                    'answer': '',
                    'type': 'mcq'
                }
            elif re.match(r'^[A-D]\)', line, re.IGNORECASE):
                current_q['options'].append(line[2:].strip())
            elif line.lower().startswith('answer:'):
                current_q['answer'] = line.split(':')[1].strip().upper()
        
        if current_q:
            questions.append(current_q)
            
        return questions

    @staticmethod
    def _parse_written_response(text: str) -> List[Dict]:
        """Parse written questions response"""
        return [{
            'question': line[2:].strip(),
            'type': 'written'
        } for line in text.split('\n') if line.lower().startswith('q:')]