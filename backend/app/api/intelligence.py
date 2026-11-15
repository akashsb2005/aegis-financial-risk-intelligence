"""Authenticated read endpoints for persisted model intelligence."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth import require_authenticated_user
from app.core.database import get_db
from app.schemas.auth import AuthenticatedUser

router = APIRouter()


@router.get("/companies/{company_id}/predictions", tags=["model-intelligence"])
def list_company_predictions(
    company_id: Annotated[int, Path(gt=0)],
    prediction_type: Annotated[str | None, Query(pattern="^(ANOMALY|VOLATILITY)$")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    _user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List persisted anomaly and volatility signals for one company."""
    exists = db.execute(
        text("SELECT 1 FROM public.companies WHERE company_id = :company_id"),
        {"company_id": company_id},
    ).scalar_one_or_none()
    if exists is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Company not found.")

    rows = db.execute(
        text(
            """
            SELECT p.prediction_id, p.security_id, s.ticker, s.exchange,
                   p.prediction_type, p.prediction_date, p.target_date,
                   p.predicted_value, p.signal, p.model_name, p.model_version,
                   p.metrics, p.features, p.created_at
            FROM public.model_predictions p
            JOIN public.securities s ON s.security_id = p.security_id
            WHERE s.company_id = :company_id
              AND (:prediction_type IS NULL OR p.prediction_type = :prediction_type)
            ORDER BY p.prediction_date DESC, p.prediction_id DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        {
            "company_id": company_id,
            "prediction_type": prediction_type,
            "limit": limit,
            "offset": offset,
        },
    ).mappings().all()
    return [dict(row) for row in rows]
