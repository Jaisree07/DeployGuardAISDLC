from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.analysis.regression_detector import detect_all_patterns
from backend.ai.ai_service import AIService

router = APIRouter()


@router.get("/regressions/explain")
def explain_regressions(environment: str, db: Session = Depends(get_db)):
    patterns = detect_all_patterns(db, environment)
    if not patterns:
        return {"environment": environment, "patterns_found": 0, "results": []}

    results = AIService.explain_all(patterns)
    return {
        "environment": environment,
        "patterns_found": len(results),
        "results": results,
    }
