"""AdmitAI Scholarship Finder - Smart UK scholarship matching system"""

from .matcher import ScholarshipMatcher, find_best_scholarships
from .api import app, StudentProfile, ScholarshipFinderResponse

__version__ = "1.0.0"
__all__ = [
    "ScholarshipMatcher",
    "find_best_scholarships",
    "app",
    "StudentProfile",
    "ScholarshipFinderResponse",
]
