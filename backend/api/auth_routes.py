"""
Authentication APIs (Section 4.15.2):
    POST /login            Administrator login
    POST /logout           End user session
    POST /change-password  Update administrator password
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.models import get_db, User, SystemLog
from services.auth_service import verify_password, hash_password, create_access_token
from models.schemas import LoginRequest, LoginResponse, ChangePasswordRequest
from api.deps import get_current_admin

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    # Deliberately generic error message for both cases (Section 4.17.1):
    # do not reveal whether the username or the password was incorrect.
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password.",
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    token = create_access_token(subject=user.username)
    db.add(SystemLog(event=f"Administrator '{user.username}' logged in."))
    db.commit()

    return LoginResponse(status="success", access_token=token)


@router.post("/logout")
def logout(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    db.add(SystemLog(event=f"Administrator '{current_admin.username}' logged out."))
    db.commit()
    return {"status": "success", "message": "Logged out successfully."}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.old_password, current_admin.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")

    current_admin.password_hash = hash_password(payload.new_password)
    db.add(SystemLog(event=f"Administrator '{current_admin.username}' changed their password."))
    db.commit()
    return {"status": "success", "message": "Password updated successfully."}
