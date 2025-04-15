import logging
from paper_reviewer import ExamPaperReviewer

logging.basicConfig(level=logging.INFO)
reviewer = ExamPaperReviewer()

exam_paper = [
    {
        "question": "Explain the difference between mitosis and meiosis.",
        "model_answer": "Mitosis is a cell division process that results in two genetically identical daughter cells, used for growth and repair. Meiosis produces four genetically diverse gametes with half the chromosome number, used for sexual reproduction. Key differences include: 1) Number of divisions (1 vs 2), 2) Genetic variation (none vs crossing over and independent assortment), 3) Number of resulting cells (2 vs 4).",
        "student_answer": "Mitosis makes identical cells while meiosis makes different cells. Mitosis is for body cells and meiosis is for sex cells. Meiosis has more steps than mitosis.",
        "marks": 5
    },
    {
        "question": "What is Newton's First Law of Motion?",
        "model_answer": "Newton's First Law, also called the Law of Inertia, states that an object at rest will remain at rest, and an object in motion will continue in motion with constant velocity, unless acted upon by an external net force.",
        "student_answer": "Things keep moving unless something stops them. Things that aren't moving won't start moving by themselves.",
        "marks": 3
    }
]

try:
    results = reviewer.review_exam_paper(exam_paper)
    
    print("\n=== EXAM PAPER REVIEW RESULTS ===\n")
    
    print(f"OVERALL SCORE: {results['overall_score']}%")
    print(f"Total Marks: {sum(q['marks_awarded'] for q in results['questions'])}/{sum(q['marks'] for q in exam_paper)}")
    print("\n")
    
    for i, (q_result, q_original) in enumerate(zip(results['questions'], exam_paper)):
        print(f"QUESTION {i+1}: {q_original['question']}")
        print(f"Score: {q_result['score']}%")
        print(f"Marks: {q_result['marks_awarded']}/{q_original['marks']}")
        
        print("\nStrengths:")
        for strength in (q_result['strengths'] or ["No specific strengths identified"]):
            print(f"- {strength}")
            
        print("\nAreas for Improvement:")
        for weakness in (q_result['weaknesses'] or ["No specific weaknesses identified"]):
            print(f"- {weakness}")
            
        print("\nSuggestions:")
        for suggestion in (q_result['suggestions'] or ["No specific suggestions provided"]):
            print(f"- {suggestion}")
        
        print("\nDetailed Feedback:")
        print(q_result['detailed_feedback'])
        print("\n" + "="*80 + "\n")
    
    print("\nSUMMARY FEEDBACK")
    print("\nKey Strengths:")
    for strength in (results['feedback_summary']['strengths'] or ["No overall strengths identified"]):
        print(f"- {strength}")
        
    print("\nMain Weaknesses:")
    for weakness in (results['feedback_summary']['weaknesses'] or ["No overall weaknesses identified"]):
        print(f"- {weakness}")
        
    print("\nTop Suggestions:")
    for suggestion in (results['feedback_summary']['suggestions'] or ["No overall suggestions provided"]):
        print(f"- {suggestion}")

except Exception as e:
    print(f"\nError occurred during paper review: {str(e)}")