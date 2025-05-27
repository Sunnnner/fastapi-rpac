

from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
import jwt
from persist.models.user_model import User


class TokenService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_token(self, user: User):
        payload = {
            "sub": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")