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
    
    
    

""" 
=== EXAM PAPER REVIEW RESULTS ===

OVERALL SCORE: 1750.0%
Total Marks: 5.4/8


QUESTION 1: Explain the difference between mitosis and meiosis.
Score: 60%
Marks: 3.0/5

Strengths:
- Correctly distinguishes between the purposes of mitosis and meiosis.
- Recognizes the difference in cell outcomes (identical vs. different).
- Acknowledges that meiosis involves more steps.

Areas for Improvement:
- Lacks specific details about the number of divisions and cells produced.
- Does not mention genetic variation mechanisms like crossing over.
- The answer is too brief and lacks depth.

Suggestions:
- Include the number of divisions (1 for mitosis, 2 for meiosis).
- Mention the number of resulting cells (2 for mitosis, 4 for meiosis).
- Explain genetic variation mechanisms like crossing over and independent assortment.

Detailed Feedback:
ACCURACY: 70
COMPLETENESS: 50
CLARITY: 60

FEEDBACK:
- The student correctly identifies that mitosis produces identical cells and meiosis produces diverse cells, and correctly associates mitosis with body cells and meiosis with sex cells.
- The student mentions that meiosis has more steps, which is correct but lacks specifics like the number of divisions or cells produced.
- The answer is clear but overly brief and lacks detailed explanations of genetic variation mechanisms.

STRENGTHS:
- Correctly distinguishes between the purposes of mitosis and meiosis.
- Recognizes the difference in cell outcomes (identical vs. different).
- Acknowledges that meiosis involves more steps.

WEAKNESSES:
- Lacks specific details about the number of divisions and cells produced.
- Does not mention genetic variation mechanisms like crossing over.
- The answer is too brief and lacks depth.

SUGGESTED IMPROVEMENTS:
- Include the number of divisions (1 for mitosis, 2 for meiosis).
- Mention the number of resulting cells (2 for mitosis, 4 for meiosis).
- Explain genetic variation mechanisms like crossing over and independent assortment.

FINAL SCORE: 60

================================================================================

QUESTION 2: What is Newton's First Law of Motion?
Score: 80%
Marks: 2.4/3

Strengths:
- Correctly conveys the essence of Newton's First Law.
- Uses clear and simple language for easy understanding.
- Addresses both states of motion and rest.

Areas for Improvement:
- Missing specific terminology which is crucial for a complete understanding.
- The explanation is overly simplistic, lacking scientific depth.

Suggestions:
- Include terms like 'constant velocity' and 'external net force.'
- Elaborate on what constitutes an external force.
- Provide examples to illustrate the concept better.

Detailed Feedback:
ACCURACY: 80
COMPLETENESS: 70
CLARITY: 90

FEEDBACK:
- The student correctly identifies the concept of inertia but lacks specific terms like 'constant velocity' and 'external net force.'
- The answer addresses both motion and rest but omits key details necessary for completeness.
- The structure is clear and straightforward, though it could benefit from more scientific depth.

STRENGTHS:
- Correctly conveys the essence of Newton's First Law.
- Uses clear and simple language for easy understanding.
- Addresses both states of motion and rest.

WEAKNESSES:
- Missing specific terminology which is crucial for a complete understanding.
- The explanation is overly simplistic, lacking scientific depth.

SUGGESTED IMPROVEMENTS:
- Include terms like 'constant velocity' and 'external net force.'
- Elaborate on what constitutes an external force.
- Provide examples to illustrate the concept better.

FINAL SCORE: 80

================================================================================


SUMMARY FEEDBACK

Key Strengths:
- Correctly distinguishes between the purposes of mitosis and meiosis.
- Correctly conveys the essence of Newton's First Law.

Main Weaknesses:
- Lacks specific details about the number of divisions and cells produced.
- Missing specific terminology which is crucial for a complete understanding.

Top Suggestions:
- Include the number of divisions (1 for mitosis, 2 for meiosis).
- Include terms like 'constant velocity' and 'external net force.'
(venv) (base) PS D:\Advance Learning> 
"""