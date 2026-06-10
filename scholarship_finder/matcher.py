"""Scholarship Finder Matching Algorithm - Smart, context-aware matching logic"""

from datetime import datetime
from typing import List, Dict, Tuple
from .scholarships_database import SCHOLARSHIPS_DB, SUBJECT_MAPPING


class ScholarshipMatcher:
    """
    Intelligent scholarship matching system that evaluates student profiles
    against real UK scholarships and returns ranked results with match scores.
    """

    def __init__(self):
        self.scholarships = SCHOLARSHIPS_DB
        self.subject_mapping = SUBJECT_MAPPING

    def find_scholarships(
        self,
        nationality: str,
        degree_level: str,
        course_interest: str,
        degree_grade: float,
        ielts_score: float,
        budget_range_usd: Tuple[float, float],
        funding_type: str,
    ) -> List[Dict]:
        """
        Main entry point - finds and ranks scholarships for a student.

        Args:
            nationality: Student's nationality (e.g., "Indian")
            degree_level: "Undergraduate" or "Postgraduate"
            course_interest: Course/subject (e.g., "MSc Data Science")
            degree_grade: GPA or grade out of 10
            ielts_score: IELTS score (e.g., 6.5)
            budget_range_usd: Tuple of (min, max) in USD
            funding_type: "Fully-funded", "Partial", or "Self-funded"

        Returns:
            List of scholarships ranked by match score (highest first)
        """
        # Convert USD budget to GBP (approximate exchange rate: 1 USD = 0.79 GBP)
        usd_to_gbp = 0.79
        budget_range_gbp = (
            budget_range_usd[0] * usd_to_gbp,
            budget_range_usd[1] * usd_to_gbp,
        )

        # Filter and score scholarships
        ranked_scholarships = []
        for scholarship in self.scholarships:
            score = self._calculate_match_score(
                scholarship=scholarship,
                nationality=nationality,
                degree_level=degree_level,
                course_interest=course_interest,
                degree_grade=degree_grade,
                ielts_score=ielts_score,
                budget_range_gbp=budget_range_gbp,
                funding_type=funding_type,
            )

            # Only include scholarships with positive match scores
            if score > 0:
                scholarship_with_score = scholarship.copy()
                scholarship_with_score["match_score"] = score
                scholarship_with_score["match_reasoning"] = self._generate_reasoning(
                    scholarship, nationality, course_interest, degree_grade, ielts_score
                )
                ranked_scholarships.append(scholarship_with_score)

        # Sort by match score (descending) and return top 6-8
        ranked_scholarships.sort(key=lambda x: x["match_score"], reverse=True)
        return ranked_scholarships[:8]

    def _calculate_match_score(
        self,
        scholarship: Dict,
        nationality: str,
        degree_level: str,
        course_interest: str,
        degree_grade: float,
        ielts_score: float,
        budget_range_gbp: Tuple[float, float],
        funding_type: str,
    ) -> float:
        """
        Calculate comprehensive match score (0-100) considering all factors.
        Weights:
        - Subject alignment: 30%
        - Academic credentials: 25%
        - IELTS requirement: 15%
        - Budget fit: 15%
        - Eligibility: 15%
        """
        score = 0.0

        # 1. DEGREE LEVEL CHECK (Must match)
        if degree_level not in scholarship["degree_levels"]:
            return 0.0

        # 2. NATIONALITY CHECK
        if scholarship["eligible_nationalities"][0] != "All":
            if nationality not in scholarship["eligible_nationalities"]:
                return 0.0
        nationality_score = 10  # Base points for eligibility

        # 3. SUBJECT ALIGNMENT (30% weight)
        subject_score = self._evaluate_subject_match(course_interest, scholarship)

        # 4. ACADEMIC CREDENTIALS (25% weight)
        academic_score = self._evaluate_academic_credentials(
            degree_grade, scholarship
        )

        # 5. IELTS REQUIREMENT (15% weight)
        ielts_score_points = self._evaluate_ielts(
            ielts_score, scholarship["ielts_requirement"]
        )

        # 6. BUDGET FIT (15% weight)
        budget_score = self._evaluate_budget_fit(
            scholarship["value_gbp"], budget_range_gbp
        )

        # Calculate weighted total
        total_score = (
            (subject_score * 0.30)
            + (academic_score * 0.25)
            + (ielts_score_points * 0.15)
            + (budget_score * 0.15)
            + (nationality_score * 0.15)
        )

        # Ensure score is between 0 and 100
        return min(100, max(0, total_score))

    def _evaluate_subject_match(self, course_interest: str, scholarship: Dict) -> float:
        """
        Evaluate how well the course matches scholarship subject areas.
        Perfect match = 100, partial match = 60-80, no match = 0
        """
        scholarship_subjects = scholarship["subject_areas"]

        # If scholarship covers "All subjects"
        if "All subjects" in scholarship_subjects:
            return 90  # Good match but generic

        # Get expected subjects for the course
        expected_subjects = self.subject_mapping.get(
            course_interest, [course_interest]
        )

        # Check for perfect matches
        perfect_matches = [
            s for s in expected_subjects if s in scholarship_subjects
        ]
        if perfect_matches:
            return 100  # Exact subject match

        # Check for partial matches (e.g., Engineering for Data Science)
        partial_matches = []
        for expected in expected_subjects:
            for scholarship_subject in scholarship_subjects:
                if (
                    expected.lower() in scholarship_subject.lower()
                    or scholarship_subject.lower() in expected.lower()
                ):
                    partial_matches.append(scholarship_subject)

        if partial_matches:
            return 75  # Partial match

        return 0  # No match

    def _evaluate_academic_credentials(self, degree_grade: float, scholarship: Dict) -> float:
        """
        Evaluate academic fit based on grade requirements.
        Grade is out of 10 (e.g., 7.8/10 = 78%)
        """
        # Map scholarship requirements to required grades
        requirement_map = {
            "First-class honors": 8.0,
            "first-class": 8.0,
            "3.8+ GPA": 8.2,
            "3.7/4.0": 9.25,
            "2.1 honors": 6.5,
            "2.1": 6.5,
            "Strong academic": 7.0,
        }

        # Find minimum required grade from criteria
        min_required = 6.0  # Default minimum
        for criteria in scholarship["eligibility_criteria"]:
            for key, grade_threshold in requirement_map.items():
                if key.lower() in criteria.lower():
                    min_required = max(min_required, grade_threshold)

        # Score based on how much above requirement
        if degree_grade >= min_required:
            # Calculate bonus for exceeding requirements
            excess = degree_grade - min_required
            base_score = 80
            bonus = min(20, excess * 5)  # Cap bonus at 20 points
            return min(100, base_score + bonus)
        else:
            # Partial credit if slightly below
            if degree_grade >= min_required - 0.5:
                return 60
            return 30  # Still possible but less likely

    def _evaluate_ielts(self, ielts_score: float, required_ielts: float) -> float:
        """
        Evaluate IELTS eligibility and fit.
        """
        if ielts_score < required_ielts - 0.5:
            # Below minimum threshold
            return 20  # Unlikely but not impossible
        elif ielts_score < required_ielts:
            # Slightly below
            return 70
        elif ielts_score == required_ielts:
            # Meets requirement exactly
            return 85
        else:
            # Exceeds requirement
            excess = ielts_score - required_ielts
            return min(100, 85 + (excess * 5))

    def _evaluate_budget_fit(self, scholarship_value: float, budget_range: Tuple[float, float]) -> float:
        """
        Evaluate how well scholarship value matches student's budget.
        Perfect fit = within range, bonus for exceeding, penalty for falling short.
        """
        min_budget, max_budget = budget_range

        # If scholarship exceeds max budget (extra coverage)
        if scholarship_value > max_budget:
            excess_ratio = scholarship_value / max_budget
            if excess_ratio <= 1.5:  # Up to 50% more is good
                return 95
            else:
                return 85  # Good but significantly more than needed

        # If scholarship is within range
        if min_budget <= scholarship_value <= max_budget:
            coverage_ratio = scholarship_value / min_budget
            if coverage_ratio >= 1.5:  # Covers 1.5x minimum
                return 100
            else:
                return 90

        # If scholarship is below budget range
        if scholarship_value < min_budget:
            coverage_ratio = scholarship_value / min_budget
            return 70 * coverage_ratio  # Partial coverage

        return 50

    def _generate_reasoning(self,
                           scholarship: Dict,
                           nationality: str,
                           course_interest: str,
                           degree_grade: float,
                           ielts_score: float) -> str:
        """
        Generate human-readable reasoning for the match score.
        """
        reasons = []

        # Subject match
        if course_interest.lower() in str(scholarship["subject_areas"]).lower():
            reasons.append(f"Strong subject fit for {course_interest}")
        elif "Data Science" in course_interest and any(s in scholarship["subject_areas"] for s in ["Computing", "Engineering", "Science"]):
            reasons.append(f"Good technical subject alignment for {course_interest}")
        else:
            reasons.append("Accepts your subject area")

        # Academic credentials
        if degree_grade >= 8.0:
            reasons.append(f"Excellent grades ({degree_grade}/10) exceed most requirements")
        elif degree_grade >= 7.0:
            reasons.append(f"Strong academic record ({degree_grade}/10)")
        else:
            reasons.append(f"Meets minimum academic requirements ({degree_grade}/10)")

        # IELTS
        if ielts_score >= scholarship["ielts_requirement"]:
            reasons.append(f"IELTS score {ielts_score} meets requirement")
        else:
            reasons.append(
                f"IELTS score {ielts_score} slightly below typical requirement of {scholarship['ielts_requirement']}"
            )

        # Value
        reasons.append(f"Scholarship value: £{scholarship['value_gbp']:,.0f}")

        # Nationality
        reasons.append(f"Open to {nationality} nationals")

        return " | ".join(reasons)


def find_best_scholarships(
    nationality: str,
    degree_level: str,
    course_interest: str,
    degree_grade: float,
    ielts_score: float,
    budget_range_usd: Tuple[float, float],
    funding_type: str = "Self-funded",
) -> List[Dict]:
    """
    Convenience function to find scholarships.
    """
    matcher = ScholarshipMatcher()
    return matcher.find_scholarships(
        nationality=nationality,
        degree_level=degree_level,
        course_interest=course_interest,
        degree_grade=degree_grade,
        ielts_score=ielts_score,
        budget_range_usd=budget_range_usd,
        funding_type=funding_type,
    )
