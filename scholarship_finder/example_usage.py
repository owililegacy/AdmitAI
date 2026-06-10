"""Example usage of the Scholarship Finder"""

from matcher import find_best_scholarships

# Example 1: Indian MSc Data Science student
print("\n" + "="*80)
print("EXAMPLE 1: Indian student - MSc Data Science")
print("="*80)

student_1 = {
    "nationality": "Indian",
    "degree_level": "Postgraduate",
    "course_interest": "MSc Data Science",
    "degree_grade": 7.8,
    "ielts_score": 6.5,
    "budget_range_usd": (25000, 35000),
    "funding_type": "Self-funded",
}

results_1 = find_best_scholarships(**student_1)

print(f"\nFound {len(results_1)} matching scholarships:\n")
for i, scholarship in enumerate(results_1, 1):
    print(f"{i}. {scholarship['name']}")
    print(f"   Awarding Body: {scholarship['awarding_body']}")
    print(f"   Value: £{scholarship['value_gbp']:,.0f}")
    print(f"   Match Score: {scholarship['match_score']:.1f}/100")
    print(f"   Reasoning: {scholarship['match_reasoning']}")
    print(f"   Deadline: {scholarship['application_deadline']}")
    print(f"   URL: {scholarship['application_url']}")
    print()

# Example 2: Nigerian MBA student
print("\n" + "="*80)
print("EXAMPLE 2: Nigerian student - MBA")
print("="*80)

student_2 = {
    "nationality": "Nigerian",
    "degree_level": "Postgraduate",
    "course_interest": "MBA",
    "degree_grade": 8.2,
    "ielts_score": 7.0,
    "budget_range_usd": (40000, 60000),
    "funding_type": "Partial",
}

results_2 = find_best_scholarships(**student_2)

print(f"\nFound {len(results_2)} matching scholarships:\n")
for i, scholarship in enumerate(results_2, 1):
    print(f"{i}. {scholarship['name']}")
    print(f"   Awarding Body: {scholarship['awarding_body']}")
    print(f"   Value: £{scholarship['value_gbp']:,.0f}")
    print(f"   Match Score: {scholarship['match_score']:.1f}/100")
    print(f"   Reasoning: {scholarship['match_reasoning']}")
    print(f"   Deadline: {scholarship['application_deadline']}")
    print(f"   URL: {scholarship['application_url']}")
    print()

# Example 3: Chinese MSc Engineering student
print("\n" + "="*80)
print("EXAMPLE 3: Chinese student - MSc Engineering")
print("="*80)

student_3 = {
    "nationality": "Chinese",
    "degree_level": "Postgraduate",
    "course_interest": "MSc Engineering",
    "degree_grade": 8.5,
    "ielts_score": 6.8,
    "budget_range_usd": (30000, 45000),
    "funding_type": "Self-funded",
}

results_3 = find_best_scholarships(**student_3)

print(f"\nFound {len(results_3)} matching scholarships:\n")
for i, scholarship in enumerate(results_3, 1):
    print(f"{i}. {scholarship['name']}")
    print(f"   Awarding Body: {scholarship['awarding_body']}")
    print(f"   Value: £{scholarship['value_gbp']:,.0f}")
    print(f"   Match Score: {scholarship['match_score']:.1f}/100")
    print(f"   Reasoning: {scholarship['match_reasoning']}")
    print(f"   Deadline: {scholarship['application_deadline']}")
    print(f"   URL: {scholarship['application_url']}")
    print()
