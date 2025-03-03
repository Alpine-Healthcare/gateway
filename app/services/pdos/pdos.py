import json
from app.services.pdos.model import N_UserAccount, NetworkMapper, PDOSNode 
from app.services.pdos import ipfs
from app.web.application import logger
from base64 import urlsafe_b64encode
from app.settings import settings
from web3 import Web3
import web3


from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import SignAndSendRawMiddlewareBuilder

w3 = Web3(Web3.HTTPProvider(settings.infura_url))
account: LocalAccount = Account.from_key(settings.marigold_private_key)
w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(account), layer=0)

import logging

logger = logging.getLogger("Gateway")


def bytes_to_base64url(val: bytes) -> str:
    """
    Base64URL-encode the provided bytes
    """
    return urlsafe_b64encode(val).decode("utf-8").rstrip("=")


'''
User Init Operations
'''

def send_user_test_tokens(public_key: str):
    amount_in_wei = Web3.to_wei(0.001, 'ether')
    tx_hash = w3.eth.send_transaction({
        "from": account.address,
        "value": amount_in_wei,
        "to": public_key
    })
    # Wait for the transaction to be mined
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    logger.info(f"Successfully sent test tokens to {public_key}. Transaction confirmed in block {tx_receipt.blockNumber}")
    return tx_receipt


def add_user_to_network(
    user_id: str,
) -> N_UserAccount:

    new_user = N_UserAccount(
        hash_id=user_id
    )

    user = add_node_to_pdfs(new_user)
    logger.info(f"Added user to network: {user_id}")


    return user


'''
Core Operations
'''

def add_node_to_pdfs(node: PDOSNode) -> PDOSNode:
    print("node: ", node)
    node_json = json.loads(node.json())
    node_json.pop("hash_id ", None)

    del node_json["hash_id"]

    hash = ipfs.add(json.dumps(node_json))

    node.hash_id = hash
    logger.info(f"Successfully added node to PDOS: {hash} of type {node.type}")
    return node


def get_node_from_pdfs(hash_id: str, return_raw: bool = False):
    from app.web.api.routes.pdos import get_core_node_type

    node = ipfs.get(hash_id, return_raw)

    if (return_raw):
        return node

    node["hash_id"] = hash_id
    try:
        core_type = get_core_node_type(node["type"])
        return NetworkMapper.node[core_type](**node)
    except Exception as e:
        print("node: ", node)
        print("exception:", e)
        raise Exception("Failed")
