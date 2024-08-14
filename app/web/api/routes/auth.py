import json
from fastapi import APIRouter
from app.services.pdos.pdos import (
    add_user_to_network,
    bytes_to_base64url,
    get_access_package_in_json_format,
    get_registering_user_challenge,
    get_user_by_credential_id,
    get_user_challenge,
    store_potential_user_and_challenge,
    store_user_challenge
)
from app.services.pdos.model import Credential
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
)
from webauthn.helpers import (
    parse_registration_credential_json, parse_authentication_credential_json,
)
import uuid
from webauthn.helpers.structs import (
    UserVerificationRequirement,
)
from typing import Dict, Any
from app.settings import settings

router = APIRouter()

'''
REGISTRATION
-----------------------------------------

1. Generate registration options
- Creates a user_id and adds to PDFS
- Creates a new user challenge
2. Verify registration response
- User creates a new credential against the challenge
- We verifiy the challenge and create a new credential
- Add the credential to PDFS

-----------------------------------------
'''

@router.post("/auth/register/options")
def register_options():
    user_uuid = uuid.uuid4()
    user_id = str(user_uuid).encode('utf-8')
    username = str(user_uuid)

    complex_registration_options = generate_registration_options(
        rp_id=settings.rp_id,
        rp_name=settings.rp_name,
        user_id=user_id,
        attestation=AttestationConveyancePreference.DIRECT,
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        user_name=username,
        supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_512],
        timeout=12000,
    )
    options_json = options_to_json(complex_registration_options)
    user_challenge_base64 = json.loads(options_json)["challenge"]

    store_potential_user_and_challenge(user_id, username, user_challenge_base64)

    return options_json 


@router.post("/auth/register/verify")
def register_verifcation(
    body: Dict[Any, Any] 
) -> bool:
    user_id = body["id"]
    registration_response = body["registrationResponse"]

    _, challenge = get_registering_user_challenge(user_id)

    challenge_bytes = base64url_to_bytes(challenge)

    verification = verify_registration_response(
        credential=parse_registration_credential_json(registration_response),
        expected_challenge=challenge_bytes,
        expected_rp_id=settings.rp_id,
        expected_origin=settings.origin,
        require_user_verification=True,
    )

    new_credential = Credential(
        id=bytes_to_base64url(verification.credential_id),
        public_key=bytes_to_base64url(verification.credential_public_key),
        sign_count=verification.sign_count,
        transports=body.get("transports", []),
    )

    add_user_to_network(user_id, new_credential)
    return True


'''
AUTHENTICATION
-----------------------------------------

1. User rquests a verification challenge
2. Signs and retrive rawId from passkey
3. Fetch the user credential from PDFS
3. Verify the challenge, the credential_json, and the user credential 

-----------------------------------------
'''

@router.get("/auth/options")
def verification_options(
    verificationId: str
):
    options = generate_authentication_options(
        rp_id=settings.rp_id,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    options_json = options_to_json(options)
    user_challenge_base64 = json.loads(options_json)["challenge"]

    store_user_challenge(verificationId, user_challenge_base64)
    return options_to_json(options)


@router.post("/auth/verify")
def verify(
    body: Dict[Any, Any] 
) -> str:
    verificaiton_id = body["verificationId"]
    authentication_credential_json = body["authenticationCredentialJson"]
    parsed_authentication_credential = parse_authentication_credential_json(authentication_credential_json)

    user = get_user_by_credential_id(authentication_credential_json["id"])
    user_challenge = get_user_challenge(verificaiton_id)
    user_challenge_bytes = base64url_to_bytes(user_challenge)

    assert user != None, "User not found"
    assert user_challenge != None, "User challenge not found"
    assert len(user.credentials) > 0, "User has no credentials"
    assert len(user.credentials) == 1, "User has multiple credentials"

    credential = user.credentials[0]

    verify_authentication_response(
        credential=parsed_authentication_credential,
        expected_challenge=user_challenge_bytes,
        expected_rp_id=settings.rp_id,
        expected_origin=settings.origin,
        require_user_verification=True,
        credential_public_key=base64url_to_bytes(credential.public_key),
        credential_current_sign_count=credential.sign_count,
    )

    return get_access_package_in_json_format(user)

