from sqlalchemy.orm import Session
from app.security import hash_password , verify_password
from app.user_repository import create_user, get_user_by_email


def register_user(
    db: Session,
    email: str,
    full_name: str,
    password: str,
):
    existing_user = get_user_by_email(db, email)

    if existing_user:
        raise ValueError("Email already registered")

    hashed_password = hash_password(password)

    return create_user(
        db=db,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
    )



from app.security import verify_password


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user