"""보안 유틸리티: JWT 토큰 및 비밀번호 해싱."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시 비교."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> tuple[str, int]:
    """JWT 액세스 토큰 생성. (token, expires_in_seconds) 반환."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    expires_in = int(timedelta(hours=settings.JWT_EXPIRE_HOURS).total_seconds())
    return token, expires_in


def decode_access_token(token: str) -> dict | None:
    """JWT 토큰 디코딩. 실패 시 None 반환."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
