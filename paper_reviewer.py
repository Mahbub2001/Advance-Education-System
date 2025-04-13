from openai import OpenAI
from typing import Dict, List
from config import Config
import re
import logging
from concurrent.futures import ThreadPoolExecutor
from diskcache import Cache
import textstat

class PaperReviewer:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.logger = logging.getLogger(__name__)
        self.cache = Cache(Config.REVIEW_CACHE_DIR)
        
    def review_paper(self, paper_text: str, paper_type: str = "essay") -> Dict:
        """
        Comprehensive paper review with multiple analysis dimensions
        """
        if not paper_text.strip():
            raise ValueError("Empty paper content provided")
            
        cache_key = f"{hash(paper_text)}_{paper_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            # Parallel execution of different review aspects
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_content = executor.submit(
                    self._review_content, 
                    paper_text, 
                    paper_type
                )
                future_structure = executor.submit(
                    self._review_structure, 
                    paper_text
                )
                future_grammar = executor.submit(
                    self._review_grammar, 
                    paper_text
                )
                future_metrics = executor.submit(
                    self._calculate_metrics, 
                    paper_text
                )
                
                results = {
                    "content_analysis": future_content.result(),
                    "structure_analysis": future_structure.result(),
                    "grammar_analysis": future_grammar.result(),
                    "readability_metrics": future_metrics.result(),
                    "overall_score": None
                }
                
            # Calculate overall score (weighted average)
            weights = Config.REVIEW_WEIGHTS
            scores = {
                "content": results["content_analysis"]["score"],
                "structure": results["structure_analysis"]["score"],
                "grammar": results["grammar_analysis"]["score"],
                "readability": results["readability_metrics"]["overall_score"]
            }
            
            overall_score = sum(scores[k] * weights[k] for k in weights) / sum(weights.values())
            results["overall_score"] = round(overall_score, 1)
            
            self.cache[cache_key] = results
            return results
            
        except Exception as e:
            self.logger.error(f"Paper review failed: {str(e)}")
            raise

    def _review_content(self, paper_text: str, paper_type: str) -> Dict:
        """Evaluate content quality and relevance"""
        prompt = Config.CONTENT_REVIEW_TEMPLATE.format(
            paper_type=paper_type,
            content=paper_text[:Config.MAX_REVIEW_LENGTH]
        )
        
        response = self._call_llm(prompt)
        return self._parse_content_response(response)

    def _review_structure(self, paper_text: str) -> Dict:
        """Evaluate paper structure and organization"""
        prompt = Config.STRUCTURE_REVIEW_TEMPLATE.format(
            content=paper_text[:Config.MAX_REVIEW_LENGTH]
        )
        
        response = self._call_llm(prompt)
        return self._parse_structure_response(response)

    def _review_grammar(self, paper_text: str) -> Dict:
        """Identify grammatical errors and suggest corrections"""
        prompt = Config.GRAMMAR_REVIEW_TEMPLATE.format(
            content=paper_text[:Config.MAX_REVIEW_LENGTH]
        )
        
        response = self._call_llm(prompt)
        return self._parse_grammar_response(response)

    def _calculate_metrics(self, paper_text: str) -> Dict:
        """Calculate readability and complexity metrics"""
        metrics = {
            "flesch_reading_ease": textstat.flesch_reading_ease(paper_text),
            "smog_index": textstat.smog_index(paper_text),
            "coleman_liau_index": textstat.coleman_liau_index(paper_text),
            "automated_readability_index": textstat.automated_readability_index(paper_text),
            "dale_chall_readability": textstat.dale_chall_readability_score(paper_text),
            "difficult_words": textstat.difficult_words(paper_text),
            "linsear_write": textstat.linsear_write_formula(paper_text),
            "gunning_fog": textstat.gunning_fog(paper_text),
            "text_standard": textstat.text_standard(paper_text),
            "lexicon_count": textstat.lexicon_count(paper_text),
            "sentence_count": textstat.sentence_count(paper_text)
        }
        
        # Normalize to 0-100 scale where higher is better
        readability_score = max(0, min(100, metrics["flesch_reading_ease"]))
        complexity_score = 100 - min(100, metrics["gunning_fog"] * 10)
        overall_score = (readability_score * 0.6 + complexity_score * 0.4)
        
        metrics["overall_score"] = round(overall_score, 1)
        return metrics

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
                temperature=0.3,  # Lower temp for more factual responses
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM API call failed: {str(e)}")
            raise

    @staticmethod
    def _parse_content_response(text: str) -> Dict:
        """Parse content evaluation response"""
        sections = re.split(r"\n(?=[A-Z][a-z]+:)", text)
        result = {"score": 70, "strengths": [], "weaknesses": [], "suggestions": []}
        
        for section in sections:
            if "Strengths:" in section:
                result["strengths"] = [s.strip() for s in section.split(":")[1].split("\n") if s.strip()]
            elif "Weaknesses:" in section:
                result["weaknesses"] = [s.strip() for s in section.split(":")[1].split("\n") if s.strip()]
            elif "Suggestions:" in section:
                result["suggestions"] = [s.strip() for s in section.split(":")[1].split("\n") if s.strip()]
            elif "Score:" in section:
                try:
                    result["score"] = min(100, max(0, int(re.search(r"\d+", section).group())))
                except:
                    pass
                    
        return result

    @staticmethod
    def _parse_structure_response(text: str) -> Dict:
        """Parse structure evaluation response"""
        sections = re.split(r"\n(?=[A-Z][a-z]+:)", text)
        result = {"score": 70, "feedback": [], "organization": [], "flow": []}
        
        for section in sections:
            if "Feedback:" in section:
                result["feedback"] = [s.strip() for s in section.split(":")[1].split("\n") if s.strip()]
            elif "Organization:" in section:
                result["organization"] = [s.strip() for s in section.split(":")[1].split("\n") if s.strip()]
            elif "Flow:" in section:
                result["flow"] = [s.strip() for s in section.split(":")[1].split("\n") if s.strip()]
            elif "Score:" in section:
                try:
                    result["score"] = min(100, max(0, int(re.search(r"\d+", section).group())))
                except:
                    pass
                    
        return result

    @staticmethod
    def _parse_grammar_response(text: str) -> Dict:
        """Parse grammar evaluation response"""
        errors = []
        corrections = []
        
        # Parse error:correction pairs
        for line in text.split("\n"):
            if "→" in line:
                parts = line.split("→")
                if len(parts) == 2:
                    errors.append(parts[0].strip())
                    corrections.append(parts[1].strip())
        
        # Estimate score based on error density
        total_words = len(text.split())
        error_count = len(errors)
        error_ratio = min(1, error_count / (total_words / 100))  # errors per 100 words
        score = max(0, 100 - (error_ratio * 50))  # Deduct up to 50 points for errors
        
        return {
            "score": round(score, 1),
            "error_count": error_count,
            "errors": errors,
            "corrections": corrections
        }