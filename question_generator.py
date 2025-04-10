import openai
from typing import List, Dict
from config import Config
import re

class QuestionGenerator:
    @staticmethod
    def generate_mcq_questions(context: List[str], num_questions: int = None) -> List[Dict]:
        """
        Generate multiple-choice questions from context using LLM
        """
        if num_questions is None:
            num_questions = Config.DEFAULT_NUM_QUESTIONS
            
        prompt = Config.MCQ_TEMPLATE.format(
            num_questions=num_questions,
            context="\n".join(context)
        )
        
        response = openai.ChatCompletion.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return QuestionGenerator._parse_mcq_response(response.choices[0].message.content)

    @staticmethod
    def generate_written_questions(context: List[str], num_questions: int = None) -> List[Dict]:
        """
        Generate written answer questions from context using LLM
        """
        if num_questions is None:
            num_questions = Config.DEFAULT_NUM_QUESTIONS
            
        prompt = Config.WRITTEN_TEMPLATE.format(
            num_questions=num_questions,
            context="\n".join(context)
        )
        
        response = openai.ChatCompletion.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return QuestionGenerator._parse_written_response(response.choices[0].message.content)

    @staticmethod
    def _parse_mcq_response(text: str) -> List[Dict]:
        """
        Parse the LLM response into structured MCQ format
        """
        questions = []
        current_q = {}
        pattern = re.compile(r'^(Q:|[A-D]\)|Answer:)', re.IGNORECASE)
        
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
                    'answer': ''
                }
            elif re.match(r'^[A-D]\)', line, re.IGNORECASE):
                option_text = line[2:].strip()
                current_q['options'].append(option_text)
            elif line.lower().startswith('answer:'):
                current_q['answer'] = line.split(':')[1].strip().upper()
        
        if current_q:
            questions.append(current_q)
        
        return questions

    @staticmethod
    def _parse_written_response(text: str) -> List[Dict]:
        """
        Parse written questions into structured format
        """
        questions = []
        
        for line in text.split('\n'):
            line = line.strip()
            if line.lower().startswith('q:'):
                questions.append({
                    'question': line[2:].strip(),
                    'type': 'written'
                })
        
        return questions