from fastapi import APIRouter

from backend.features.feature_engineering import FeatureEngineering

router = APIRouter(
    prefix="/features",
    tags=["Feature Engineering"]
)


@router.get("/")
def generate_dataset():

    df = FeatureEngineering.export_dataset()

    return {
        "message": "ML Dataset Generated Successfully",
        "rows": len(df),
        "columns": list(df.columns)
    }


@router.get("/stats")
def dataset_statistics():

    return FeatureEngineering.get_statistics()