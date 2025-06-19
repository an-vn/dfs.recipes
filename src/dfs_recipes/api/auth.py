import pickle
from pathlib import Path
from pprint import pprint
import webauthn
import json
import uuid
from fastapi import APIRouter, HTTPException, Request, Response
from dfs_recipes.models.auth import AuthenticationCredentialWrapper, RegistrationCredentialWrapper
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticationCredential,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    PublicKeyCredentialHint,
    RegistrationCredential,
    AuthenticatorAttestationResponse,
    AuthenticatorAssertionResponse,
)

webauthn_db = {}

_pickle_file = Path(__file__).parent.parent / 'database' / 'webauthn_db.pkl'

if not _pickle_file.exists():
    with _pickle_file.open('wb') as file:
        pickle.dump({}, file)

with _pickle_file.open(mode='rb') as file:
    webauthn_db = pickle.load(file)

router = APIRouter()


@router.get('/session')
async def session(request: Request):
    if 'thread_id' not in request.session:
        request.session['thread_id'] = str(uuid.uuid4())

    return {
        'thread_id': request.session['thread_id']
    }


@router.get('/login')
async def login(request: Request):
    pprint(request.session)
    if 'webauthn_user' not in request.session:
        raise HTTPException(
            status_code=401,
            detail='No user registered for device'
        )
    return {
        'username': request.session.get('webauthn_user', ''),
    }


@router.get('/register/{username}')
async def register_get(request: Request, res: Response, username: str):
    opts = webauthn.generate_registration_options(
        rp_id='localhost',
        rp_name='DFS Recipes',
        user_name=username,
        user_id=username.encode('utf-8'),
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            resident_key=ResidentKeyRequirement.DISCOURAGED,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        hints=[PublicKeyCredentialHint.CLIENT_DEVICE],
    )

    public_key_options = json.loads(webauthn.options_to_json(opts))
    request.session['webauthn_register_challenge'] = public_key_options['challenge']

    return public_key_options


@router.post('/register/{username}')
async def register_post(request: Request, username: str, credential: RegistrationCredentialWrapper):
    registration_credential = RegistrationCredential(
        id=credential.id,
        raw_id=webauthn.base64url_to_bytes(credential.rawId.decode('utf-8')),
        response=AuthenticatorAttestationResponse(
            client_data_json=webauthn.base64url_to_bytes(credential.response.clientDataJSON.decode('utf-8')),
            attestation_object=webauthn.base64url_to_bytes(credential.response.attestationObject.decode('utf-8')),
            transports=credential.response.transports,
        ),
        authenticator_attachment=credential.authenticatorAttachment,
        type=PublicKeyCredentialType.PUBLIC_KEY,
    )

    expected_challenge = webauthn.base64url_to_bytes(request.session['webauthn_register_challenge'])

    registration = webauthn.verify_registration_response(
        credential=registration_credential,
        expected_challenge=expected_challenge,
        expected_rp_id='localhost',
        expected_origin='https://localhost:8080',
    )

    webauthn_db[username] = {
        'public_key': registration.credential_public_key,
        'sign_count': registration.sign_count,
        'credential_id': registration.credential_id,
        'challenge': expected_challenge,
    }

    request.session['webauthn_user'] = username

    with _pickle_file.open('wb') as file:
        pickle.dump(webauthn_db, file)

    pprint(webauthn_db)


@router.get('/auth')
async def auth_get(request: Request):
    try:
        username = request.session['webauthn_user']
        user_creds = webauthn_db[username]
    except KeyError:
        raise HTTPException(status_code=404, detail='user not found')

    opts = webauthn.generate_authentication_options(
        rp_id='localhost',
        timeout=50000,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                type=PublicKeyCredentialType.PUBLIC_KEY,
                id=user_creds['credential_id'],
            )
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    public_key_options = json.loads(webauthn.options_to_json(opts))

    pprint(public_key_options)

    request.session['webauthn_auth_challenge'] = public_key_options['challenge']

    return public_key_options


@router.post('/auth')
async def auth_post(request: Request, credential: AuthenticationCredentialWrapper):
    expected_challenge = webauthn.base64url_to_bytes(request.session['webauthn_auth_challenge'])

    try:
        username = request.session['webauthn_user']
        user_creds = webauthn_db[username]
    except KeyError:
        raise HTTPException(status_code=404, detail='user not found')

    auth = webauthn.verify_authentication_response(
        credential=AuthenticationCredential(
            id=credential.id,
            raw_id=webauthn.base64url_to_bytes(credential.rawId.decode('utf-8')),
            response=AuthenticatorAssertionResponse(
                client_data_json=webauthn.base64url_to_bytes(credential.response.clientDataJSON.decode('utf-8')),
                authenticator_data=webauthn.base64url_to_bytes(credential.response.authenticatorData.decode('utf-8')),
                signature=webauthn.base64url_to_bytes(credential.response.signature.decode('utf-8')),
                user_handle=None if credential.response.userHandle is None else webauthn.base64url_to_bytes(
                    credential.response.userHandle.decode('utf-8')),
            ),
            authenticator_attachment=credential.authenticatorAttachment,
            type=PublicKeyCredentialType.PUBLIC_KEY,
        ),
        expected_challenge=expected_challenge,
        expected_rp_id='localhost',
        expected_origin='https://localhost:8080',
        credential_public_key=user_creds['public_key'],
        credential_current_sign_count=user_creds['sign_count'],
        require_user_verification=True
    )
