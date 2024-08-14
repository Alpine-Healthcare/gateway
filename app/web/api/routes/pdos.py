import json
from typing import List, Optional
from fastapi import APIRouter
from app.services.pdos.pdos import get_node_from_pdfs, add_node_to_pdfs
from app.services.pdos.model import Edge, NetworkMapper, PDFSNode
from pydantic import BaseModel
from app.services.pdos import ipfs
from typing import Generic, TypeVar
from pydantic.generics import GenericModel
import threading


router = APIRouter()

'''
PDOS Mutex Routes

TBD

'''

user_mutexes = {}

@router.get("/pdos/mutex")
def get_pdos_mutex(
    credential_id: str,
) -> bool:
    if credential_id in user_mutexes:
        mutex = user_mutexes[credential_id]
        if mutex.locked():
            return False
        else:
            mutex.acquire()
            return True
    else:
        user_mutexes[credential_id] = threading.Lock()
        user_mutexes[credential_id].acquire()
        return True


@router.post("/pdos/release_mutex")
def release_pdos_mutex(
    credential_id: str,
) -> bool:
    if credential_id not in user_mutexes:
        return False
    else:
        mutex = user_mutexes[credential_id]
        if mutex.locked():
            mutex.release()
            return True
        else:
            return False


'''
PDOS Tree Routes

TBD


'''

@router.get("/pdos")
def get_node_from_pdos(
    hash: str,
):
    assert hash is not None, "No hash id passed"
    return get_node_from_pdfs(hash).json()

class NewPDFSNodeRequest(BaseModel):
    new_node_type: Optional[str] = None
    new_node_data: str 
    new_node_instance: Optional[str] = None

    tree_path: Optional[List[str]] = []

# Define a type variable
T = TypeVar('T')

# Generic model
class NewPDFSNodeResponse(GenericModel, Generic[T]):
    new_node: T
    new_tree_path: List[str]
    old_tree_path: List[str]


def get_core_node_type(node_type: str):
    node_split = node_type.split("_") 

    if (len(node_split) >= 3):
        return node_split[0] + "_" + node_split[1] + "_I"
    else:
        return node_split[0] + "_" + node_split[1]

def get_node_name(node_type: str):
    node_split = node_type.split("_") 
    if (len(node_split) >= 3):
        return node_split[1] + "_" + node_split[2]
    else:
        return node_split[1]

def get_node_instance_type(node_type: str):
    node_split = node_type.split("_") 
    if (len(node_split) == 3):
        return node_split[2]
    else:
        return None


def is_instance_node(node_type: str):
    node_split = node_type.split("_") 
    return len(node_split) == 3

'''
Adds node to PDOS

This entails adding the node to the IPFS network and updating the parent nodes,
generating a new tree root.
'''
@router.post("/pdos")
def add_node_to_pdos(
    new_pdfs_node: NewPDFSNodeRequest
) -> NewPDFSNodeResponse:
    core_node_type = get_core_node_type(new_pdfs_node.new_node_type) 
    new_node_data_json = json.loads(new_pdfs_node.new_node_data)
    data_model = NetworkMapper.node[core_node_type](**new_node_data_json)

    if is_instance_node(new_pdfs_node.new_node_type):
        data_model.init_instance(get_node_instance_type(new_pdfs_node.new_node_type)) 

    newly_added_pdfs_node = add_node_to_pdfs(
        data_model,
    )

    new_tree_path = []
    new_tree_path.append(newly_added_pdfs_node.hash_id)

    def update_parent_nodes(parent_node_hash_list: List[str], new_node: PDFSNode) -> PDFSNode:

        next_parent_hash = parent_node_hash_list.pop()

        parent_node = get_node_from_pdfs(next_parent_hash)
        node_name = get_node_name(new_node.type)

        relation_to_child = 'e_out_' + node_name

        updated_parent_node = parent_node.copy()
        updated_parent_node.edges[relation_to_child] = Edge(
            type=new_node.type,
            child_hash_id=new_node.hash_id
        ) 

        new_parent_node = add_node_to_pdfs(
            updated_parent_node,
        )

        new_tree_path.append(new_parent_node.hash_id)
        if parent_node.is_root:
            if (parent_node.type == "N_UserAccount"):
                alpine = ipfs.ALPINE_NODE_MANIFEST 
                updated_alpine = alpine.copy()

                if (parent_node.hash_id in updated_alpine.users):
                    del updated_alpine.users[parent_node.hash_id]

                updated_alpine.users[new_parent_node.hash_id] = True
                ipfs.update_alpine_node_manifest(updated_alpine)
        else:
            update_parent_nodes(parent_node_hash_list, new_parent_node)


    if len(new_pdfs_node.tree_path) > 0:
        update_parent_nodes(new_pdfs_node.tree_path, newly_added_pdfs_node)

    return NewPDFSNodeResponse[NetworkMapper.node[core_node_type]](
        new_node=newly_added_pdfs_node,
        new_tree_path = list(reversed(new_tree_path)),
        old_tree_path = new_pdfs_node.tree_path
    )
