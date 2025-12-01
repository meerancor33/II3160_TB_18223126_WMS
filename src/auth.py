from datetime import datetime, timedelta
from typing import Optional, Set

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_db, UserModel

# ==========================
# JWT CONFIGURATION
# ==========================
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# TOKEN BLACKLIST (logout)
TOKEN_BLACKLIST: Set[str] = set()


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    full_name: Optional[str]
    role: str
    disabled: Optional[bool]


class UserInDB(User):
    hashed_password: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_user(db: Session, username: str) -> Optional[UserInDB]:
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None
    return UserInDB(
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        disabled=user.disabled,
        hashed_password=user.hashed_password,
    )


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expire})
    encoded = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    if token in TOKEN_BLACKLIST:
        raise HTTPException(status_code=401, detail="Logged out token")

    credentials_error = HTTPException(
        status_code=401,
        detail="Invalid authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = get_user(db, username)
    if not user or user.disabled:
        raise credentials_error

    return User(
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        disabled=user.disabled,
    )


def require_role(role: str):
    def wrapper(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return wrapper


def logout_token(token: str):
    TOKEN_BLACKLIST.add(token)
