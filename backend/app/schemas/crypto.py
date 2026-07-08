"""Schemas Pydantic para operaciones criptograficas asimetricas."""
from pydantic import BaseModel


class KeyPair(BaseModel):
    private_key_pem: str
    public_key_pem: str
    algorithm: str = "RSA-2048"


class SignatureResult(BaseModel):
    signature_b64: str
    algorithm: str = "RSA-PSS-SHA256"


class VerifyResult(BaseModel):
    valid: bool
    detail: str
