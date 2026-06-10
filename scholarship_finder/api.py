"""FastAPI endpoints for Scholarship Finder service"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple
from .matcher import find_best_scholarships
from datetime import datetime

app = FastAPI(
    title="AdmitAI Scholarship Finder",
    description="Smart UK scholarship matching system for international students",
    version="1.0.0",
)


class StudentProfile(BaseModel):
    """Student profile for scholarship matching"""

    nationality: str = Field(..., example="Indian", description="Student nationality")
    degree_level: str = Field(
        ...,
        example="Postgraduate",
        description="Undergraduate or Postgraduate",
    )
    course_interest: str = Field(
        ...,
        example="MSc Data Science",
        description="Course or subject of interest",
    )
    degree_grade: float = Field(
        ...,
        example=7.8,
        description="Current degree grade (out of 10 or GPA equivalent)",
    )
    ielts_score: float = Field(
        ..., example=6.5, description="IELTS score"
    )
    budget_range_usd: Tuple[float, float] = Field(
        ...,
        example=(25000, 35000),
        description="Budget range in USD (min, max)",
    )
    funding_type: str = Field(
        default="Self-funded",
        example="Self-funded",
        description="Fully-funded, Partial, or Self-funded",
    )


class ScholarshipMatch(BaseModel):
    """Scholarship match result"""

    id: str
    name: str
    awarding_body: str
    value_gbp: float
    coverage: List[str]
    eligibility_criteria: List[str]
    eligible_nationalities: List[str]
    degree_levels: List[str]
    subject_areas: List[str]
    application_deadline: str
    application_url: str
    ielts_requirement: float
    match_score: float = Field(
        ..., description="Match score out of 100"
    )
    match_reasoning: str = Field(
        ..., description="Explanation of why this scholarship matches"
    )
    notes: str
    last_verified: str


class ScholarshipFinderResponse(BaseModel):
    """Response containing matched scholarships"""

    student_profile: StudentProfile
    total_matches: int
    scholarships: List[ScholarshipMatch]
    search_timestamp: str


@app.post(
    "/api/v1/find-scholarships",
    response_model=ScholarshipFinderResponse,
    summary="Find matching UK scholarships",
    tags=["Scholarship Finder"],
)
async def find_scholarships(profile: StudentProfile) -> ScholarshipFinderResponse:
    """
    Find and rank the best UK scholarships matching a student's profile.

    **Request body:**
    - `nationality`: Student's country of origin
    - `degree_level`: "Undergraduate" or "Postgraduate"
    - `course_interest`: Specific course or subject
    - `degree_grade`: Current academic grade (0-10 scale)
    - `ielts_score`: IELTS test score
    - `budget_range_usd`: Tuple of (minimum, maximum) scholarship needed in USD
    - `funding_type`: Type of funding sought

    **Response:**
    Returns 6-8 scholarships ranked by match score (highest first).
    """
    try:
        # Validate inputs
        if profile.degree_grade < 0 or profile.degree_grade > 10:
            raise HTTPException(
                status_code=400,
                detail="Degree grade must be between 0 and 10",
            )

        if profile.ielts_score < 0 or profile.ielts_score > 9:
            raise HTTPException(
                status_code=400,
                detail="IELTS score must be between 0 and 9",
            )

        if profile.budget_range_usd[0] < 0 or profile.budget_range_usd[1] < profile.budget_range_usd[0]:
            raise HTTPException(
                status_code=400,
                detail="Invalid budget range",
            )

        if profile.degree_level not in ["Undergraduate", "Postgraduate"]:
            raise HTTPException(
                status_code=400,
                detail="Degree level must be 'Undergraduate' or 'Postgraduate'",
            )

        # Find scholarships
        matches = find_best_scholarships(
            nationality=profile.nationality,
            degree_level=profile.degree_level,
            course_interest=profile.course_interest,
            degree_grade=profile.degree_grade,
            ielts_score=profile.ielts_score,
            budget_range_usd=profile.budget_range_usd,
            funding_type=profile.funding_type,
        )

        # Convert to response format
        scholarship_matches = [
            ScholarshipMatch(
                id=match["id"],
                name=match["name"],
                awarding_body=match["awarding_body"],
                value_gbp=match["value_gbp"],
                coverage=match["coverage"],
                eligibility_criteria=match["eligibility_criteria"],
                eligible_nationalities=match["eligible_nationalities"],
                degree_levels=match["degree_levels"],
                subject_areas=match["subject_areas"],
                application_deadline=match["application_deadline"],
                application_url=match["application_url"],
                ielts_requirement=match["ielts_requirement"],
                match_score=match["match_score"],
                match_reasoning=match["match_reasoning"],
                notes=match["notes"],
                last_verified=match["last_verified"],
            )
            for match in matches
        ]

        return ScholarshipFinderResponse(
            student_profile=profile,
            total_matches=len(scholarship_matches),
            scholarships=scholarship_matches,
            search_timestamp=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding scholarships: {str(e)}",
        )


@app.get(
    "/api/v1/health",
    tags=["Health"],
    summary="API health check",
)
async def health_check():
    """
    Check if the API is running and database is accessible.
    """
    return {
        "status": "healthy",
        "service": "AdmitAI Scholarship Finder",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get(
    "/",
    tags=["Documentation"],
)
async def root():
    """
    Welcome endpoint with API information.
    """
    return {
        "message": "AdmitAI Scholarship Finder API",
        "version": "1.0.0",
        "description": "Smart UK scholarship matching for international students",
        "docs": "/docs",
        "endpoints": {
            "find_scholarships": "POST /api/v1/find-scholarships",
            "health_check": "GET /api/v1/health",
        },
    }
