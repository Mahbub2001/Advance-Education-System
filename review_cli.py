from paper_reviewer import PaperReviewer
from config import Config
import json
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=== Academic Paper Review System ===")
    print("Supports: essays, research papers, reports, theses\n")
    
    reviewer = PaperReviewer()
    
    # Input options
    input_method = input("Enter text directly (1) or load from file (2)? ").strip()
    
    if input_method == "1":
        print("\nEnter/Paste your content (Ctrl+D to finish):")
        paper_text = ""
        try:
            while True:
                paper_text += input() + "\n"
        except EOFError:
            pass
    else:
        file_path = input("Enter file path: ").strip()
        try:
            with open(file_path, 'r') as f:
                paper_text = f.read()
        except Exception as e:
            logger.error(f"Failed to read file: {str(e)}")
            return
    
    paper_type = input("Paper type (essay/research/report/thesis): ").lower().strip()
    
    try:
        print("\nAnalyzing paper...")
        results = reviewer.review_paper(paper_text, paper_type)
        
        # Save results
        output_dir = Path("./reviews")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "paper_review.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Display summary
        print("\n=== REVIEW SUMMARY ===")
        print(f"Overall Score: {results['overall_score']}/100")
        
        print("\nCONTENT (Score: {})".format(results['content_analysis']['score']))
        print("Strengths:")
        for s in results['content_analysis']['strengths'][:3]:
            print(f"- {s}")
            
        print("\nAreas for Improvement:")
        for w in results['content_analysis']['weaknesses'][:3]:
            print(f"- {w}")
        
        print("\nGRAMMAR (Score: {})".format(results['grammar_analysis']['score']))
        print(f"Found {results['grammar_analysis']['error_count']} errors")
        if results['grammar_analysis']['errors']:
            print("\nTop Corrections:")
            for err, fix in zip(results['grammar_analysis']['errors'][:3], 
                              results['grammar_analysis']['corrections'][:3]):
                print(f"{err} → {fix}")
        
        print("\nFull report saved to:", output_file)
        
    except Exception as e:
        logger.error(f"Review failed: {str(e)}")

if __name__ == "__main__":
    main()