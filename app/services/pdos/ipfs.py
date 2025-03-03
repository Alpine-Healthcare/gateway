from app.services.pdos.model import AlpineNodeManifest
from app.web.application import logger
from app.settings import settings
import requests
import pickle
import json


ALPINE_MANIFEST = "./alpine_manifest.pkl"

ALPINE_IPNS_ID = settings.ipfs_ipns_id 
ALPINE_NODE_MANIFEST = None

def start_ipfs():
    global ALPINE_NODE_MANIFEST 

    try:
        logger.info(f"Connecting to IPFS at {settings.ipfs_url}")
        ALPINE_NODE_MANIFEST = get_alpine_manifest()
        
        if not ALPINE_NODE_MANIFEST:
            create_new_alpine_manifest()
            logger.info(f"Successfully created new Alpine Node Manifest")
            return

        logger.info(f"Retrieved Alpine Node Manifest: {ALPINE_NODE_MANIFEST}")
            
    except Exception as e:
        logger.error(f"Failed to connect to IPFS : {e}")

def get_alpine_manifest() -> AlpineNodeManifest:
    #reload object from file
    logger.info(f"Getting Alpine Node Manifest from local")
    try:
        file2 = open(rf"{ALPINE_MANIFEST}", 'rb')
        new_d = pickle.load(file2)
        file2.close()
        return AlpineNodeManifest(**json.loads(new_d))
    except Exception as e:
        logger.error(f"Failed to get Alpine Node Manifest: {e}")
        return None


def create_new_alpine_manifest():
    global ALPINE_NODE_MANIFEST

    try:
        alpine_manifest = AlpineNodeManifest()
        logger.info(f"Creating new Alpine Manifest: {alpine_manifest}")
        alpine_manifest_json = alpine_manifest.json()
        afile = open(rf"{ALPINE_MANIFEST}", 'wb')
        pickle.dump(alpine_manifest_json, afile)
        afile.close()
        ALPINE_NODE_MANIFEST = alpine_manifest
    except Exception as e:
        logger.error(f"Failed to create new Alpine Manifest: {e}")


def set_new_alpine_manifest(alpine_manifest: AlpineNodeManifest):
    global ALPINE_NODE_MANIFEST

    try:
        alpine_manifest_json = alpine_manifest.json()
        afile = open(rf"{ALPINE_MANIFEST}", 'wb')
        pickle.dump(alpine_manifest_json, afile)
        afile.close()
        ALPINE_NODE_MANIFEST = alpine_manifest
    except Exception as e:
        logger.error(f"Failed to create new Alpine Manifest: {e}")


def update_alpine_node_manifest(new_alpine_node: AlpineNodeManifest):
    global ALPINE_NODE_MANIFEST 

    set_new_alpine_manifest(new_alpine_node)
    ALPINE_NODE_MANIFEST = new_alpine_node


def add(node_json: str):
    bytes = str.encode(node_json)
    url = f"{settings.ipfs_url}/api/v0/add"
    response = requests.post(url, files={"file": bytes})

    if response.status_code != 200:
        logger.error(f"Failed getting alpine node {response.status_code}")
        raise Exception("Failed to add node to IPFS")

    parsed_response = response.json()
    return parsed_response["Hash"]


def add_bytes(blob: bytes):
    url = f"{settings.ipfs_url}/api/v0/add"
    response = requests.post(url, files={"file": blob})

    if response.status_code != 200:
        logger.error(f"Failed getting alpine node {response.status_code}")
        raise Exception("Failed to add node to IPFS")

    parsed_response = response.json()
    return parsed_response["Hash"]

def get_bytes(hash_id: str):
    url = f"{settings.ipfs_url}/api/v0/cat?arg=/ipfs/{hash_id}"
    response = requests.post(url, stream=True)
    response.raise_for_status()

    # Read chunks and accumulate into a single bytes object
    data = b""
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            data += chunk
    return data

def get(hash_id: str, return_raw: bool = False):
    url = f"{settings.ipfs_url}/api/v0/cat?arg=/ipfs/{hash_id}"
    response = requests.post(url)
    if return_raw:
        return response.text

    return response.json() 