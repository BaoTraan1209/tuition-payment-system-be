from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Services.notification_service import (
    list_notifications, mark_notification_read, send_tuition_reminder
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me")
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return {"success": True, "data": list_notifications(db, int(current_user.payer_id))}


@router.patch("/{notification_id}/read")
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        updated = mark_notification_read(db, int(current_user.payer_id), notification_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Notification not found.")
        return {"success": True, "message": "Notification marked as read."}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/tuition/{tuition_id}/email-reminder")
def tuition_email_reminder(
    tuition_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        result = send_tuition_reminder(db, int(current_user.payer_id), tuition_id)
        return {"success": True, "message": "Tuition reminder email sent.", "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
