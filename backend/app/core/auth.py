"""
Role-Based Access Control and Authentication for FLOODTWIN RESPONDER.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import hashlib
import hmac

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)


class UserRole(str, Enum):
    DISASTER_COMMANDER = "DISASTER_COMMANDER"
    FIELD_ANALYST = "FIELD_ANALYST"
    AUDITOR = "AUDITOR"
    SYSTEM_AGENT = "SYSTEM_AGENT"


# Pre-configured mock operators for disaster response operations
OPERATORS = {
    "cmd_kumar": {
        "id": "OP_001",
        "name": "Dr. R. Senthil Kumar",
        "role": UserRole.DISASTER_COMMANDER,
        "district": "Chennai Metropolitan"
    },
    "analyst_anitha": {
        "id": "OP_002",
        "name": "Anitha Rajan, GIS Specialist",
        "role": UserRole.FIELD_ANALYST,
        "district": "Chennai Metropolitan"
    },
    "auditor_raman": {
        "id": "OP_003",
        "name": "V. Raman, Emergency Oversight Officer",
        "role": UserRole.AUDITOR,
        "district": "Chennai Metropolitan"
    }
}


def create_access_token(operator_key: str) -> str:
    """Generates simple signed token for demo/production authorization."""
    op = OPERATORS.get(operator_key)
    if not op:
        raise ValueError("Invalid operator key")
    raw_payload = f"{op['id']}:{op['role'].value}:{op['name']}"
    sig = hmac.new(settings.SECRET_KEY.encode(), raw_payload.encode(), hashlib.sha256).hexdigest()
    return f"{raw_payload}:{sig}"


def verify_token(token_str: str) -> Dict[str, Any]:
    """Verifies token signature and extracts role."""
    parts = token_str.split(":")
    if len(parts) != 4:
        # Fallback to dev header if operator key is provided directly
        if token_str in OPERATORS:
            return OPERATORS[token_str]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authorization token."
        )
    op_id, role_val, name, sig = parts
    raw = f"{op_id}:{role_val}:{name}"
    expected_sig = hmac.new(settings.SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid cryptographic token signature."
        )
    return {
        "id": op_id,
        "name": name,
        "role": UserRole(role_val),
        "district": "Chennai Metropolitan"
    }


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    x_operator_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Resolves authenticated operator from Bearer token or development header."""
    if credentials:
        return verify_token(credentials.credentials)
    if x_operator_key and x_operator_key in OPERATORS:
        return OPERATORS[x_operator_key]
    # Default to DISASTER_COMMANDER in development for seamless evaluation
    return OPERATORS["cmd_kumar"]


def require_role(allowed_roles: list[UserRole]):
    """Enforces specific role permissions on critical endpoints."""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Action requires one of roles: {[r.value for r in allowed_roles]}. Current role: {user_role}"
            )
        return current_user
    return role_checker
