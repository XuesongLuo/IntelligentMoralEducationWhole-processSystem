from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.schemas.common import ResponseModel
from app.services.exam_runtime import apply_ai_callback


settings = get_settings()
router = APIRouter(prefix="/exam", tags=["exam"])


@router.post("/ai/callback", response_model=ResponseModel)
def receive_ai_callback(
    payload: dict,
    x_ai_callback_token: str | None = Header(default=None),
):
    if x_ai_callback_token != settings.AI_CALLBACK_TOKEN:
        raise HTTPException(status_code=401, detail="invalid callback token")

    attempt_id = payload.get("attempt_id")
    if not attempt_id:
        raise HTTPException(status_code=400, detail="attempt_id is required")

    db: Session = SessionLocal()
    try:
        report = apply_ai_callback(db, attempt_id=int(attempt_id), payload=payload)
        db.commit()
        return ResponseModel(
            data={
                "attemptId": int(attempt_id),
                "status": report.status,
            }
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc))
    finally:
        db.close()
