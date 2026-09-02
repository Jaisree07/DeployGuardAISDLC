from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db

from backend.analysis.regression_detector import (
    detect_all_patterns,
    get_regression_history,
)

from backend.ai.ai_service import AIService


router = APIRouter()


# =====================================================
# AI Regression Explanation
# =====================================================

@router.get("/regressions/explain")
def explain_regressions(
    environment: str,
    db: Session = Depends(get_db)
):
    patterns = detect_all_patterns(
        db,
        environment
    )

    if not patterns:
        return {
            "environment": environment,
            "patterns_found": 0,
            "results": []
        }

    results = AIService.explain_all(
        patterns
    )

    return {
        "environment": environment,
        "patterns_found": len(results),
        "results": results,
    }


# =====================================================
# Regression History
# =====================================================

@router.get("/regressions/history")
def regression_history(
    environment: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    history = get_regression_history(
        db=db,
        environment=environment,
        limit=limit
    )

    return {
        "environment": environment,
        "total_records": len(history),
        "history": history
    }


# =====================================================
# Current Regression Patterns
# =====================================================

@router.get("/regressions")
def current_regressions(
    environment: str,
    db: Session = Depends(get_db)
):
    patterns = detect_all_patterns(
        db,
        environment
    )

    return {
        "environment": environment,
        "patterns_found": len(patterns),
        "results": patterns
    }