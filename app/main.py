from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field

from app.feature_engineering import hashed_feature


class PredictRequest(BaseModel):
    """Request model for prediction endpoint."""
    user_id: str = Field(..., description="Bucket identifier")
    num_buckets: int = Field(
        default=1000,
        ge=1,
        description="Number of buckets for hashing")


class PredictResponse(BaseModel):
    """Response model for prediction endpoint."""
    bucket: int = Field(..., description="Assigned bucket number")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(default="ok", description="Service health status")


class PredictionService:
    """Service layer for prediction logic."""

    @staticmethod
    def compute_bucket(user_id: str, num_buckets: int) -> int:
        """Compute bucket assignment for a user."""
        return hashed_feature(user_id, num_buckets)


# Create routers for better organization
api_router = APIRouter(tags=["api"])
health_router = APIRouter(tags=["health"])


@health_router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


@api_router.post("/predict", response_model=PredictResponse)
def create_predict(request: PredictRequest) -> PredictResponse:
    """Predict bucket assignment for a user."""
    service = PredictionService()
    bucket = service.compute_bucket(request.user_id, request.num_buckets)
    return PredictResponse(bucket=bucket)


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""
    app = FastAPI(
        title="ML Prediction Service",
        description="Service for computing user bucket assignments",
        version="1.0.0"
    )

    # Register routers
    app.include_router(health_router)
    app.include_router(api_router)

    return app


# Create the app instance
app = create_app()
