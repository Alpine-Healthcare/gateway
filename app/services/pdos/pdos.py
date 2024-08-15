from datetime import datetime
import json
from app.services.pdos.model import Credential, Edge, N_AccessPackage, N_UserAccount, NetworkMapper, PDFSNode 
from app.services.pdos import ipfs
from app.web.application import logger
from base64 import urlsafe_b64encode


def bytes_to_base64url(val: bytes) -> str:
    """
    Base64URL-encode the provided bytes
    """
    return urlsafe_b64encode(val).decode("utf-8").rstrip("=")

'''
User Registration Util Functions
'''
registering_user_map = {}
validating_user_map = {}

def store_potential_user_and_challenge(
    user_id: str,
    username: str,
    challenge: str
):
    new_user = N_UserAccount(
        id=user_id,
        username=username,
        credentials=[],
    )

    registering_user_map[username] = {
        "user": new_user,
        "challenge": challenge
    }


def get_registering_user_challenge(user_id) -> N_UserAccount:
    return registering_user_map[user_id].get("user"), registering_user_map[user_id].get("challenge")     


def store_user_challenge(
    verification_id: str,
    challenge: str
):
    validating_user_map[verification_id] = challenge


def get_user_challenge(
    verification_id: str,
):
    return validating_user_map[verification_id]


def get_user_by_credential_id(
    credential_id: str
):
    if credential_id in ipfs.ALPINE_NODE_MANIFEST.users:
        user_info = ipfs.ALPINE_NODE_MANIFEST.users[credential_id]
        user_node = get_node_from_pdfs(user_info["hash_id"]) 
        return user_node
    else:
        raise RuntimeError(f"User not found {credential_id}")


def get_access_package_in_json_format(
    user: N_UserAccount
) -> str:
    #return get_node_from_pdfs(user.edges["e_out_access_package"].child_hash_id, "N_AccessPackage").json()
    ret = '{ "hashId":' + user.hash_id + '}'
    return user.hash_id 


'''
Higher Level Operations
'''
def add_user_to_network(
    user_id: str,
    credential: Credential,
) -> N_UserAccount:

    new_user = registering_user_map[user_id].get("user")
    new_user.credentials.append(credential)
    user_credential_id = credential.id

    new_access_package = N_AccessPackage(key="default")
    access_package = add_node_to_pdfs(new_access_package)

    access_package_edge= Edge(
        child_hash_id=access_package.hash_id,
        type="N_AccessPackage"
    )

    new_user.edges["e_out_AccessPackage"] = access_package_edge

    user = add_node_to_pdfs(new_user)
    logger.info(f"Added user to network: {user_id}")

    alpine = ipfs.ALPINE_NODE_MANIFEST 
    updated_alpine = alpine.copy()

    updated_alpine.users[user_credential_id] = {
        "hash_id": user.hash_id,
        "timestamp": datetime.now().timestamp()
    }

    ipfs.update_alpine_node_manifest(updated_alpine)
    return user


'''
Core Operations
'''

def add_node_to_pdfs(node: PDFSNode) -> PDFSNode:
    node_json = json.loads(node.json())
    node_json.pop("hash_id ", None)

    hash = ipfs.add(json.dumps(node_json))

    node.hash_id = hash
    logger.info(f"Successfully added node to IPFS: {hash} of type {node.type}")
    return node


def get_node_from_pdfs(hash_id: str):
    from app.web.api.routes.pdos import get_core_node_type

    node = ipfs.get(hash_id)
    node["hash_id"] = hash_id
    try:
        core_type = get_core_node_type(node["type"])
        return NetworkMapper.node[core_type](**node)
    except Exception as e:
        print("node: ", node)
        print("exception:", e)
        raise Exception("Failed")
