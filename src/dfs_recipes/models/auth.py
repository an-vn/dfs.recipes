from typing import Optional, Literal, List
from pydantic import BaseModel
from webauthn.helpers.structs import (
    AuthenticatorAttachment,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    UserVerificationRequirement,
    AuthenticatorTransport,
)


class AuthenticatorAttestationResponseWrapper(BaseModel):
    clientDataJSON: bytes
    attestationObject: bytes
    transports: Optional[List[AuthenticatorTransport]] = None


class RegistrationCredentialWrapper(BaseModel):
    id: str
    rawId: bytes
    response: AuthenticatorAttestationResponseWrapper
    authenticatorAttachment: Optional[AuthenticatorAttachment] = None
    type: Literal[PublicKeyCredentialType.PUBLIC_KEY] = PublicKeyCredentialType.PUBLIC_KEY


class AuthenticatorAssertionResponseWrapper(BaseModel):
    clientDataJSON: bytes
    authenticatorData: bytes
    signature: bytes
    userHandle: Optional[bytes] = None


class AuthenticationCredentialWrapper(BaseModel):
    id: str
    rawId: bytes
    response: AuthenticatorAssertionResponseWrapper
    authenticatorAttachment: Optional[AuthenticatorAttachment] = None
    type: Literal[PublicKeyCredentialType.PUBLIC_KEY] = PublicKeyCredentialType.PUBLIC_KEY


class PublicKeyCredentialRequestOptionsWrapper(BaseModel):
    challenge: bytes
    timeout: Optional[int] = None
    rpId: Optional[str] = None
    allowCredentials: Optional[List[PublicKeyCredentialDescriptor]] = None
    userVerification: Optional[UserVerificationRequirement] = (
        UserVerificationRequirement.PREFERRED
    )
