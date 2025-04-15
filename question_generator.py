from openai import OpenAI
from typing import List, Dict, Tuple
from config import Config
import re
import logging
import math
from concurrent.futures import ThreadPoolExecutor
from diskcache import Cache

class QuestionGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.logger = logging.getLogger(__name__)
        self.cache = Cache(Config.CACHE_DIR)
        
    def generate_questions(self, context: str, question_type: str, num_questions: int, 
                         weaknesses: List[str] = None, strengths: List[str] = None) -> List[Dict]:
        """Main method to generate questions with student weaknesses/strengths in mind"""
        if not context:
            raise ValueError("Empty context provided")
            
        if question_type not in ['mcq', 'written']:
            raise ValueError("Invalid question type. Choose 'mcq' or 'written'")
            
        if num_questions <= 0:
            raise ValueError("Number of questions must be positive")

        try:
            token_count = len(context.split()) * 1.33
            
            if weaknesses or strengths:
                if token_count <= Config.SINGLE_BATCH_THRESHOLD:
                    return self._generate_single_batch_with_focus(context, question_type, num_questions, weaknesses, strengths)
                else:
                    return self._generate_multi_batch_with_focus(context, question_type, num_questions, weaknesses, strengths)
            else:
                if token_count <= Config.SINGLE_BATCH_THRESHOLD:
                    return self._generate_single_batch(context, question_type, num_questions)
                else:
                    return self._generate_multi_batch(context, question_type, num_questions)
                
        except Exception as e:
            self.logger.error(f"Question generation failed: {str(e)}")
            raise

    def _generate_single_batch(self, context: str, question_type: str, num_questions: int) -> List[Dict]:
        """Handle small content in one batch"""
        if question_type == 'mcq':
            return self._generate_mcqs(context, num_questions)
        return self._generate_written(context, num_questions)

    def _generate_multi_batch(self, context: str, question_type: str, num_questions: int) -> List[Dict]:
        """Handle large content with chunking and parallel processing"""
        chunks, questions_per_chunk = self._calculate_optimal_chunking(context, num_questions)
        
        with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
            futures = []
            for chunk in chunks:
                futures.append(
                    executor.submit(
                        self._generate_questions_from_chunk,
                        chunk,
                        question_type,
                        questions_per_chunk
                    )
                )
            
            questions = []
            for future in futures:
                try:
                    questions.extend(future.result())
                except Exception as e:
                    self.logger.warning(f"Chunk processing failed: {str(e)}")
            
            return self._deduplicate_questions(questions)[:num_questions]

    def _calculate_optimal_chunking(self, context: str, num_questions: int) -> Tuple[List[str], int]:
        """Determine optimal chunking strategy"""
        paragraphs = [p for p in context.split('\n\n') if p.strip()]
        total_paragraphs = len(paragraphs)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para.split())
            if current_size + para_size > Config.MAX_CHUNK_TOKENS and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_size = 0
                
            current_chunk.append(para)
            current_size += para_size
            
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        num_chunks = min(len(chunks), Config.MAX_CHUNKS)
        questions_per_chunk = max(1, math.ceil(num_questions / num_chunks))
        
        return chunks, questions_per_chunk

    def _generate_questions_from_chunk(self, chunk: str, question_type: str, num_questions: int) -> List[Dict]:
        """Generate questions from a single chunk"""
        cache_key = f"{hash(chunk)}_{question_type}_{num_questions}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            if question_type == 'mcq':
                result = self._generate_mcqs(chunk, num_questions)
            else:
                result = self._generate_written(chunk, num_questions)
                
            self.cache[cache_key] = result
            return result
        except Exception as e:
            self.logger.error(f"Failed to process chunk: {str(e)}")
            return []

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
        
    def _generate_single_batch_with_focus(self, context: str, question_type: str, 
                                        num_questions: int, weaknesses: List[str], 
                                        strengths: List[str]) -> List[Dict]:
        """Handle small content with weakness/strength focus in one batch"""
        if question_type == 'mcq':
            return self._generate_mcqs_with_focus(context, num_questions, weaknesses, strengths)
        return self._generate_written_with_focus(context, num_questions, weaknesses, strengths)

    def _generate_multi_batch_with_focus(self, context: str, question_type: str, 
                                       num_questions: int, weaknesses: List[str], 
                                       strengths: List[str]) -> List[Dict]:
        """Handle large content with chunking and parallel processing with focus"""
        chunks, questions_per_chunk = self._calculate_optimal_chunking(context, num_questions)
        
        with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
            futures = []
            for chunk in chunks:
                futures.append(
                    executor.submit(
                        self._generate_questions_from_chunk_with_focus,
                        chunk,
                        question_type,
                        questions_per_chunk,
                        weaknesses,
                        strengths
                    )
                )
            
            questions = []
            for future in futures:
                try:
                    questions.extend(future.result())
                except Exception as e:
                    self.logger.warning(f"Chunk processing failed: {str(e)}")
            
            return self._deduplicate_questions(questions)[:num_questions]

    def _generate_questions_from_chunk_with_focus(self, chunk: str, question_type: str, 
                                                num_questions: int, weaknesses: List[str], 
                                                strengths: List[str]) -> List[Dict]:
        """Generate questions from a single chunk with focus on weaknesses"""
        cache_key = f"{hash(chunk)}_{question_type}_{num_questions}_w{hash(str(weaknesses))}_s{hash(str(strengths))}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            if question_type == 'mcq':
                result = self._generate_mcqs_with_focus(chunk, num_questions, weaknesses, strengths)
            else:
                result = self._generate_written_with_focus(chunk, num_questions, weaknesses, strengths)
                
            self.cache[cache_key] = result
            return result
        except Exception as e:
            self.logger.error(f"Failed to process chunk: {str(e)}")
            return []

    def _generate_mcqs_with_focus(self, context: str, num_questions: int, 
                                 weaknesses: List[str], strengths: List[str]) -> List[Dict]:
        prompt = Config.MCQ_WEAKNESS_TEMPLATE.format(
            num_questions=num_questions,
            weaknesses=", ".join(weaknesses) if weaknesses else "none",
            strengths=", ".join(strengths) if strengths else "none",
            context=context
        )
        response = self._call_llm(prompt)
        return self._parse_mcq_response(response)

    def _generate_written_with_focus(self, context: str, num_questions: int, 
                                   weaknesses: List[str], strengths: List[str]) -> List[Dict]:
        prompt = Config.WRITTEN_WEAKNESS_TEMPLATE.format(
            num_questions=num_questions,
            weaknesses=", ".join(weaknesses) if weaknesses else "none",
            strengths=", ".join(strengths) if strengths else "none",
            context=context
        )
        response = self._call_llm(prompt)
        return self._parse_written_response(response)

    @staticmethod
    def _deduplicate_questions(questions: List[Dict]) -> List[Dict]:
        """Remove duplicate questions while preserving order"""
        seen = set()
        unique_questions = []
        
        for q in questions:
            question_text = q['question'].lower().strip()
            if question_text not in seen:
                seen.add(question_text)
                unique_questions.append(q)
                
        return unique_questions

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
                    'explanation': '',
                    'type': 'mcq'
                }
            elif re.match(r'^[A-D]\)', line, re.IGNORECASE):
                current_q['options'].append(line[2:].strip())
            elif line.lower().startswith('answer:'):
                current_q['answer'] = line.split(':')[1].strip().upper()
            elif line.lower().startswith('explanation:'):
                current_q['explanation'] = line.split(':')[1].strip()
        
        if current_q:
            questions.append(current_q)
            
        return questions

    @staticmethod
    def _parse_written_response(text: str) -> List[Dict]:
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
                    'solution': '',
                    'type': 'written'
                }
            elif line.lower().startswith('solution:'):
                current_q['solution'] = line.split(':')[1].strip()
        
        if current_q:
            questions.append(current_q)
            
        return questions