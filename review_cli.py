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
    # {
    #     "question": "What is Newton's First Law of Motion?",
    #     "model_answer": "Newton's First Law, also called the Law of Inertia, states that an object at rest will remain at rest, and an object in motion will continue in motion with constant velocity, unless acted upon by an external net force.",
    #     "student_answer": "Things keep moving unless something stops them. Things that aren't moving won't start moving by themselves.",
    #     "marks": 3
    # }
]

results = reviewer.review_exam_paper(exam_paper)

print(f"Overall Score: {results['overall_score']}%")
print("\nQuestion-by-question feedback:")
for i, q in enumerate(results['questions']):
    print(f"\nQuestion {i+1}:")
    print(f"Score: {q['score']}%")
    print(f"Marks awarded: {q['marks_awarded']}")
    print("\nStrengths:")
    for strength in q['strengths']:
        print(f"- {strength}")
    print("\nAreas for improvement:")
    for weakness in q['weaknesses']:
        print(f"- {weakness}")
    print("\nSuggestions:")
    for suggestion in q['suggestions']:
        print(f"- {suggestion}")

print("\nSummary Feedback:")
print("Strengths:")
for strength in results['feedback_summary']['strengths']:
    print(f"- {strength}")
print("\nWeaknesses:")
for weakness in results['feedback_summary']['weaknesses']:
    print(f"- {weakness}")
print("\nSuggestions:")
for suggestion in results['feedback_summary']['suggestions']:
    print(f"- {suggestion}")